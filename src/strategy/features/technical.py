import pandas as pd
import numpy as np

from src.strategy.features.models import (
    TechnicalFeatures,
)


class TechnicalFeatureEngine:

    def calculate(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        self._validate_dataframe(dataframe)

        df = dataframe.copy()

        df = df.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        # --------------------------------------------------
        # EMA
        # --------------------------------------------------

        df["ema_20"] = (
            df["close"]
            .ewm(
                span=20,
                adjust=False,
            )
            .mean()
        )

        df["ema_50"] = (
            df["close"]
            .ewm(
                span=50,
                adjust=False,
            )
            .mean()
        )

        df["ema_200"] = (
            df["close"]
            .ewm(
                span=200,
                adjust=False,
            )
            .mean()
        )

        # --------------------------------------------------
        # RSI
        # --------------------------------------------------

        delta = df["close"].diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        avg_gain = gain.ewm(
            alpha=1 / 14,
            adjust=False,
            min_periods=14,
        ).mean()

        avg_loss = loss.ewm(
            alpha=1 / 14,
            adjust=False,
            min_periods=14,
        ).mean()

        rs = pd.Series(
            np.nan,
            index=df.index,
        )

        normal = avg_loss > 0

        rs.loc[normal] = (
                avg_gain.loc[normal]
                / avg_loss.loc[normal]
        )

        gain_only = (
                (avg_loss == 0)
                & (avg_gain > 0)
        )

        loss_only = (
                (avg_gain == 0)
                & (avg_loss > 0)
        )

        rs.loc[gain_only] = np.inf
        rs.loc[loss_only] = 0.0

        df["rsi_14"] = (
                100
                - (
                        100
                        / (1 + rs)
                )
        )

        # --------------------------------------------------
        # True Range
        # --------------------------------------------------

        previous_close = (
            df["close"].shift(1)
        )

        tr_components = pd.concat(
            [
                df["high"] - df["low"],
                (
                    df["high"]
                    - previous_close
                ).abs(),
                (
                    df["low"]
                    - previous_close
                ).abs(),
            ],
            axis=1,
        )

        true_range = tr_components.max(
            axis=1
        )

        # --------------------------------------------------
        # ATR
        # --------------------------------------------------

        df["atr_14"] = (
            true_range
            .ewm(
                alpha=1 / 14,
                adjust=False,
                min_periods=14,
            )
            .mean()
        )

        df["atr_pct"] = (
            df["atr_14"]
            / df["close"]
            * 100
        )

        # --------------------------------------------------
        # ROC
        # --------------------------------------------------

        df["roc_10"] = (
            df["close"]
            .pct_change(10)
            * 100
        )

        # --------------------------------------------------
        # Volume
        # --------------------------------------------------

        df["volume_ma_20"] = (
            df["volume"]
            .rolling(20)
            .mean()
        )

        df["volume_ratio"] = (
            df["volume"]
            / df["volume_ma_20"]
        )

        return df

    @staticmethod
    def _validate_dataframe(
        dataframe: pd.DataFrame,
    ) -> None:

        required = {
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        }

        missing = (
            required
            - set(dataframe.columns)
        )

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        if dataframe.empty:
            raise ValueError(
                "Dataframe is empty"
            )