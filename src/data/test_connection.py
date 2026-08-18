from src.config.loader import load_settings
from src.data.exchange import ExchangeClient


def main():
    settings = load_settings()

    exchange = ExchangeClient(
        settings["market"]["exchange"]
    )

    try:
        symbol = settings["market"]["symbol"]

        markets = exchange.load_markets()

        if symbol not in markets:
            raise ValueError(
                f"Symbol not found: {symbol}"
            )

        candles = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe="5m",
            limit=10,
        )

        print()
        print("=" * 60)
        print("BINANCE FUTURES DATA TEST")
        print("=" * 60)
        print(f"Symbol: {symbol}")
        print(f"Timeframe: 5m")
        print(f"Candles received: {len(candles)}")
        print()

        for candle in candles[-5:]:
            print(candle)

        print("=" * 60)

    finally:
        exchange.close()


if __name__ == "__main__":
    main()