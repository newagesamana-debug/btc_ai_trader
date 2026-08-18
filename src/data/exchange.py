import ccxt


class ExchangeClient:
    def __init__(self, exchange_id: str = "binanceusdm"):
        if not hasattr(ccxt, exchange_id):
            raise ValueError(f"Unsupported exchange: {exchange_id}")

        exchange_class = getattr(ccxt, exchange_id)

        self.exchange = exchange_class({
            "enableRateLimit": True,
            "options": {
                "defaultType": "future",
            },
        })

    def load_markets(self) -> dict:
        return self.exchange.load_markets()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: int | None = None,
        limit: int = 1000,
    ) -> list[list[float]]:
        return self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=since,
            limit=limit,
        )

    def close(self) -> None:
        self.exchange.close()