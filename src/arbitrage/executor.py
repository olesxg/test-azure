import asyncio
from typing import List
from src.arbitrage.analyzer import ArbitrageOpportunity
from src.monitoring.telemetry import track_event, track_metric


class ArbitrageExecutor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.executed_trades = []

    async def execute_opportunity(self, opportunity: ArbitrageOpportunity) -> bool:
        if self.dry_run:
            return await self._simulate_execution(opportunity)
        else:
            return await self._real_execution(opportunity)

    async def _simulate_execution(self, opportunity: ArbitrageOpportunity) -> bool:
        await asyncio.sleep(0.1)

        track_event(
            "arbitrage_opportunity_simulated",
            {
                "symbol": opportunity.symbol,
                "buy_exchange": opportunity.buy_exchange,
                "sell_exchange": opportunity.sell_exchange,
                "profit_percent": opportunity.profit_percent,
                "profit_usd": opportunity.profit_usd,
            },
        )

        track_metric("arbitrage_profit_percent", opportunity.profit_percent)
        track_metric("arbitrage_profit_usd", opportunity.profit_usd)

        self.executed_trades.append(opportunity)
        return True

    async def _real_execution(self, opportunity: ArbitrageOpportunity) -> bool:
        return False

    def get_statistics(self) -> dict:
        if not self.executed_trades:
            return {
                "total_trades": 0,
                "total_profit_usd": 0.0,
                "avg_profit_percent": 0.0,
                "best_opportunity": None,
            }

        total_profit = sum(t.profit_usd for t in self.executed_trades)
        avg_profit_percent = sum(t.profit_percent for t in self.executed_trades) / len(
            self.executed_trades
        )
        best_opp = max(self.executed_trades, key=lambda x: x.profit_percent)

        return {
            "total_trades": len(self.executed_trades),
            "total_profit_usd": total_profit,
            "avg_profit_percent": avg_profit_percent,
            "best_opportunity": {
                "symbol": best_opp.symbol,
                "profit_percent": best_opp.profit_percent,
                "profit_usd": best_opp.profit_usd,
            },
        }
