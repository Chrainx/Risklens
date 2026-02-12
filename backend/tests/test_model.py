import math
import pytest

from app.simulation.model import (
    PricingDecision,
    PricingParameters,
    evaluate_pricing_causal_model,
)


def test_basic_causal_computation():
    decision = PricingDecision(price=10.0)

    params = PricingParameters(
        base_demand=100.0,
        price_elasticity=0.1,
        unit_cost=3.0,
        fixed_cost=50.0,
    )

    outcome = evaluate_pricing_causal_model(decision, params)

    expected_demand = 100.0 * math.exp(-0.1 * 10.0)
    expected_revenue = 10.0 * expected_demand
    expected_cost = 50.0 + 3.0 * expected_demand
    expected_profit = expected_revenue - expected_cost

    assert math.isclose(outcome.demand, expected_demand)
    assert math.isclose(outcome.revenue, expected_revenue)
    assert math.isclose(outcome.total_cost, expected_cost)
    assert math.isclose(outcome.profit, expected_profit)


def test_zero_or_negative_price_fails():
    decision = PricingDecision(price=0.0)

    params = PricingParameters(
        base_demand=100.0,
        price_elasticity=0.1,
        unit_cost=3.0,
        fixed_cost=50.0,
    )

    with pytest.raises(ValueError):
        evaluate_pricing_causal_model(decision, params)


def test_negative_elasticity_fails():
    decision = PricingDecision(price=10.0)

    params = PricingParameters(
        base_demand=100.0,
        price_elasticity=-0.5,
        unit_cost=3.0,
        fixed_cost=50.0,
    )

    with pytest.raises(ValueError):
        evaluate_pricing_causal_model(decision, params)


def test_deterministic_behavior():
    decision = PricingDecision(price=12.0)

    params = PricingParameters(
        base_demand=150.0,
        price_elasticity=0.2,
        unit_cost=4.0,
        fixed_cost=30.0,
    )

    outcome1 = evaluate_pricing_causal_model(decision, params)
    outcome2 = evaluate_pricing_causal_model(decision, params)

    assert outcome1 == outcome2
