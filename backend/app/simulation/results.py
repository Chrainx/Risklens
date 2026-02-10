from dataclasses import dataclass
from typing import List

from .config import PricingSimulationConfig
from .model import PricingOutcome
from .monte_carlo import run_monte_carlo
from .aggregate import aggregate_outcomes, SimulationSummary


@dataclass(frozen=True)
class SimulationResult:
    outcomes: List[PricingOutcome]
    summary: SimulationSummary


def run_simulation(
    config: PricingSimulationConfig,
) -> SimulationResult:
    """
    High-level orchestration for a single pricing simulation.
    Runs Monte Carlo and aggregates results.
    """
    outcomes = run_monte_carlo(config)
    summary = aggregate_outcomes(outcomes)
    return SimulationResult(
        outcomes=outcomes,
        summary=summary,
    )