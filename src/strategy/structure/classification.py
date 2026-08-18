from src.strategy.structure.models import (
    ClassifiedSwing,
    StructureLabel,
    SwingPoint,
    SwingType,
)


class StructureClassifier:

    def classify(
        self,
        swings: list[SwingPoint],
    ) -> list[ClassifiedSwing]:

        if not swings:
            return []

        swings = sorted(
            swings,
            key=lambda swing: swing.index,
        )

        previous_high = None
        previous_low = None

        result = []

        for swing in swings:

            if swing.type == SwingType.HIGH:

                if previous_high is None:
                    previous_high = swing
                    continue

                if swing.price > previous_high.price:
                    label = StructureLabel.HH
                else:
                    label = StructureLabel.LH

                result.append(
                    ClassifiedSwing(
                        swing=swing,
                        label=label,
                    )
                )

                previous_high = swing

            elif swing.type == SwingType.LOW:

                if previous_low is None:
                    previous_low = swing
                    continue

                if swing.price > previous_low.price:
                    label = StructureLabel.HL
                else:
                    label = StructureLabel.LL

                result.append(
                    ClassifiedSwing(
                        swing=swing,
                        label=label,
                    )
                )

                previous_low = swing

        return result