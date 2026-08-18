import pandas as pd

from src.strategy.structure.events import (
    StructureEventDetector,
)

from src.strategy.structure.models import (
    ClassifiedSwing,
    StructureEventType,
    StructureLabel,
    SwingPoint,
    SwingType,
)


def create_swing(
    index: int,
    price: float,
    swing_type: SwingType,
    label: StructureLabel,
):

    return ClassifiedSwing(
        swing=SwingPoint(
            timestamp=pd.Timestamp(
                "2026-01-01"
            ).to_pydatetime(),
            price=price,
            index=index,
            type=swing_type,
            strength=3,
        ),
        label=label,
    )


def test_bullish_bos():

    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=6,
                freq="1min",
                tz="UTC",
            ),
            "close": [
                100,
                105,
                103,
                104,
                106,
                108,
            ],
        }
    )

    swings = [
        create_swing(
            index=1,
            price=105,
            swing_type=SwingType.HIGH,
            label=StructureLabel.HH,
        )
    ]

    detector = StructureEventDetector()

    events = detector.detect(
        dataframe,
        swings,
    )

    assert len(events) == 1

    event = events[0]

    assert event.event_type == StructureEventType.BOS
    assert event.broken_level == 105
    assert event.break_price == 106
    assert event.candle_index == 4


def test_bearish_bos():

    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=6,
                freq="1min",
                tz="UTC",
            ),
            "close": [
                100,
                95,
                97,
                96,
                94,
                92,
            ],
        }
    )

    swings = [
        create_swing(
            index=1,
            price=95,
            swing_type=SwingType.LOW,
            label=StructureLabel.LL,
        )
    ]

    detector = StructureEventDetector()

    events = detector.detect(
        dataframe,
        swings,
    )

    assert len(events) == 1

    event = events[0]

    assert event.event_type == StructureEventType.BOS
    assert event.broken_level == 95
    assert event.break_price == 94
    assert event.candle_index == 4


def test_bullish_choch():

    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=5,
                freq="1min",
                tz="UTC",
            ),
            "close": [
                100,
                95,
                97,
                99,
                106,
            ],
        }
    )

    swings = [
        create_swing(
            index=1,
            price=105,
            swing_type=SwingType.HIGH,
            label=StructureLabel.LH,
        )
    ]

    detector = StructureEventDetector()

    events = detector.detect(
        dataframe,
        swings,
    )

    assert len(events) == 1
    assert (
        events[0].event_type
        == StructureEventType.CHOCH
    )


def test_no_break_no_event():

    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=5,
                freq="1min",
                tz="UTC",
            ),
            "close": [
                100,
                102,
                103,
                104,
                104,
            ],
        }
    )

    swings = [
        create_swing(
            index=1,
            price=110,
            swing_type=SwingType.HIGH,
            label=StructureLabel.HH,
        )
    ]

    detector = StructureEventDetector()

    events = detector.detect(
        dataframe,
        swings,
    )

    assert events == []