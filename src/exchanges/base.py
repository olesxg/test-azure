from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderBook:
    exchange: str
    symbol: str
    bids: List[tuple]
    asks: List[tuple]
    timestamp: datetime


@dataclass
class Ticker:
    exchange: str
    symbol: str
    bid: float
    ask: float
    last: float
    volume: float
    timestamp: datetime


class BaseExchange(ABC):
    def __init__(self, api_key: str, api_secret: str, name: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.name = name

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        pass

    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 10) -> Optional[OrderBook]:
        pass

    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        pass

    @abstractmethod
    async def close(self):
        pass
