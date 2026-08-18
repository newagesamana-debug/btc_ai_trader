from datetime import datetime, timezone

from src.strategy.structure.classification import (
    StructureClassifier,
)

from src.strategy.structure.models import (
    StructureLabel,
    SwingPoint,
    SwingType,
)


def swing(
    index: int,
    price: float,
    swing_type: SwingType,
) -> SwingPoint:

    return SwingPoint(
        timestamp=datetime.fromtimestamp(
            index * 60,
            tz=timezone.utc,
        ),
        price=price,
        index=index,
        type=swing_type,
        strength=3,
    )


def test_higher_high():

    swings = [
        swing(3, 100, SwingType.HIGH),
        swing(8, 110, SwingType.HIGH),
    ]

    classifier = StructureClassifier()

    result = classifier.classify(swings)

    assert len(result) == 1
    assert result[0].label == StructureLabel.HH


def test_lower_high():

    swings = [
        swing(3, 110, SwingType.HIGH),
        swing(8, 100, SwingType.HIGH),
    ]

    classifier = StructureClassifier()

    result = classifier.classify(swings)

    assert len(result) == 1
    assert result[0].label == StructureLabel.LH


def test_higher_low():

    swings = [
        swing(3, 90, SwingType.LOW),
        swing(8, 100, SwingType.LOW),
    ]

    classifier = StructureClassifier()

    result = classifier.classify(swings)

    assert len(result) == 1
    assert result[0].label == StructureLabel.HL


def test_lower_low():

    swings = [
        swing(3, 100, SwingType.LOW),
        swing(8, 90, SwingType.LOW),
    ]

    classifier = StructureClassifier()

    result = classifier.classify(swings)

    assert len(result) == 1
    assert result[0].label == StructureLabel.LL


def test_first_swing_is_not_classified():

    swings = [
        swing(3, 100, SwingType.HIGH),
    ]

    classifier = StructureClassifier()

    result = classifier.classify(swings)

    assert result == []