import random
from typing import List

from .config import PricingSimulationConfig
from .model import (
    PricingDecision,
    PricingParameters,
    PricingOutcome,
    evaluate_pricing_causal_model,
)
from .sampler import DistributionSampler, enforce_valid_sample


def run_monte_carlo(
    config: PricingSimulationConfig,
) -> List[PricingOutcome]:
    # One RNG for full reproducibility
    rng = random.Random(config.random_seed)
    sampler = DistributionSampler(rng)

    # Decision is fixed across runs
    decision = PricingDecision(price=config.price)

    outcomes: List[PricingOutcome] = []

    for _ in range(config.num_runs):
        # Sample uncertainty
        demand_noise = sampler.sample(
            config.demand_noise_distribution,
            config.demand_noise_sigma,
        )
        elasticity_noise = sampler.sample(
            config.elasticity_noise_distribution,
            config.elasticity_noise_sigma,
        )

        # Enforce validity
        demand_noise = enforce_valid_sample(demand_noise)
        elasticity_noise = enforce_valid_sample(elasticity_noise)

        # Perturb parameters (model remains deterministic)
        params = PricingParameters(
            base_demand=config.base_demand * demand_noise,
            price_elasticity=config.price_elasticity * elasticity_noise,
            unit_cost=config.unit_cost,
            fixed_cost=config.fixed_cost,
        )

        outcome = evaluate_pricing_causal_model(decision, params)
        outcomes.append(outcome)

    return outcomes
