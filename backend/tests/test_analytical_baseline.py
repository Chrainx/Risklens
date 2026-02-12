import math

from app.simulation.model import (
    PricingDecision,
    PricingParameters,
    evaluate_pricing_causal_model,
)


def compute_analytical_optimal_price(unit_cost: float, elasticity: float) -> float:
    """
    Closed-form optimal price for exponential demand:
        Q = Q0 * exp(-k p)

    p* = c + 1/k
    """
    return unit_cost + 1.0 / elasticity


def test_optimal_price_matches_analytical_solution():
    params = PricingParameters(
        base_demand=500.0,
        price_elasticity=0.2,   # k
        unit_cost=5.0,          # c
        fixed_cost=100.0,
    )

    optimal_price = compute_analytical_optimal_price(
        params.unit_cost,
        params.price_elasticity,
    )

    # Evaluate slightly below, at, and above optimal price
    eps = 1e-4

    outcome_below = evaluate_pricing_causal_model(
        PricingDecision(price=optimal_price - eps),
        params,
    )

    outcome_optimal = evaluate_pricing_causal_model(
        PricingDecision(price=optimal_price),
        params,
    )

    outcome_above = evaluate_pricing_causal_model(
        PricingDecision(price=optimal_price + eps),
        params,
    )

    # Profit at optimum should be >= neighboring profits
    assert outcome_optimal.profit >= outcome_below.profit
    assert outcome_optimal.profit >= outcome_above.profit


def test_profit_curvature_near_optimum():
    """
    Ensure second-order behavior: small deviations reduce profit.
    """
    params = PricingParameters(
        base_demand=300.0,
        price_elasticity=0.1,
        unit_cost=2.0,
        fixed_cost=50.0,
    )

    optimal_price = compute_analytical_optimal_price(
        params.unit_cost,
        params.price_elasticity,
    )

    delta = 0.5

    outcome_left = evaluate_pricing_causal_model(
        PricingDecision(price=optimal_price - delta),
        params,
    )

    outcome_optimal = evaluate_pricing_causal_model(
        PricingDecision(price=optimal_price),
        params,
    )

    outcome_right = evaluate_pricing_causal_model(
        PricingDecision(price=optimal_price + delta),
        params,
    )

    assert outcome_optimal.profit > outcome_left.profit
    assert outcome_optimal.profit > outcome_right.profit


def test_analytical_price_is_positive():
    params = PricingParameters(
        base_demand=100.0,
        price_elasticity=0.5,
        unit_cost=1.0,
        fixed_cost=10.0,
    )

    optimal_price = compute_analytical_optimal_price(
        params.unit_cost,
        params.price_elasticity,
    )

    assert optimal_price > 0
    assert math.isfinite(optimal_price)
