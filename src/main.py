from src.config.loader import (
    load_risk_config,
    load_settings,
    load_strategy_config,
)


def main() -> None:
    settings = load_settings()
    strategy = load_strategy_config()
    risk = load_risk_config()

    print("=" * 60)
    print("BTC AI TRADER")
    print("=" * 60)

    print(f"Environment: {settings['app']['environment']}")
    print(f"Exchange: {settings['market']['exchange']}")
    print(f"Symbol: {settings['market']['symbol']}")

    print(f"Primary timeframe: {settings['timeframes']['primary']}")
    print(f"Setup timeframe: {settings['timeframes']['setup']}")
    print(f"Trend timeframe: {settings['timeframes']['trend']}")
    print(f"Regime timeframe: {settings['timeframes']['regime']}")

    print(f"Trading enabled: {settings['execution']['trading_enabled']}")
    print(f"Live trading enabled: {settings['execution']['live_trading_enabled']}")

    print(f"Base risk: {risk['risk']['base_risk_per_trade'] * 100:.2f}%")
    print(f"Max leverage: {risk['risk']['max_leverage']}x")

    print(f"Minimum RR: {strategy['strategy']['min_rr']}")
    print(f"Minimum probability: {strategy['strategy']['min_probability']}")

    print("=" * 60)
    print("SYSTEM INITIALIZED")
    print("=" * 60)


if __name__ == "__main__":
    main()