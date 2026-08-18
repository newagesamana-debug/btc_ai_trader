from src.strategy.exit.models import ExitDecision, ExitReason
from src.strategy.signal.models import SignalDirection, TradeSignal
from src.strategy.risk.models import PositionPlan


class ExitEngine:
    def evaluate(
        self,
        position: PositionPlan,
        candle_high: float,
        candle_low: float,
        candles_held: int,
        max_candles: int,
        signal: TradeSignal | None = None,
    ) -> ExitDecision:
        if not position.valid:
            return self._no_exit(candles_held)

        if candle_high < candle_low:
            raise ValueError("candle_high cannot be below candle_low")

        if candles_held < 0:
            raise ValueError("candles_held cannot be negative")

        if max_candles <= 0:
            raise ValueError("max_candles must be positive")

        if position.direction == SignalDirection.LONG:
            if candle_low <= position.stop_loss:
                return self._exit(
                    ExitReason.STOP_LOSS,
                    position.stop_loss,
                    position.entry,
                    candles_held,
                )

            if candle_high >= position.take_profit:
                return self._exit(
                    ExitReason.TAKE_PROFIT,
                    position.take_profit,
                    position.entry,
                    candles_held,
                )

        elif position.direction == SignalDirection.SHORT:
            if candle_high >= position.stop_loss:
                return self._exit(
                    ExitReason.STOP_LOSS,
                    position.stop_loss,
                    position.entry,
                    candles_held,
                )

            if candle_low <= position.take_profit:
                return self._exit(
                    ExitReason.TAKE_PROFIT,
                    position.take_profit,
                    position.entry,
                    candles_held,
                )

        if candles_held >= max_candles:
            return self._exit(
                ExitReason.TIME_STOP,
                position.entry,
                position.entry,
                candles_held,
            )

        if signal is not None and signal.valid:
            opposite = (
                position.direction == SignalDirection.LONG
                and signal.direction == SignalDirection.SHORT
            ) or (
                position.direction == SignalDirection.SHORT
                and signal.direction == SignalDirection.LONG
            )

            if opposite:
                return self._exit(
                    ExitReason.SIGNAL_EXIT,
                    position.entry,
                    position.entry,
                    candles_held,
                )

        return self._no_exit(candles_held)

    @staticmethod
    def _exit(
        reason: ExitReason,
        exit_price: float,
        entry_price: float | None,
        candles_held: int,
    ) -> ExitDecision:
        if entry_price is None:
            return ExitDecision(False, ExitReason.NONE, None, None, candles_held)

        pnl_per_unit = exit_price - entry_price
        return ExitDecision(
            should_exit=True,
            reason=reason,
            exit_price=exit_price,
            pnl_per_unit=pnl_per_unit,
            candles_held=candles_held,
        )

    @staticmethod
    def _no_exit(candles_held: int) -> ExitDecision:
        return ExitDecision(
            should_exit=False,
            reason=ExitReason.NONE,
            exit_price=None,
            pnl_per_unit=None,
            candles_held=candles_held,
        )
