from typing import Dict, List, Tuple

from .config import PricingSimulationConfig
from .results import run_simulation


def sensitivity_analysis(
    base_config: PricingSimulationConfig,
    perturbation: float = 0.1,  # 10% change
) -> Dict[str, float]:
    """
    Measures sensitivity of mean profit to each key assumption.
    Returns absolute change in mean profit.
    """

    base_result = run_simulation(base_config)
    base_profit = base_result.summary.mean_profit

    impacts: Dict[str, float] = {}

    # Helper to clone config with modifications
    def modified_config(**changes):
        data = base_config.__dict__.copy()
        data.update(changes)
        return PricingSimulationConfig(**data)

    # Base demand sensitivity
    cfg = modified_config(
        base_demand=base_config.base_demand * (1 + perturbation)
    )
    impacts["base_demand"] = (
        run_simulation(cfg).summary.mean_profit - base_profit
    )

    # Price elasticity sensitivity
    cfg = modified_config(
        price_elasticity=base_config.price_elasticity * (1 + perturbation)
    )
    impacts["price_elasticity"] = (
        run_simulation(cfg).summary.mean_profit - base_profit
    )

    # Unit cost sensitivity
    cfg = modified_config(
        unit_cost=base_config.unit_cost * (1 + perturbation)
    )
    impacts["unit_cost"] = (
        run_simulation(cfg).summary.mean_profit - base_profit
    )

    # Fixed cost sensitivity
    cfg = modified_config(
        fixed_cost=base_config.fixed_cost * (1 + perturbation)
    )
    impacts["fixed_cost"] = (
        run_simulation(cfg).summary.mean_profit - base_profit
    )

    return impacts

def rank_assumptions_by_impact(
    base_config: PricingSimulationConfig,
    perturbation: float = 0.1,
) -> List[Tuple[str, float]]:
    """
    Returns assumptions ranked by absolute impact on mean profit.
    """
    impacts = sensitivity_analysis(base_config, perturbation)

    ranked = sorted(
        impacts.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    return ranked
