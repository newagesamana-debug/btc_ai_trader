import pandas as pd

from src.strategy.pipeline.engine import (
    PipelineResult,
    StrategyPipeline,
)


class StrategyEngine:

    def __init__(self):

        self.pipeline = StrategyPipeline()

    def evaluate(
        self,
        row: pd.Series,
        account_balance: float = 10_000,
        risk_percent: float = 1.0,
        leverage: float = 1.0,
    ) -> PipelineResult:

        return self.pipeline.process(
            row=row,
            account_balance=account_balance,
            risk_percent=risk_percent,
            leverage=leverage,
        )