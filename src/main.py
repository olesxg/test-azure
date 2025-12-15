import sys
import traceback

print("=== STARTING CRYPTO ARBITRAGE BOT ===", flush=True)
sys.stdout.flush()

try:
    import asyncio
    import logging
    print("Imported asyncio and logging", flush=True)
except Exception as e:
    print(f"FATAL ERROR importing asyncio/logging: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

from datetime import datetime
from typing import List
print("Imported datetime and typing", flush=True)

from src.config import settings

print(f"Loaded config: {settings.environment}", flush=True)

from src.exchanges.binance import BinanceExchange
from src.exchanges.bybit import BybitExchange
from src.exchanges.gateio import GateioExchange
from src.exchanges.kraken import KrakenExchange
from src.exchanges.base import BaseExchange, Ticker

print("Imported exchanges", flush=True)

from src.arbitrage.analyzer import ArbitrageAnalyzer
from src.arbitrage.executor import ArbitrageExecutor

print("Imported arbitrage modules", flush=True)

from src.ai.openai_service import OpenAIAnalyzer

print("Imported AI service", flush=True)

from src.azure.keyvault import KeyVaultManager
from src.azure.storage import StorageManager
print("Imported Azure keyvault and storage", flush=True)

try:
    from src.azure.sql import SQLManager
except ImportError:
    SQLManager = None
    print("SQL Manager not available", flush=True)

from src.azure.datalake import DataLakeManager

print("Imported DataLake manager", flush=True)

from src.monitoring.telemetry import (
    init_telemetry,
    track_event,
    track_metric,
    create_span,
)
from src.monitoring.metrics import MetricsCollector

print("Imported monitoring modules", flush=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
print("Logger initialized", flush=True)


class ArbitrageBot:
    def __init__(self):
        self.exchanges: List[BaseExchange] = []
        self.analyzer = ArbitrageAnalyzer(
            threshold_percent=settings.arbitrage_threshold_percent,
            max_position_size=settings.max_position_size_usd,
        )
        self.executor = ArbitrageExecutor(dry_run=True)
        self.ai_analyzer = None
        self.storage_manager = None
        self.sql_manager = None
        self.datalake_manager = None
        self.metrics_collector = MetricsCollector()
        self.running = False

    async def initialize(self):
        logger.info("Initializing Arbitrage Bot")

        if settings.azure_application_insights_connection_string:
            init_telemetry(settings.azure_application_insights_connection_string)
            track_event("bot_initialization_started")

        await self._initialize_azure_services()
        await self._initialize_exchanges()
        await self._initialize_ai()

        track_event("bot_initialization_completed")
        logger.info("Arbitrage Bot initialized successfully")

    async def _initialize_azure_services(self):
        if settings.azure_storage_connection_string:
            self.storage_manager = StorageManager(
                settings.azure_storage_connection_string
            )
            await self.storage_manager.init_storage()
            logger.info("Azure Storage initialized")

        if settings.azure_sql_connection_string and SQLManager:
            try:
                self.sql_manager = SQLManager(settings.azure_sql_connection_string)
                await self.sql_manager.init_database()
                logger.info("Azure SQL initialized")
            except ImportError:
                logger.warning("SQL Manager not available (pyodbc not installed)")

        if settings.azure_datalake_account_name:
            self.datalake_manager = DataLakeManager(
                settings.azure_datalake_account_name
            )
            await self.datalake_manager.init_filesystem()
            logger.info("Azure Data Lake initialized")

    async def _initialize_exchanges(self):
        if settings.azure_key_vault_url:
            kv_manager = KeyVaultManager(settings.azure_key_vault_url)

            for exchange_name in ["binance", "bybit", "gateio", "kraken"]:
                creds = await kv_manager.get_exchange_credentials(exchange_name)

                if creds.get("api_key"):
                    exchange = self._create_exchange(
                        exchange_name, creds["api_key"], creds["api_secret"]
                    )
                    if exchange:
                        self.exchanges.append(exchange)
                        logger.info(f"Initialized {exchange_name} exchange")
        else:
            logger.warning("No Key Vault configured, using demo mode")

    def _create_exchange(
        self, name: str, api_key: str, api_secret: str
    ) -> BaseExchange:
        exchange_map = {
            "binance": BinanceExchange,
            "bybit": BybitExchange,
            "gateio": GateioExchange,
            "kraken": KrakenExchange,
        }

        exchange_class = exchange_map.get(name)
        if exchange_class:
            return exchange_class(api_key, api_secret)
        return None

    async def _initialize_ai(self):
        api_key = settings.openai_api_key

        if not api_key and settings.azure_key_vault_url:
            kv_manager = KeyVaultManager(settings.azure_key_vault_url)
            api_key = await kv_manager.get_openai_key()

        if api_key:
            self.ai_analyzer = OpenAIAnalyzer(api_key)
            logger.info("OpenAI Analyzer initialized")

    async def fetch_market_data(self) -> List[Ticker]:
        tasks = []
        for exchange in self.exchanges:
            for symbol in settings.trading_pairs:
                tasks.append(self._fetch_ticker(exchange, symbol))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        tickers = [r for r in results if isinstance(r, Ticker)]

        return tickers

    async def _fetch_ticker(self, exchange: BaseExchange, symbol: str) -> Ticker:
        try:
            ticker = await exchange.get_ticker(symbol)
            success = ticker is not None
            self.metrics_collector.record_ticker_fetch(exchange.name, symbol, success)

            if success:
                track_metric(
                    "ticker_price",
                    ticker.last,
                    {"exchange": exchange.name, "symbol": symbol},
                )

            return ticker
        except Exception as e:
            self.metrics_collector.record_ticker_fetch(exchange.name, symbol, False)
            logger.error(f"Error fetching {symbol} from {exchange.name}: {e}")
            return None

    async def analyze_and_execute(self, tickers: List[Ticker]):
        with create_span("analyze_opportunities"):
            opportunities = self.analyzer.analyze_opportunities(tickers)

        if not opportunities:
            logger.info("No arbitrage opportunities found")
            return

        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        track_metric("opportunities_found", len(opportunities))

        for opp in opportunities[:3]:
            logger.info(
                f"  {opp.symbol}: {opp.buy_exchange} -> {opp.sell_exchange}, "
                f"Profit: {opp.profit_percent:.2f}% (${opp.profit_usd:.2f})"
            )

        await self._save_opportunities(opportunities)

        if self.ai_analyzer and opportunities:
            with create_span("ai_analysis"):
                ai_result = await self.ai_analyzer.analyze_opportunities(
                    opportunities[:5]
                )
                logger.info(f"AI Recommendation: {ai_result['recommendation']}")
                logger.info(f"AI Analysis: {ai_result['analysis'][:200]}...")

        if opportunities and self.executor:
            best_opportunity = opportunities[0]
            with create_span("execute_trade"):
                executed = await self.executor.execute_opportunity(best_opportunity)
                if executed:
                    logger.info(f"Executed opportunity: {best_opportunity.symbol}")

    async def _save_opportunities(self, opportunities):
        opportunity_dicts = [
            {
                "symbol": o.symbol,
                "buy_exchange": o.buy_exchange,
                "sell_exchange": o.sell_exchange,
                "buy_price": o.buy_price,
                "sell_price": o.sell_price,
                "profit_percent": o.profit_percent,
                "profit_usd": o.profit_usd,
                "volume": o.volume,
                "timestamp": o.timestamp,
            }
            for o in opportunities
        ]

        if self.storage_manager:
            await self.storage_manager.save_opportunities_to_blob(
                opportunity_dicts, datetime.now()
            )

            for opp_dict in opportunity_dicts[:10]:
                await self.storage_manager.save_opportunity_to_table(opp_dict)

        if self.sql_manager:
            for opp_dict in opportunity_dicts[:10]:
                await self.sql_manager.save_opportunity(opp_dict)

        if self.datalake_manager:
            await self.datalake_manager.upload_arbitrage_results(
                {"opportunities": opportunity_dicts, "timestamp": datetime.now()}
            )

    async def run(self):
        self.running = True
        logger.info("Starting arbitrage bot main loop")
        track_event("bot_started")

        iteration = 0
        while self.running:
            try:
                iteration += 1
                logger.info(f"Iteration {iteration} started")

                tickers = await self.fetch_market_data()
                logger.info(f"Fetched {len(tickers)} tickers")

                if tickers:
                    await self.analyze_and_execute(tickers)

                stats = self.metrics_collector.get_summary()
                logger.info(f"Bot statistics: {stats}")

                await asyncio.sleep(settings.data_collection_interval_seconds)

            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                track_event("bot_error", {"error": str(e)})
                await asyncio.sleep(5)

        await self.shutdown()

    async def shutdown(self):
        logger.info("Shutting down Arbitrage Bot")
        track_event("bot_shutdown")

        for exchange in self.exchanges:
            await exchange.close()

        final_stats = self.executor.get_statistics()
        logger.info(f"Final statistics: {final_stats}")

        logger.info("Arbitrage Bot stopped")


async def main():
    bot = ArbitrageBot()
    await bot.initialize()
    await bot.run()


if __name__ == "__main__":
    try:
        print("=== RUNNING MAIN FUNCTION ===", flush=True)
        asyncio.run(main())
    except Exception as e:
        print(f"\n\nFATAL ERROR in main: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
