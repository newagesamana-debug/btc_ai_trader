from pathlib import Path

import pandas as pd

from src.backtest.engine import BacktestEngine
from src.backtest.metrics import BacktestMetrics, calculate_metrics
from src.backtest.models import BacktestResult


class BacktestRunner:
    """Load historical candles and run a reproducible strategy backtest."""

    def __init__(
        self,
        fee_rate: float = 0.0005,
        slippage_bps: float = 2.0,
    ):
        self.engine = BacktestEngine(
            fee_rate=fee_rate,
            slippage_bps=slippage_bps,
        )

    def run_file(
        self,
        path: str | Path,
        initial_balance: float,
        risk_percent: float = 1.0,
        leverage: float = 1.0,
        max_candles: int = 24,
    ) -> tuple[BacktestResult, BacktestMetrics]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Backtest data not found: {path}")

        if path.suffix.lower() == ".parquet":
            data = pd.read_parquet(path)
        elif path.suffix.lower() == ".csv":
            data = pd.read_csv(path)
        else:
            raise ValueError("Unsupported data format. Use .parquet or .csv")

        self._validate_data(data)

        result = self.engine.run(
            data=data,
            initial_balance=initial_balance,
            risk_percent=risk_percent,
            leverage=leverage,
            max_candles=max_candles,
        )
        return result, calculate_metrics(result)

    @staticmethod
    def _validate_data(data: pd.DataFrame) -> None:
        required = {"open", "high", "low", "close"}
        missing = sorted(required.difference(data.columns))
        if missing:
            raise ValueError(f"Missing OHLC columns: {missing}")

        if data.empty:
            return

        if data[list(required)].isnull().any().any():
            raise ValueError("Backtest data contains null OHLC values")

        if (data["high"] < data["low"]).any():
            raise ValueError("Backtest data contains high < low")

        if (data["high"] < data["open"]).any() or (data["high"] < data["close"]).any():
            raise ValueError("Backtest data contains prices above high")

        if (data["low"] > data["open"]).any() or (data["low"] > data["close"]).any():
            raise ValueError("Backtest data contains prices below low")
