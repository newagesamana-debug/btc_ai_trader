from dataclasses import dataclass
import random

from src.backtest.models import BacktestResult


@dataclass(frozen=True)
class MonteCarloResult:
    simulations: int
    seed: int | None
    median_final_balance: float
    p05_final_balance: float
    p95_final_balance: float
    median_max_drawdown_pct: float
    p95_max_drawdown_pct: float
    probability_of_loss_pct: float
    probability_of_ruin_pct: float


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def run_monte_carlo(
    result: BacktestResult,
    simulations: int = 1_000,
    seed: int | None = 42,
    ruin_threshold_pct: float = 50.0,
) -> MonteCarloResult:
    """Bootstrap completed trade PnLs to estimate outcome robustness.

    Trade order is randomized by sampling with replacement. This is a
    diagnostic tool, not a substitute for an out-of-sample backtest.
    """
    if simulations <= 0:
        raise ValueError("simulations must be positive")
    if ruin_threshold_pct < 0 or ruin_threshold_pct >= 100:
        raise ValueError("ruin_threshold_pct must be in [0, 100)")

    pnls = [trade.pnl for trade in result.trades]
    if not pnls:
        return MonteCarloResult(
            simulations=simulations,
            seed=seed,
            median_final_balance=result.initial_balance,
            p05_final_balance=result.initial_balance,
            p95_final_balance=result.initial_balance,
            median_max_drawdown_pct=0.0,
            p95_max_drawdown_pct=0.0,
            probability_of_loss_pct=0.0,
            probability_of_ruin_pct=0.0,
        )

    rng = random.Random(seed)
    final_balances: list[float] = []
    max_drawdowns: list[float] = []
    losses = 0
    ruins = 0

    ruin_balance = result.initial_balance * (1.0 - ruin_threshold_pct / 100.0)

    for _ in range(simulations):
        balance = result.initial_balance
        peak = balance
        max_drawdown = 0.0

        for _ in pnls:
            balance += rng.choice(pnls)
            peak = max(peak, balance)
            if peak > 0:
                drawdown = (peak - balance) / peak * 100.0
                max_drawdown = max(max_drawdown, drawdown)

        final_balances.append(balance)
        max_drawdowns.append(max_drawdown)
        losses += balance < result.initial_balance
        ruins += balance <= ruin_balance

    return MonteCarloResult(
        simulations=simulations,
        seed=seed,
        median_final_balance=_percentile(final_balances, 0.50),
        p05_final_balance=_percentile(final_balances, 0.05),
        p95_final_balance=_percentile(final_balances, 0.95),
        median_max_drawdown_pct=_percentile(max_drawdowns, 0.50),
        p95_max_drawdown_pct=_percentile(max_drawdowns, 0.95),
        probability_of_loss_pct=losses / simulations * 100.0,
        probability_of_ruin_pct=ruins / simulations * 100.0,
    )
