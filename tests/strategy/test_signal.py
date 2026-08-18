
from src.strategy.setup.models import (
    SetupDirection,
    SetupType,
    TradeSetup,
)
from src.strategy.signal.engine import SignalEngine
from src.strategy.signal.models import (
    SignalDirection,
    SignalReason,
)


def create_setup(
    direction=SetupDirection.LONG,
    setup_type=SetupType.BOS_CONTINUATION,
    confidence=0.85,
    risk_reward=3.0,
):

    return TradeSetup(
        direction=direction,
        setup_type=setup_type,

        entry=100_000,
        stop_loss=98_000,
        take_profit=106_000,

        risk=2_000,
        reward=6_000,
        risk_reward=risk_reward,

        confidence=confidence,

        valid=True,
    )


def test_bullish_signal():

    engine = SignalEngine()

    result = engine.generate(
        create_setup()
    )

    assert result.valid is True

    assert result.direction == SignalDirection.LONG

    assert result.entry == 100_000
    assert result.stop_loss == 98_000
    assert result.take_profit == 106_000

    assert result.risk_reward == 3.0


def test_bearish_signal():

    engine = SignalEngine()

    result = engine.generate(
        create_setup(
            direction=SetupDirection.SHORT,
        )
    )

    assert result.valid is True

    assert result.direction == SignalDirection.SHORT

    assert result.entry == 100_000
    assert result.stop_loss == 98_000
    assert result.take_profit == 106_000


def test_invalid_setup_produces_no_signal():

    engine = SignalEngine()

    setup = create_setup()

    invalid_setup = TradeSetup(
        direction=setup.direction,
        setup_type=setup.setup_type,

        entry=setup.entry,
        stop_loss=setup.stop_loss,
        take_profit=setup.take_profit,

        risk=setup.risk,
        reward=setup.reward,
        risk_reward=setup.risk_reward,

        confidence=setup.confidence,

        valid=False,
    )

    result = engine.generate(
        invalid_setup
    )

    assert result.valid is False

    assert result.direction == SignalDirection.NONE


def test_low_confidence_produces_no_signal():

    engine = SignalEngine()

    result = engine.generate(
        create_setup(
            confidence=0.40,
        )
    )

    assert result.valid is False


def test_low_risk_reward_produces_no_signal():

    engine = SignalEngine()

    result = engine.generate(
        create_setup(
            risk_reward=1.5,
        )
    )

    assert result.valid is False


def test_bullish_bos_reason():

    engine = SignalEngine()

    result = engine.generate(
        create_setup(
            setup_type=SetupType.BOS_CONTINUATION,
        )
    )

    assert result.reason == SignalReason.BULLISH_BOS


def test_bullish_choch_reason():

    engine = SignalEngine()

    result = engine.generate(
        create_setup(
            setup_type=SetupType.CHOCH_REVERSAL,
        )
    )

    assert result.reason == SignalReason.BULLISH_CHOCH