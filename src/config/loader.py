from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


def load_yaml(filename: str) -> dict[str, Any]:
    path = CONFIG_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in {path}")

    return data


def load_settings() -> dict[str, Any]:
    return load_yaml("settings.yaml")


def load_strategy_config() -> dict[str, Any]:
    return load_yaml("strategy.yaml")


def load_risk_config() -> dict[str, Any]:
    return load_yaml("risk.yaml")