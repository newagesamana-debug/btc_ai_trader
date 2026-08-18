import pytest

from src.strategy.exit.engine import ExitEngine
from src.strategy.exit.models import ExitReason
from src.strategy.risk.manager import RiskManager
from src.strategy.signal.models import SignalDirection, SignalReason, TradeSignal


def create_position(direction=SignalDirection.LONG):
    signal = TradeSignal(
        direction=direction,
        entry=100_000,
        stop_loss=98_000 if direction == SignalDirection.LONG else 102_000,
        take_profit=106_000 if direction == SignalDirection.LONG else 94_000,
        risk_reward=3.0,
        confidence=0.85,
        reason=(
            SignalReason.BULLISH_BOS
            if direction == SignalDirection.LONG
            else SignalReason.BEARISH_BOS
        ),
        valid=True,
    )
    return RiskManager().calculate(signal, 10_000, 1.0, 1.0)


def test_long_stop_loss():
    result = ExitEngine().evaluate(create_position(), 100_500, 97_900, 2, 24)
    assert result.should_exit is True
    assert result.reason == ExitReason.STOP_LOSS
    assert result.exit_price == 98_000
    assert result.pnl_per_unit == -2_000


def test_long_take_profit():
    result = ExitEngine().evaluate(create_position(), 106_100, 100_100, 2, 24)
    assert result.should_exit is True
    assert result.reason == ExitReason.TAKE_PROFIT
    assert result.exit_price == 106_000
    assert result.pnl_per_unit == 6_000


def test_short_stop_loss():
    result = ExitEngine().evaluate(create_position(SignalDirection.SHORT), 102_100, 99_500, 2, 24)
    assert result.should_exit is True
    assert result.reason == ExitReason.STOP_LOSS
    assert result.exit_price == 102_000
    assert result.pnl_per_unit == -2_000


def test_short_take_profit():
    result = ExitEngine().evaluate(create_position(SignalDirection.SHORT), 99_500, 93_900, 2, 24)
    assert result.should_exit is True
    assert result.reason == ExitReason.TAKE_PROFIT
    assert result.exit_price == 94_000
    assert result.pnl_per_unit == 6_000


def test_time_stop():
    result = ExitEngine().evaluate(create_position(), 100_500, 99_500, 24, 24)
    assert result.should_exit is True
    assert result.reason == ExitReason.TIME_STOP
    assert result.exit_price == 100_000
    assert result.pnl_per_unit == 0


def test_opposite_signal_exit():
    opposite = TradeSignal(
        direction=SignalDirection.SHORT,
        entry=100_000,
        stop_loss=102_000,
        take_profit=94_000,
        risk_reward=3.0,
        confidence=0.85,
        reason=SignalReason.BEARISH_BOS,
        valid=True,
    )
    result = ExitEngine().evaluate(create_position(), 100_500, 99_500, 2, 24, opposite)
    assert result.should_exit is True
    assert result.reason == ExitReason.SIGNAL_EXIT


def test_no_exit_when_no_exit_condition_is_met():
    result = ExitEngine().evaluate(create_position(), 100_500, 99_500, 2, 24)
    assert result.should_exit is False
    assert result.reason == ExitReason.NONE
    assert result.exit_price is None


def test_invalid_position_does_not_exit():
    position = create_position()
    invalid = position.__class__(
        direction=position.direction,
        entry=position.entry,
        stop_loss=position.stop_loss,
        take_profit=position.take_profit,
        account_balance=position.account_balance,
        risk_percent=position.risk_percent,
        risk_amount=position.risk_amount,
        position_size=position.position_size,
        notional_value=position.notional_value,
        leverage=position.leverage,
        max_loss=position.max_loss,
        potential_profit=position.potential_profit,
        risk_reward=position.risk_reward,
        valid=False,
    )
    result = ExitEngine().evaluate(invalid, 110_000, 90_000, 100, 24)
    assert result.should_exit is False
    assert result.reason == ExitReason.NONE


def test_invalid_candle_is_rejected():
    with pytest.raises(ValueError):
        ExitEngine().evaluate(create_position(), 99_000, 101_000, 1, 24)
