import pandas as pd

from src.strategy.engine import StrategyEngine
from src.strategy.exit.engine import ExitEngine
from src.strategy.exit.models import ExitReason
from src.strategy.risk.models import PositionPlan
from src.strategy.signal.models import SignalDirection

from src.backtest.models import BacktestResult, BacktestTrade


class BacktestEngine:
    def __init__(
        self,
        fee_rate: float = 0.0,
        slippage_bps: float = 0.0,
    ):
        if fee_rate < 0:
            raise ValueError("fee_rate must be non-negative")
        if slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")

        self.strategy_engine = StrategyEngine()
        self.exit_engine = ExitEngine()
        self.fee_rate = fee_rate
        self.slippage_bps = slippage_bps

    def run(
        self,
        data: pd.DataFrame,
        initial_balance: float,
        risk_percent: float = 1.0,
        leverage: float = 1.0,
        max_candles: int = 24,
    ) -> BacktestResult:
        if initial_balance <= 0:
            raise ValueError("initial_balance must be positive")

        if max_candles <= 0:
            raise ValueError("max_candles must be positive")

        if data.empty:
            return self._empty_result(initial_balance)

        required_columns = {"high", "low", "close"}
        missing = required_columns.difference(data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        balance = initial_balance
        peak_balance = initial_balance
        max_drawdown_pct = 0.0

        position: PositionPlan | None = None
        entry_index: int | None = None
        candles_held = 0
        trades: list[BacktestTrade] = []

        for index, row in data.reset_index(drop=True).iterrows():
            if position is not None:
                candles_held += 1

                pipeline_result = self.strategy_engine.evaluate(
                    row=row,
                    account_balance=balance,
                    risk_percent=risk_percent,
                    leverage=leverage,
                )
                signal = pipeline_result.signal

                decision = self.exit_engine.evaluate(
                    position=position,
                    candle_high=float(row["high"]),
                    candle_low=float(row["low"]),
                    candles_held=candles_held,
                    max_candles=max_candles,
                    signal=signal,
                )

                if decision.should_exit:
                    trade = self._build_trade(
                        position=position,
                        entry_index=entry_index,
                        exit_index=index,
                        exit_price=decision.exit_price,
                        reason=decision.reason,
                        candles_held=candles_held,
                    )
                    balance += trade.pnl
                    trades.append(trade)

                    position = None
                    entry_index = None
                    candles_held = 0

                    peak_balance = max(peak_balance, balance)
                    drawdown_pct = (
                        (peak_balance - balance) / peak_balance * 100.0
                    )
                    max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)

                continue

            pipeline_result = self.strategy_engine.evaluate(
                row=row,
                account_balance=balance,
                risk_percent=risk_percent,
                leverage=leverage,
            )

            signal = pipeline_result.signal
            if not signal.valid:
                continue

            position_candidate = pipeline_result.position
            if not position_candidate.valid:
                continue

            position = position_candidate
            entry_index = index
            candles_held = 0

        if position is not None and entry_index is not None:
            last_index = len(data) - 1
            last_close = float(data.iloc[-1]["close"])

            trade = self._build_trade(
                position=position,
                entry_index=entry_index,
                exit_index=last_index,
                exit_price=last_close,
                reason=ExitReason.END_OF_DATA,
                candles_held=candles_held,
            )
            balance += trade.pnl
            trades.append(trade)

            peak_balance = max(peak_balance, balance)
            drawdown_pct = (
                (peak_balance - balance) / peak_balance * 100.0
            )
            max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)

        winning_trades = sum(1 for trade in trades if trade.pnl > 0)
        losing_trades = sum(1 for trade in trades if trade.pnl < 0)
        total_trades = len(trades)

        win_rate_pct = (
            winning_trades / total_trades * 100.0
            if total_trades
            else 0.0
        )

        return BacktestResult(
            initial_balance=initial_balance,
            final_balance=balance,
            total_pnl=balance - initial_balance,
            return_pct=(balance - initial_balance) / initial_balance * 100.0,
            max_drawdown_pct=max_drawdown_pct,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate_pct=win_rate_pct,
            trades=tuple(trades),
        )

    def _build_trade(
        self,
        position: PositionPlan,
        entry_index: int,
        exit_index: int,
        exit_price: float,
        reason: ExitReason,
        candles_held: int,
    ) -> BacktestTrade:
        entry_price = float(position.entry)
        exit_price = float(exit_price)
        position_size = float(position.position_size)

        if position.direction == SignalDirection.LONG:
            gross_pnl = (exit_price - entry_price) * position_size
            entry_execution = self._apply_slippage(entry_price, is_buy=True)
            exit_execution = self._apply_slippage(exit_price, is_buy=False)
        else:
            gross_pnl = (entry_price - exit_price) * position_size
            entry_execution = self._apply_slippage(entry_price, is_buy=False)
            exit_execution = self._apply_slippage(exit_price, is_buy=True)

        slippage_cost = abs(
            (entry_execution - entry_price) * position_size
        ) + abs(
            (exit_execution - exit_price) * position_size
        )

        execution_pnl = gross_pnl - slippage_cost
        fees = (
            entry_execution * position_size * self.fee_rate
            + exit_execution * position_size * self.fee_rate
        )
        net_pnl = execution_pnl - fees

        return BacktestTrade(
            entry_index=entry_index,
            exit_index=exit_index,
            direction=position.direction,
            entry_price=entry_price,
            exit_price=exit_price,
            position_size=position_size,
            pnl=net_pnl,
            risk_amount=position.risk_amount,
            reason=reason,
            candles_held=candles_held,
            gross_pnl=gross_pnl,
            fees=fees,
            slippage_cost=slippage_cost,
        )

    def _apply_slippage(self, price: float, is_buy: bool) -> float:
        multiplier = self.slippage_bps / 10_000.0
        if is_buy:
            return price * (1.0 + multiplier)
        return price * (1.0 - multiplier)

    @staticmethod
    def _empty_result(initial_balance: float) -> BacktestResult:
        return BacktestResult(
            initial_balance=initial_balance,
            final_balance=initial_balance,
            total_pnl=0.0,
            return_pct=0.0,
            max_drawdown_pct=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate_pct=0.0,
            trades=(),
        )
