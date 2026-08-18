from src.strategy.risk.manager import RiskManager
from src.strategy.signal.models import (
    SignalDirection,
    SignalReason,
    TradeSignal,
)


def create_signal(
    direction=SignalDirection.LONG,
    confidence=0.85,
    risk_reward=3.0,
):
    if direction == SignalDirection.LONG:
        entry = 100_000
        stop_loss = 98_000
        take_profit = 106_000
        reason = SignalReason.BULLISH_BOS
    else:
        entry = 100_000
        stop_loss = 102_000
        take_profit = 94_000
        reason = SignalReason.BEARISH_BOS

    return TradeSignal(
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk_reward=risk_reward,
        confidence=confidence,
        reason=reason,
        valid=True,
    )


def test_long_position_size():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )
    assert result.valid is True
    assert result.direction == SignalDirection.LONG
    assert result.risk_amount == 100
    assert result.position_size == 0.05
    assert result.notional_value == 5_000
    assert result.max_loss == 100
    assert result.potential_profit == 300


def test_short_position_size():
    result = RiskManager().calculate(
        signal=create_signal(direction=SignalDirection.SHORT),
        account_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )
    assert result.valid is True
    assert result.direction == SignalDirection.SHORT
    assert result.position_size == 0.05
    assert result.max_loss == 100
    assert result.potential_profit == 300


def test_two_percent_risk():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=10_000,
        risk_percent=2.0,
        leverage=1.0,
    )
    assert result.valid is True
    assert result.risk_amount == 200
    assert result.position_size == 0.1
    assert result.max_loss == 200


def test_invalid_signal_produces_invalid_plan():
    signal = TradeSignal(
        direction=SignalDirection.NONE,
        entry=None,
        stop_loss=None,
        take_profit=None,
        risk_reward=None,
        confidence=0.0,
        reason=SignalReason.NO_SETUP,
        valid=False,
    )
    result = RiskManager().calculate(signal=signal, account_balance=10_000)
    assert result.valid is False
    assert result.direction == SignalDirection.NONE


def test_leverage_limit():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=10_000,
        risk_percent=1.0,
        leverage=11.0,
    )
    assert result.valid is False


def test_zero_balance_is_invalid():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=0,
    )
    assert result.valid is False


def test_negative_risk_is_invalid():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=10_000,
        risk_percent=-1.0,
    )
    assert result.valid is False


def test_leverage_increases_maximum_position_value():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=10_000,
        risk_percent=1.0,
        leverage=5.0,
    )
    assert result.valid is True
    assert result.leverage == 5.0
    assert result.position_size == 0.05
    assert result.notional_value == 5_000
    assert result.max_loss == 100
    assert result.potential_profit == 300


def test_position_exceeding_leverage_limit_is_invalid():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=10_000,
        risk_percent=1.0,
        leverage=0.1,
    )
    assert result.valid is False


def test_configured_max_leverage_is_allowed():
    result = RiskManager().calculate(
        signal=create_signal(),
        account_balance=10_000,
        risk_percent=1.0,
        leverage=10.0,
    )
    assert result.valid is True
    assert result.leverage == 10.0
