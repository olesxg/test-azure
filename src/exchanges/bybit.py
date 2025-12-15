import ccxt.async_support as ccxt
from typing import Optional, Dict
from datetime import datetime
from src.exchanges.base import BaseExchange, Ticker, OrderBook


class BybitExchange(BaseExchange):
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret, "bybit")
        self.exchange = ccxt.bybit(
            {"apiKey": api_key, "secret": api_secret, "enableRateLimit": True}
        )

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return Ticker(
                exchange=self.name,
                symbol=symbol,
                bid=ticker["bid"],
                ask=ticker["ask"],
                last=ticker["last"],
                volume=ticker["baseVolume"],
                timestamp=datetime.now(),
            )
        except Exception:
            return None

    async def get_orderbook(self, symbol: str, limit: int = 10) -> Optional[OrderBook]:
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit)
            return OrderBook(
                exchange=self.name,
                symbol=symbol,
                bids=orderbook["bids"][:limit],
                asks=orderbook["asks"][:limit],
                timestamp=datetime.now(),
            )
        except Exception:
            return None

    async def get_balance(self) -> Dict[str, float]:
        try:
            balance = await self.exchange.fetch_balance()
            return {k: v["free"] for k, v in balance.items() if v["free"] > 0}
        except Exception:
            return {}

    async def close(self):
        await self.exchange.close()
