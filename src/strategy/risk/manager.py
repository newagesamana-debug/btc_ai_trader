from src.config.loader import load_risk_config
from src.strategy.signal.models import SignalDirection, TradeSignal
from src.strategy.risk.models import PositionPlan


class RiskManager:
    DEFAULT_RISK_PERCENT = 1.0
    DEFAULT_MAX_LEVERAGE = 5.0

    def __init__(self, config: dict | None = None):
        config = config if config is not None else load_risk_config()
        risk = config.get("risk", {})

        self.base_risk_percent = float(risk.get("base_risk_per_trade", 0.005)) * 100.0
        self.max_risk_percent = float(risk.get("max_risk_per_trade", 0.0075)) * 100.0
        self.min_leverage = float(risk.get("min_leverage", 1.0))
        self.max_leverage = float(
            risk.get("max_leverage", self.DEFAULT_MAX_LEVERAGE)
        )

        if self.base_risk_percent <= 0:
            raise ValueError("base_risk_per_trade must be positive")
        if self.max_risk_percent <= 0:
            raise ValueError("max_risk_per_trade must be positive")
        if self.max_risk_percent < self.base_risk_percent:
            raise ValueError("max_risk_per_trade must be >= base_risk_per_trade")
        if self.min_leverage <= 0:
            raise ValueError("min_leverage must be positive")
        if self.max_leverage < self.min_leverage:
            raise ValueError("max_leverage must be >= min_leverage")

    def calculate(
        self,
        signal: TradeSignal,
        account_balance: float,
        risk_percent: float | None = None,
        leverage: float | None = None,
    ) -> PositionPlan:
        if not signal.valid or signal.entry is None or signal.stop_loss is None or signal.take_profit is None:
            return self._invalid_plan(account_balance)

        if account_balance <= 0:
            return self._invalid_plan(account_balance)

        if risk_percent is None:
            risk_percent = self.base_risk_percent

        if leverage is None:
            leverage = self.min_leverage

        if risk_percent <= 0 or risk_percent > self.max_risk_percent:
            return self._invalid_plan(account_balance)

        if leverage < self.min_leverage or leverage > self.max_leverage:
            return self._invalid_plan(account_balance)

        risk_amount = account_balance * risk_percent / 100.0

        if signal.direction == SignalDirection.LONG:
            price_risk = signal.entry - signal.stop_loss
            potential_profit_per_unit = signal.take_profit - signal.entry
        elif signal.direction == SignalDirection.SHORT:
            price_risk = signal.stop_loss - signal.entry
            potential_profit_per_unit = signal.entry - signal.take_profit
        else:
            return self._invalid_plan(account_balance)

        if price_risk <= 0 or potential_profit_per_unit <= 0:
            return self._invalid_plan(account_balance)

        position_size = risk_amount / price_risk
        notional_value = position_size * signal.entry
        maximum_position_value = account_balance * leverage

        if notional_value > maximum_position_value:
            return self._invalid_plan(account_balance)

        return PositionPlan(
            direction=signal.direction,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            account_balance=account_balance,
            risk_percent=risk_percent,
            risk_amount=risk_amount,
            position_size=position_size,
            notional_value=notional_value,
            leverage=leverage,
            max_loss=position_size * price_risk,
            potential_profit=position_size * potential_profit_per_unit,
            risk_reward=signal.risk_reward,
            valid=True,
        )

    @staticmethod
    def _invalid_plan(account_balance: float) -> PositionPlan:
        return PositionPlan(
            direction=SignalDirection.NONE,
            entry=None,
            stop_loss=None,
            take_profit=None,
            account_balance=account_balance,
            risk_percent=0.0,
            risk_amount=0.0,
            position_size=0.0,
            notional_value=0.0,
            leverage=0.0,
            max_loss=0.0,
            potential_profit=0.0,
            risk_reward=None,
            valid=False,
        )
