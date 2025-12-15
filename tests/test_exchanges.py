import pytest
from src.exchanges.binance import BinanceExchange
from src.exchanges.bybit import BybitExchange
from src.exchanges.gateio import GateioExchange
from src.exchanges.kraken import KrakenExchange


def test_exchange_initialization():
    exchanges = [
        BinanceExchange("test_key", "test_secret"),
        BybitExchange("test_key", "test_secret"),
        GateioExchange("test_key", "test_secret"),
        KrakenExchange("test_key", "test_secret"),
    ]

    assert all(exchange.api_key == "test_key" for exchange in exchanges)
    assert all(exchange.api_secret == "test_secret" for exchange in exchanges)


def test_exchange_names():
    assert BinanceExchange("k", "s").name == "binance"
    assert BybitExchange("k", "s").name == "bybit"
    assert GateioExchange("k", "s").name == "gateio"
    assert KrakenExchange("k", "s").name == "kraken"
