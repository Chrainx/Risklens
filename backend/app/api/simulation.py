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


@router.post("/simulate", response_model=SimulationResponse)

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

