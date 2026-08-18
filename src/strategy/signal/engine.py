from src.strategy.setup.models import (
    SetupDirection,
    SetupType,
    TradeSetup,
)

from src.strategy.signal.models import (
    SignalDirection,
    SignalReason,
    TradeSignal,
)


class SignalEngine:

    MIN_CONFIDENCE = 0.65
    MIN_RISK_REWARD = 2.0

    def generate(
        self,
        setup: TradeSetup,
    ) -> TradeSignal:

        if not setup.valid:
            return self._no_signal()

        if setup.confidence < self.MIN_CONFIDENCE:
            return self._no_signal()

        if setup.risk_reward is None:
            return self._no_signal()

        if setup.risk_reward < self.MIN_RISK_REWARD:
            return self._no_signal()

        if setup.entry is None:
            return self._no_signal()

        if setup.stop_loss is None:
            return self._no_signal()

        if setup.take_profit is None:
            return self._no_signal()

        # --------------------------------------------------
        # LONG
        # --------------------------------------------------

        if setup.direction == SetupDirection.LONG:

            reason = self._determine_long_reason(
                setup
            )

            return TradeSignal(
                direction=SignalDirection.LONG,

                entry=setup.entry,
                stop_loss=setup.stop_loss,
                take_profit=setup.take_profit,

                risk_reward=setup.risk_reward,

                confidence=setup.confidence,

                reason=reason,

                valid=True,
            )

        # --------------------------------------------------
        # SHORT
        # --------------------------------------------------

        if setup.direction == SetupDirection.SHORT:

            reason = self._determine_short_reason(
                setup
            )

            return TradeSignal(
                direction=SignalDirection.SHORT,

                entry=setup.entry,
                stop_loss=setup.stop_loss,
                take_profit=setup.take_profit,

                risk_reward=setup.risk_reward,

                confidence=setup.confidence,

                reason=reason,

                valid=True,
            )

        return self._no_signal()

    # ======================================================
    # LONG REASON
    # ======================================================

    @staticmethod
    def _determine_long_reason(
        setup: TradeSetup,
    ) -> SignalReason:

        if setup.setup_type == SetupType.CHOCH_REVERSAL:
            return SignalReason.BULLISH_CHOCH

        if setup.setup_type == SetupType.BOS_CONTINUATION:
            return SignalReason.BULLISH_BOS

        return SignalReason.TREND_CONTINUATION

    # ======================================================
    # SHORT REASON
    # ======================================================

    @staticmethod
    def _determine_short_reason(
        setup: TradeSetup,
    ) -> SignalReason:

        if setup.setup_type == SetupType.CHOCH_REVERSAL:
            return SignalReason.BEARISH_CHOCH

        if setup.setup_type == SetupType.BOS_CONTINUATION:
            return SignalReason.BEARISH_BOS

        return SignalReason.TREND_CONTINUATION

    # ======================================================
    # NO SIGNAL
    # ======================================================

    @staticmethod
    def _no_signal() -> TradeSignal:

        return TradeSignal(
            direction=SignalDirection.NONE,

            entry=None,
            stop_loss=None,
            take_profit=None,

            risk_reward=None,

            confidence=0.0,

            reason=SignalReason.NO_SETUP,

            valid=False,
        )