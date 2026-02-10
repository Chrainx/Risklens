from typing import List, Dict

from .config import PricingSimulationConfig
from .results import SimulationResult, run_simulation


def compare_pricing_decisions(
    base_config: PricingSimulationConfig,
    prices: List[float],
) -> Dict[float, SimulationResult]:
    """
    Compare multiple pricing decisions under identical uncertainty.
    """
    results: Dict[float, SimulationResult] = {}

    for price in prices:
        # Create a new config with only price changed
        config = PricingSimulationConfig(
            price=price,
            base_demand=base_config.base_demand,
            price_elasticity=base_config.price_elasticity,
            unit_cost=base_config.unit_cost,
            fixed_cost=base_config.fixed_cost,
            demand_noise_distribution=base_config.demand_noise_distribution,
            demand_noise_sigma=base_config.demand_noise_sigma,
            elasticity_noise_distribution=base_config.elasticity_noise_distribution,
            elasticity_noise_sigma=base_config.elasticity_noise_sigma,
            num_runs=base_config.num_runs,
            random_seed=base_config.random_seed,  # SAME seed
        )

        results[price] = run_simulation(config)

    return results
