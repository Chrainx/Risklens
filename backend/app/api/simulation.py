from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np


from app.simulation.model import (
    PricingDecision,
    PricingParameters,
    evaluate_pricing_causal_model,
)

router = APIRouter()


class SimulationRequest(BaseModel):
    price: float
    base_demand: float
    price_elasticity: float
    unit_cost: float
    fixed_cost: float


class SimulationResponse(BaseModel):
    demand: float
    revenue: float
    total_cost: float
    profit: float

class RangeSimulationRequest(BaseModel):
    base_demand: float
    price_elasticity: float
    unit_cost: float
    fixed_cost: float
    min_price: float
    max_price: float
    step: float


class PricePoint(BaseModel):
    price: float
    profit: float


class RangeSimulationResponse(BaseModel):
    curve: list[PricePoint]
    optimal_price: float
    max_profit: float

class MonteCarloRequest(BaseModel):
    price: float
    base_demand: float
    elasticity_mean: float
    elasticity_sigma: float
    unit_cost: float
    fixed_cost: float
    num_runs: int


class MonteCarloResponse(BaseModel):
    profits: list[float]
    mean_profit: float
    std_profit: float
    prob_loss: float



@router.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest):
    try:
        decision = PricingDecision(price=req.price)

        params = PricingParameters(
            base_demand=req.base_demand,
            price_elasticity=req.price_elasticity,
            unit_cost=req.unit_cost,
            fixed_cost=req.fixed_cost,
        )

        outcome = evaluate_pricing_causal_model(decision, params)

        return SimulationResponse(
            demand=outcome.demand,
            revenue=outcome.revenue,
            total_cost=outcome.total_cost,
            profit=outcome.profit,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/simulate-range", response_model=RangeSimulationResponse)
def simulate_range(req: RangeSimulationRequest):
    try:
        params = PricingParameters(
            base_demand=req.base_demand,
            price_elasticity=req.price_elasticity,
            unit_cost=req.unit_cost,
            fixed_cost=req.fixed_cost,
        )

        curve = []
        price = req.min_price

        while price <= req.max_price:
            decision = PricingDecision(price=price)
            outcome = evaluate_pricing_causal_model(decision, params)

            curve.append(
                PricePoint(
                    price=price,
                    profit=outcome.profit,
                )
            )

            price += req.step

        if not curve:
            raise ValueError("Price range produced no results.")

        optimal = max(curve, key=lambda p: p.profit)

        return RangeSimulationResponse(
            curve=curve,
            optimal_price=optimal.price,
            max_profit=optimal.profit,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simulate-monte-carlo", response_model=MonteCarloResponse)
def simulate_monte_carlo(req: MonteCarloRequest):
    try:
        if req.num_runs <= 0:
            raise ValueError("num_runs must be positive.")

        profits = []

        for _ in range(req.num_runs):
            while True:
                sampled_elasticity = np.random.normal(
                    req.elasticity_mean,
                    req.elasticity_sigma
                )
                if sampled_elasticity > 0:
                    break

            params = PricingParameters(
                base_demand=req.base_demand,
                price_elasticity=sampled_elasticity,
                unit_cost=req.unit_cost,
                fixed_cost=req.fixed_cost,
            )

            decision = PricingDecision(price=req.price)
            outcome = evaluate_pricing_causal_model(decision, params)

            profits.append(outcome.profit)

        profits_array = np.array(profits)

        mean_profit = float(np.mean(profits_array))
        std_profit = float(np.std(profits_array))
        prob_loss = float(np.mean(profits_array < 0))

        return MonteCarloResponse(
            profits=profits,
            mean_profit=mean_profit,
            std_profit=std_profit,
            prob_loss=prob_loss,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))