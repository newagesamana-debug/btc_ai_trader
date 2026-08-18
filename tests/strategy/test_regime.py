import pandas as pd

from src.strategy.regime.classifier import RegimeClassifier
from src.strategy.regime.models import MarketRegime


def create_row(**overrides):

    data = {
        "h4_ema_20": 105,
        "h4_ema_50": 100,
        "h4_ema_200": 95,

        "h1_ema_20": 104,
        "h1_ema_50": 100,
        "h1_ema_200": 96,

        "h4_rsi": 60,
        "h1_rsi": 58,

        "h4_atr_pct": 1.5,
        "h1_atr_pct": 1.0,
        "m15_atr_pct": 0.6,
    }

    data.update(overrides)

    return pd.Series(data)


def test_bullish_regime():

    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row()
    )

    assert result.regime == MarketRegime.BULLISH

    assert result.bullish_alignment > 0.5
    assert result.bullish_alignment > result.bearish_alignment

    assert 0.0 <= result.confidence <= 1.0


def test_bearish_regime():

    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(
            h4_ema_20=95,
            h4_ema_50=100,
            h4_ema_200=105,

            h1_ema_20=96,
            h1_ema_50=100,
            h1_ema_200=104,

            h4_rsi=40,
            h1_rsi=42,
        )
    )

    assert result.regime == MarketRegime.BEARISH

    assert result.bearish_alignment > 0.5
    assert result.bearish_alignment > result.bullish_alignment

    assert 0.0 <= result.confidence <= 1.0


def test_range_regime():

    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(
            h4_ema_20=100,
            h4_ema_50=100,
            h4_ema_200=100,

            h1_ema_20=100,
            h1_ema_50=100,
            h1_ema_200=100,

            h4_rsi=50,
            h1_rsi=50,
        )
    )

    assert result.regime == MarketRegime.RANGE


def test_unknown_when_no_features():

    classifier = RegimeClassifier()

    result = classifier.classify(
        pd.Series()
    )

    assert result.regime == MarketRegime.UNKNOWN
    assert result.confidence == 0.0


def test_confidence_is_bounded():

    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row()
    )

    assert 0.0 <= result.confidence <= 1.0
    assert 0.0 <= result.trend_score <= 1.0
    assert 0.0 <= result.volatility_score <= 1.0


def test_high_volatility_increases_volatility_score():

    classifier = RegimeClassifier()

    normal = classifier.classify(
        create_row(
            h4_atr_pct=1.0,
            h1_atr_pct=1.0,
            m15_atr_pct=1.0,
        )
    )

    high_volatility = classifier.classify(
        create_row(
            h4_atr_pct=4.0,
            h1_atr_pct=4.0,
            m15_atr_pct=4.0,
        )
    )

    assert (
            high_volatility.volatility_score
            > normal.volatility_score
    )


def test_hh_produces_bullish_structure_score():
    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(),
        structure_label="HH",
    )

    assert result.structure_score > 0


def test_hl_produces_bullish_structure_score():
    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(),
        structure_label="HL",
    )

    assert result.structure_score > 0


def test_lh_produces_bearish_structure_score():
    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(),
        structure_label="LH",
    )

    assert result.structure_score < 0


def test_ll_produces_bearish_structure_score():
    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(),
        structure_label="LL",
    )

    assert result.structure_score < 0


def test_bullish_bos_produces_positive_structure_score():
    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(),
        event_type="BOS",
        event_direction="BULLISH",
    )

    assert result.structure_score > 0


def test_bearish_bos_produces_negative_structure_score():
    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(),
        event_type="BOS",
        event_direction="BEARISH",
    )

    assert result.structure_score < 0


def test_strong_bearish_structure_can_override_bullish_indicators():

    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(),
        structure_label="LL",
        event_type="CHoCH",
        event_direction="BEARISH",
    )

    assert result.regime == MarketRegime.BEARISH

def test_strong_bullish_structure_can_override_bearish_indicators():

    classifier = RegimeClassifier()

    result = classifier.classify(
        create_row(
            h4_ema_20=95,
            h4_ema_50=100,
            h4_ema_200=105,

            h1_ema_20=96,
            h1_ema_50=100,
            h1_ema_200=104,

            h4_rsi=40,
            h1_rsi=42,
        ),
        structure_label="HH",
        event_type="CHoCH",
        event_direction="BULLISH",
    )

    assert result.regime == MarketRegime.BULLISH