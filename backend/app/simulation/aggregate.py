from dataclasses import dataclass
from typing import List, Dict
import math

from .model import PricingOutcome


@dataclass(frozen=True)
class SimulationSummary:
    mean_profit: float
    profit_variance: float
    profit_percentiles: Dict[int, float]


def aggregate_outcomes(
    outcomes: List[PricingOutcome],
    percentiles: List[int] = [5, 50, 95],
) -> SimulationSummary:
    if not outcomes:
        raise ValueError("No outcomes to aggregate")

    profits = []
    
    for o in outcomes:
        # Sanity checks per run
        if o.demand < 0:
            raise ValueError("Negative demand detected")

        if not math.isfinite(o.profit):
            raise ValueError("Non-finite profit detected")

        profits.append(o.profit)

    # Mean
    mean = sum(profits) / len(profits)

    # Variance (population variance for MC)
    variance = sum((p - mean) ** 2 for p in profits) / len(profits)

    # Percentiles
    sorted_profits = sorted(profits)
    n = len(sorted_profits)

    pct_values: Dict[int, float] = {}
    for p in percentiles:
        idx = int(math.floor((p / 100) * (n - 1)))
        pct_values[p] = sorted_profits[idx]

    return SimulationSummary(
        mean_profit=mean,
        profit_variance=variance,
        profit_percentiles=pct_values,
    )
