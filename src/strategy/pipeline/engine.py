from dataclasses import dataclass

import pandas as pd

from src.strategy.regime.classifier import RegimeClassifier

from src.strategy.setup.engine import SetupEngine
from src.strategy.setup.models import TradeSetup

from src.strategy.signal.engine import SignalEngine
from src.strategy.signal.models import TradeSignal

from src.strategy.risk.manager import RiskManager
from src.strategy.risk.models import PositionPlan


@dataclass(frozen=True)
class PipelineResult:
    setup: TradeSetup
    signal: TradeSignal
    position: PositionPlan


class StrategyPipeline:

    def __init__(self):

        self.regime_classifier = RegimeClassifier()

        self.setup_engine = SetupEngine()

        self.signal_engine = SignalEngine()

        self.risk_manager = RiskManager()

    def process(
        self,
        row: pd.Series,
        account_balance: float,
        risk_percent: float = 1.0,
        leverage: float = 1.0,
    ) -> PipelineResult:

        # ==================================================
        # 1. REGIME
        # ==================================================

        regime_result = self.regime_classifier.classify(
            row=row,
            structure_label=row.get("structure_label"),
            event_type=row.get("event_type"),
            event_direction=row.get("event_direction"),
        )

        strategy_row = row.copy()

        strategy_row["regime"] = (
            regime_result.regime
        )

        strategy_row["regime_confidence"] = (
            regime_result.confidence
        )

        strategy_row["trend_score"] = (
            regime_result.trend_score
        )

        strategy_row["volatility_score"] = (
            regime_result.volatility_score
        )

        strategy_row["bullish_alignment"] = (
            regime_result.bullish_alignment
        )

        strategy_row["bearish_alignment"] = (
            regime_result.bearish_alignment
        )

        strategy_row["structure_score"] = (
            regime_result.structure_score
        )

        # ==================================================
        # 2. SETUP
        # ==================================================

        setup = self.setup_engine.generate(
            strategy_row
        )

        if not setup.valid:

            return PipelineResult(
                setup=setup,

                signal=self.signal_engine._no_signal(),

                position=self.risk_manager._invalid_plan(
                    account_balance=account_balance,
                ),
            )

        # ==================================================
        # 3. SIGNAL
        # ==================================================

        signal = self.signal_engine.generate(
            setup
        )

        if not signal.valid:

            return PipelineResult(
                setup=setup,

                signal=signal,

                position=self.risk_manager._invalid_plan(
                    account_balance=account_balance,
                ),
            )

        # ==================================================
        # 4. RISK / POSITION
        # ==================================================

        position = self.risk_manager.calculate(
            signal=signal,
            account_balance=account_balance,
            risk_percent=risk_percent,
            leverage=leverage,
        )

        # ==================================================
        # 5. RESULT
        # ==================================================

        return PipelineResult(
            setup=setup,
            signal=signal,
            position=position,
        )