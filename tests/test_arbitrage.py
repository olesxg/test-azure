import pytest
from datetime import datetime
from src.arbitrage.analyzer import ArbitrageAnalyzer, ArbitrageOpportunity
from src.arbitrage.executor import ArbitrageExecutor
from src.exchanges.base import Ticker


@pytest.fixture
def analyzer():
    return ArbitrageAnalyzer(threshold_percent=0.5, max_position_size=10000)


@pytest.fixture
def executor():
    return ArbitrageExecutor(dry_run=True)


@pytest.fixture
def sample_tickers():
    return [
        Ticker("binance", "BTC/USDT", 50000.0, 50010.0, 50005.0, 100.0, datetime.now()),
        Ticker("bybit", "BTC/USDT", 49500.0, 49510.0, 49505.0, 100.0, datetime.now()),
        Ticker("gateio", "BTC/USDT", 50200.0, 50210.0, 50205.0, 100.0, datetime.now()),
    ]


def test_analyzer_finds_opportunities(analyzer, sample_tickers):
    opportunities = analyzer.analyze_opportunities(sample_tickers)
    assert len(opportunities) > 0
    assert all(isinstance(opp, ArbitrageOpportunity) for opp in opportunities)


def test_analyzer_filters_by_threshold(sample_tickers):
    analyzer = ArbitrageAnalyzer(threshold_percent=10.0, max_position_size=10000)
    opportunities = analyzer.analyze_opportunities(sample_tickers)
    assert all(opp.profit_percent >= 10.0 for opp in opportunities)


@pytest.mark.asyncio
async def test_executor_simulates_execution(executor):
    opportunity = ArbitrageOpportunity(
        symbol="BTC/USDT",
        buy_exchange="binance",
        sell_exchange="bybit",
        buy_price=50000.0,
        sell_price=51000.0,
        profit_percent=2.0,
        profit_usd=200.0,
        volume=10.0,
        timestamp=datetime.now(),
    )

    result = await executor.execute_opportunity(opportunity)
    assert result is True
    assert len(executor.executed_trades) == 1


@pytest.mark.asyncio
async def test_executor_statistics(executor):
    opportunity = ArbitrageOpportunity(
        symbol="BTC/USDT",
        buy_exchange="binance",
        sell_exchange="bybit",
        buy_price=50000.0,
        sell_price=51000.0,
        profit_percent=2.0,
        profit_usd=200.0,
        volume=10.0,
        timestamp=datetime.now(),
    )

    await executor.execute_opportunity(opportunity)
    stats = executor.get_statistics()

    assert stats["total_trades"] == 1
    assert stats["total_profit_usd"] == 200.0
    assert stats["avg_profit_percent"] == 2.0
