from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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


