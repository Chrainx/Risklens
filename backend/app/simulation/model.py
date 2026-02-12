from dataclasses import dataclass
from .config import PricingSimulationConfig
import math


@dataclass(frozen=True)
class PricingOutcome:
    demand: float
    revenue: float
    total_cost: float
    profit: float

@dataclass(frozen=True)
class PricingDecision:
    price: float


@dataclass(frozen=True)
class PricingParameters:
    base_demand: float
    price_elasticity: float
    unit_cost: float
    fixed_cost: float

def evaluate_pricing_causal_model(
    decision: PricingDecision,
    params: PricingParameters,
) -> PricingOutcome:
    """
    Deterministic causal evaluation of one pricing scenario.
    No randomness. No side effects.
    """

    if decision.price <= 0:
        raise ValueError("Price must be > 0")

    if params.base_demand < 0:
        raise ValueError("Base demand must be >= 0")

    if params.price_elasticity <= 0:
        raise ValueError("Price elasticity must be > 0")

    if params.unit_cost < 0:
        raise ValueError("Unit cost must be >= 0")

    if params.fixed_cost < 0:
        raise ValueError("Fixed cost must be >= 0")

    # 1. Demand
    demand = params.base_demand * math.exp(
        -params.price_elasticity * decision.price
    )
    
    if not math.isfinite(demand):
        raise ValueError("Non-finite demand computed")
    demand = max(0.0, demand)

    # 2. Revenue
    revenue = decision.price * demand

    if not math.isfinite(revenue):
        raise ValueError("Non-finite revenue computed")

    # 3. Cost
    total_cost = params.fixed_cost + params.unit_cost * demand

    if not math.isfinite(total_cost):
        raise ValueError("Non-finite total cost computed")

    # 4. Profit
    profit = revenue - total_cost

    if not math.isfinite(profit):
        raise ValueError("Non-finite profit computed")

    return PricingOutcome(
        demand=demand,
        revenue=revenue,
        total_cost=total_cost,
        profit=profit,
    )

def evaluate_from_config(
    config: PricingSimulationConfig,
) -> PricingOutcome:
    decision = PricingDecision(price=config.price)
    params = PricingParameters(
        base_demand=config.base_demand,
        price_elasticity=config.price_elasticity,
        unit_cost=config.unit_cost,
        fixed_cost=config.fixed_cost,
    )
    return evaluate_pricing_causal_model(decision, params)

def intervene_price(
    decision: PricingDecision,
    new_price: float,
) -> PricingDecision:
    """
    Intervention: do(price = new_price)
    Returns a new decision with price overridden.
    """
    return PricingDecision(price=new_price)
