from src.config.loader import (
    load_risk_config,
    load_settings,
    load_strategy_config,
)


def test_settings_load():
    settings = load_settings()

    assert settings["app"]["name"] == "btc_ai_trader"
    assert settings["market"]["symbol"] == "BTC/USDT:USDT"


def test_strategy_load():
    strategy = load_strategy_config()

    assert strategy["strategy"]["min_rr"] > 0
    assert 0 < strategy["strategy"]["min_probability"] < 1


def test_risk_load():
    risk = load_risk_config()

    assert 0 < risk["risk"]["base_risk_per_trade"] < 1
    assert risk["risk"]["max_leverage"] > 0