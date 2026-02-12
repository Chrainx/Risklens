import math

from app.simulation.model import (
    evaluate_pricing_causal_model,
    PricingDecision,
    PricingParameters,
)
from app.simulation.config import PricingSimulationConfig
from app.simulation.model import evaluate_from_config


def test_same_inputs_produce_identical_outputs():
    decision = PricingDecision(price=15.0)

    params = PricingParameters(
        base_demand=200.0,
        price_elasticity=0.15,
        unit_cost=5.0,
        fixed_cost=40.0,
    )

    outcome1 = evaluate_pricing_causal_model(decision, params)
    outcome2 = evaluate_pricing_causal_model(decision, params)

    assert outcome1 == outcome2


def test_config_wrapper_reproducibility():
    config = PricingSimulationConfig(
        price=20.0,
        base_demand=120.0,
        price_elasticity=0.12,
        unit_cost=4.0,
        fixed_cost=60.0,
        demand_noise_distribution="normal",
        demand_noise_sigma=0.0,
        elasticity_noise_distribution="normal",
        elasticity_noise_sigma=0.0,
        num_runs=1,
        random_seed=42,
    )

    outcome1 = evaluate_from_config(config)
    outcome2 = evaluate_from_config(config)

    assert outcome1 == outcome2


def test_numerical_stability_large_price():
    decision = PricingDecision(price=1000.0)

    params = PricingParameters(
        base_demand=100.0,
        price_elasticity=0.01,
        unit_cost=2.0,
        fixed_cost=10.0,
    )

    outcome = evaluate_pricing_causal_model(decision, params)

    assert math.isfinite(outcome.demand)
    assert math.isfinite(outcome.revenue)
    assert math.isfinite(outcome.total_cost)
    assert math.isfinite(outcome.profit)


def test_repeated_calls_do_not_mutate_state():
    decision = PricingDecision(price=8.0)

    params = PricingParameters(
        base_demand=90.0,
        price_elasticity=0.25,
        unit_cost=3.0,
        fixed_cost=25.0,
    )

    outcomes = [
        evaluate_pricing_causal_model(decision, params)
        for _ in range(10)
    ]

    for o in outcomes[1:]:
        assert o == outcomes[0]
