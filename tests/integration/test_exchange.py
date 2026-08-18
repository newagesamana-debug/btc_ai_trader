from src.data.exchange import ExchangeClient


def test_binance_futures_connection():
    exchange = ExchangeClient("binanceusdm")

    try:
        markets = exchange.load_markets()

        assert markets
        assert "BTC/USDT:USDT" in markets

    finally:
        exchange.close()