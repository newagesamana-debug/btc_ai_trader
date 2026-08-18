from dataclasses import dataclass

from src.strategy.regime.models import RegimeResult, MarketRegime
from src.strategy.setup.models import TradeSetup
from src.strategy.signal.models import TradeSignal
from src.strategy.risk.models import PositionPlan


@dataclass(frozen=True)
class StrategyResult:
    regime: MarketRegime
    regime_confidence: float

    setup: TradeSetup
    signal: TradeSignal
    position: PositionPlan