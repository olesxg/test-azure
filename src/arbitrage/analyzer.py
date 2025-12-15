from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from src.exchanges.base import Ticker


@dataclass
class ArbitrageOpportunity:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit_percent: float
    profit_usd: float
    volume: float
    timestamp: datetime


class ArbitrageAnalyzer:
    def __init__(
        self, threshold_percent: float = 0.5, max_position_size: float = 10000
    ):
        self.threshold_percent = threshold_percent
        self.max_position_size = max_position_size

    def analyze_opportunities(
        self, tickers: List[Ticker]
    ) -> List[ArbitrageOpportunity]:
        opportunities = []
        grouped = self._group_by_symbol(tickers)

        for symbol, symbol_tickers in grouped.items():
            if len(symbol_tickers) < 2:
                continue

            opps = self._find_opportunities(symbol, symbol_tickers)
            opportunities.extend(opps)

        return sorted(opportunities, key=lambda x: x.profit_percent, reverse=True)

    def _group_by_symbol(self, tickers: List[Ticker]) -> Dict[str, List[Ticker]]:
        grouped = {}
        for ticker in tickers:
            if ticker.symbol not in grouped:
                grouped[ticker.symbol] = []
            grouped[ticker.symbol].append(ticker)
        return grouped

    def _find_opportunities(
        self, symbol: str, tickers: List[Ticker]
    ) -> List[ArbitrageOpportunity]:
        opportunities = []

        for i in range(len(tickers)):
            for j in range(i + 1, len(tickers)):
                ticker1, ticker2 = tickers[i], tickers[j]

                opp1 = self._calculate_opportunity(ticker1, ticker2, symbol)
                if opp1:
                    opportunities.append(opp1)

                opp2 = self._calculate_opportunity(ticker2, ticker1, symbol)
                if opp2:
                    opportunities.append(opp2)

        return opportunities

    def _calculate_opportunity(
        self, buy_ticker: Ticker, sell_ticker: Ticker, symbol: str
    ) -> Optional[ArbitrageOpportunity]:
        buy_price = buy_ticker.ask
        sell_price = sell_ticker.bid

        if buy_price <= 0 or sell_price <= 0:
            return None

        profit_percent = ((sell_price - buy_price) / buy_price) * 100

        if profit_percent < self.threshold_percent:
            return None

        position_size = min(self.max_position_size, buy_ticker.volume * buy_price)
        profit_usd = position_size * (profit_percent / 100)

        return ArbitrageOpportunity(
            symbol=symbol,
            buy_exchange=buy_ticker.exchange,
            sell_exchange=sell_ticker.exchange,
            buy_price=buy_price,
            sell_price=sell_price,
            profit_percent=profit_percent,
            profit_usd=profit_usd,
            volume=position_size / buy_price,
            timestamp=datetime.now(),
        )
