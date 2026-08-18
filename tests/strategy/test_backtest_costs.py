import pandas as pd
import pytest

from src.backtest.engine import BacktestEngine


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
        "close": 100_000,
        "atr": 1_000,
        "swing_low": 98_000,
        "swing_high": 102_000,
        "structure_label": "HH",
        "event_type": "BOS",
        "event_direction": "BULLISH",
    }
    data.update(overrides)
    return pd.Series(data)


def make_data(*rows):
    return pd.DataFrame(rows)


def test_backtest_default_execution_costs_are_zero():
    result = BacktestEngine().run(
        data=make_data(
            create_row(),
            create_row(close=101_000, high=106_700, low=100_500),
        ),
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    trade = result.trades[0]

    assert trade.gross_pnl == pytest.approx(300.0)
    assert trade.fees == pytest.approx(0.0)
    assert trade.slippage_cost == pytest.approx(0.0)
    assert trade.pnl == pytest.approx(300.0)


def test_backtest_applies_fees_and_slippage_to_net_pnl():
    result = BacktestEngine(
        fee_rate=0.0005,
        slippage_bps=10.0,
    ).run(
        data=make_data(
            create_row(),
            create_row(close=101_000, high=106_700, low=100_500),
        ),
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    trade = result.trades[0]

    expected_slippage = (100_000 * 0.001 + 106_600 * 0.001) * (100 / 2200)
    expected_fees = (
        100_000 * (100 / 2200) * 0.0005
        + 106_600 * (100 / 2200) * 0.0005
    )
    expected_net = 300.0 - expected_slippage - expected_fees

    assert trade.gross_pnl == pytest.approx(300.0)
    assert trade.slippage_cost == pytest.approx(expected_slippage)
    assert trade.fees == pytest.approx(expected_fees)
    assert trade.pnl == pytest.approx(expected_net)
    assert result.total_pnl == pytest.approx(expected_net)


def test_backtest_rejects_negative_execution_costs():
    with pytest.raises(ValueError):
        BacktestEngine(fee_rate=-0.0001)

    with pytest.raises(ValueError):
        BacktestEngine(slippage_bps=-1.0)


def test_short_trade_execution_costs_are_directionally_correct():
    result = BacktestEngine(
        fee_rate=0.0005,
        slippage_bps=10.0,
    ).run(
        data=make_data(
            create_row(
                h4_ema_20=95,
                h4_ema_50=100,
                h4_ema_200=105,
                h1_ema_20=96,
                h1_ema_50=100,
                h1_ema_200=104,
                h4_rsi=40,
                h1_rsi=42,
                structure_label="LL",
                event_direction="BEARISH",
            ),
            create_row(
                close=99_000,
                high=102_000,
                low=97_000,
                h4_ema_20=95,
                h4_ema_50=100,
                h4_ema_200=105,
                h1_ema_20=96,
                h1_ema_50=100,
                h1_ema_200=104,
                h4_rsi=40,
                h1_rsi=42,
                structure_label="LL",
                event_direction="BEARISH",
            ),
        ),
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    trade = result.trades[0]

    assert trade.gross_pnl > 0
    assert trade.slippage_cost > 0
    assert trade.fees > 0
    assert trade.pnl < trade.gross_pnl
