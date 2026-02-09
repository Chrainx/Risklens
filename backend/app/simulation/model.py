# risklens/simulation/model.py

from dataclasses import dataclass
from .config import PricingSimulationConfig
import math


@dataclass(frozen=True)
class PricingOutcome:
    demand: float
    revenue: float
    total_cost: float
    profit: float


def evaluate_pricing_causal_model(
    config: PricingSimulationConfig,
) -> PricingOutcome:
    """
    Deterministic causal evaluation of one pricing scenario.
    No randomness. No side effects.
    """

    # 1. Demand
    demand = config.base_demand * math.exp(
        -config.price_elasticity * config.price
    )
    demand = max(0.0, demand)

    # 2. Revenue
    revenue = config.price * demand

    # 3. Cost
    total_cost = config.fixed_cost + config.unit_cost * demand

    # 4. Profit
    profit = revenue - total_cost

    return PricingOutcome(
        demand=demand,
        revenue=revenue,
        total_cost=total_cost,
        profit=profit,
    )
