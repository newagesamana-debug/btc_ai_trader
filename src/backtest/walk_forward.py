from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.backtest.engine import BacktestEngine
from src.backtest.metrics import BacktestMetrics, calculate_metrics
from src.backtest.models import BacktestResult
from src.backtest.runner import BacktestRunner


@dataclass(frozen=True)
class WalkForwardFold:
    fold: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    result: BacktestResult
    metrics: BacktestMetrics


@dataclass(frozen=True)
class WalkForwardResult:
    initial_balance: float
    folds: tuple[WalkForwardFold, ...]
    combined_result: BacktestResult
    combined_metrics: BacktestMetrics

    @property
    def total_folds(self) -> int:
        return len(self.folds)


class WalkForwardRunner:
    """Evaluate a strategy on sequential out-of-sample windows.

    The current strategy has no parameter-fitting step, so the training
    window is retained as an explicit part of the evaluation protocol and
    can be used by a future optimizer. No test-window data is used to create
    the preceding training window.
    """

    def __init__(self, fee_rate: float = 0.0005, slippage_bps: float = 2.0):
        self.engine = BacktestEngine(
            fee_rate=fee_rate,
            slippage_bps=slippage_bps,
        )

    def run(
        self,
        data: pd.DataFrame,
        initial_balance: float,
        train_size: int,
        test_size: int,
        step_size: int | None = None,
        risk_percent: float = 1.0,
        leverage: float = 1.0,
        max_candles: int = 24,
    ) -> WalkForwardResult:
        if initial_balance <= 0:
            raise ValueError("initial_balance must be positive")
        if train_size <= 0:
            raise ValueError("train_size must be positive")
        if test_size <= 0:
            raise ValueError("test_size must be positive")
        if step_size is None:
            step_size = test_size
        if step_size <= 0:
            raise ValueError("step_size must be positive")

        BacktestRunner._validate_data(data)
        data = data.reset_index(drop=True)

        if len(data) < train_size + test_size:
            raise ValueError(
                "Not enough data for one walk-forward fold: "
                f"need at least {train_size + test_size} rows, got {len(data)}"
            )

        folds: list[WalkForwardFold] = []
        fold_number = 1
        test_start = train_size

        while test_start + test_size <= len(data):
            train_start = max(0, test_start - train_size)
            train_end = test_start
            test_end = test_start + test_size
            test_data = data.iloc[test_start:test_end].copy()

            result = self.engine.run(
                data=test_data,
                initial_balance=initial_balance,
                risk_percent=risk_percent,
                leverage=leverage,
                max_candles=max_candles,
            )

            folds.append(
                WalkForwardFold(
                    fold=fold_number,
                    train_start=train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                    result=result,
                    metrics=calculate_metrics(result),
                )
            )

            fold_number += 1
            test_start += step_size

        combined_result = _combine_results(initial_balance, folds)
        return WalkForwardResult(
            initial_balance=initial_balance,
            folds=tuple(folds),
            combined_result=combined_result,
            combined_metrics=calculate_metrics(combined_result),
        )

    def run_file(
        self,
        path: str | Path,
        initial_balance: float,
        train_size: int,
        test_size: int,
        step_size: int | None = None,
        risk_percent: float = 1.0,
        leverage: float = 1.0,
        max_candles: int = 24,
    ) -> WalkForwardResult:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Backtest data not found: {path}")

        if path.suffix.lower() == ".parquet":
            data = pd.read_parquet(path)
        elif path.suffix.lower() == ".csv":
            data = pd.read_csv(path)
        else:
            raise ValueError("Unsupported data format. Use .parquet or .csv")

        return self.run(
            data=data,
            initial_balance=initial_balance,
            train_size=train_size,
            test_size=test_size,
            step_size=step_size,
            risk_percent=risk_percent,
            leverage=leverage,
            max_candles=max_candles,
        )


def _combine_results(
    initial_balance: float,
    folds: list[WalkForwardFold],
) -> BacktestResult:
    trades = tuple(trade for fold in folds for trade in fold.result.trades)
    final_balance = initial_balance + sum(trade.pnl for trade in trades)

    equity = [initial_balance]
    balance = initial_balance
    peak = initial_balance
    max_drawdown_pct = 0.0
    for trade in trades:
        balance += trade.pnl
        equity.append(balance)
        peak = max(peak, balance)
        if peak > 0:
            max_drawdown_pct = max(
                max_drawdown_pct,
                (peak - balance) / peak * 100.0,
            )

    winning_trades = sum(1 for trade in trades if trade.pnl > 0)
    losing_trades = sum(1 for trade in trades if trade.pnl < 0)
    total_trades = len(trades)

    return BacktestResult(
        initial_balance=initial_balance,
        final_balance=final_balance,
        total_pnl=final_balance - initial_balance,
        return_pct=(final_balance - initial_balance) / initial_balance * 100.0,
        max_drawdown_pct=max_drawdown_pct,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate_pct=(winning_trades / total_trades * 100.0 if total_trades else 0.0),
        trades=trades,
        equity_curve=tuple(equity),
    )
