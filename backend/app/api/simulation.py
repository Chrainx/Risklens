from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import math

from app.simulation.config import PricingSimulationConfig, ConfigValidationError
from app.simulation.results import run_simulation

router = APIRouter()

Dist = Literal["normal", "lognormal"]


# ==============================
# /simulate  (atomic evaluation)
# ==============================

class SimulateRequest(BaseModel):
    # decision
    price: float = Field(gt=0)

    # assumptions
    base_demand: float
    price_elasticity: float
    unit_cost: float
    fixed_cost: float

    # uncertainty (NOTE: your config requires sigma > 0)
    demand_noise_distribution: Dist = "normal"
    demand_noise_sigma: float = Field(gt=0)

    elasticity_noise_distribution: Dist = "normal"
    elasticity_noise_sigma: float = Field(gt=0)

    # simulation
    num_runs: int = Field(default=1000, ge=1)
    random_seed: int = 0


class SimulateResponse(BaseModel):
    profits: List[float]
    mean_profit: float
    std_profit: float
    prob_loss: float


@router.post("/simulate", response_model=SimulateResponse)
async def simulate(req: SimulateRequest) -> SimulateResponse:
    payload = {
        "decision": {"price": req.price},
        "assumptions": {
            "demand_model": {
                "base_demand": req.base_demand,
                "price_elasticity": req.price_elasticity,
            },
            "cost_model": {
                "unit_cost": req.unit_cost,
                "fixed_cost": req.fixed_cost,
            },
        },
        "uncertainty": {
            "demand_noise": {
                "distribution": req.demand_noise_distribution,
                "sigma": req.demand_noise_sigma,
            },
            "elasticity_noise": {
                "distribution": req.elasticity_noise_distribution,
                "sigma": req.elasticity_noise_sigma,
            },
        },
        "simulation": {
            "num_runs": req.num_runs,
            "random_seed": req.random_seed,
        },
    }

    try:
        config = PricingSimulationConfig.from_request(payload)
    except ConfigValidationError as e:
        raise HTTPException(status_code=400, detail={"field": e.field, "message": str(e)})

    result = run_simulation(config)
    profits = [o.profit for o in result.outcomes]

    mean_profit = result.summary.mean_profit
    std_profit = math.sqrt(result.summary.profit_variance)

    prob_loss = sum(1 for p in profits if p < 0) / len(profits)

    return SimulateResponse(
        profits=profits,
        mean_profit=mean_profit,
        std_profit=std_profit,
        prob_loss=prob_loss,
    )


# =================================
# /simulate-range (search/optimize)
# =================================

class SimulateRangeRequest(BaseModel):
    # assumptions
    base_demand: float
    price_elasticity: float
    unit_cost: float
    fixed_cost: float

    # price search
    min_price: float = Field(gt=0)
    max_price: float = Field(gt=0)
    step: float = Field(gt=0)

    # uncertainty (same constraints as config: sigma > 0)
    demand_noise_distribution: Dist = "normal"
    demand_noise_sigma: float = Field(gt=0)

    elasticity_noise_distribution: Dist = "normal"
    elasticity_noise_sigma: float = Field(gt=0)

    # simulation (applied per price)
    num_runs: int = Field(default=500, ge=1)
    random_seed: int = 0


class PricePoint(BaseModel):
    price: float
    mean_profit: float
    std_profit: float
    prob_loss: float


class SimulateRangeResponse(BaseModel):
    curve: List[PricePoint]
    optimal_price: float
    max_mean_profit: float


@router.post("/simulate-range", response_model=SimulateRangeResponse)
async def simulate_range(req: SimulateRangeRequest) -> SimulateRangeResponse:
    if req.max_price < req.min_price:
        raise HTTPException(status_code=400, detail={"field": "max_price", "message": "Must be >= min_price"})

    curve: List[PricePoint] = []

    # avoid float drift by iterating with k
    span = req.max_price - req.min_price
    n_steps = int(span / req.step) + 1  # inclusive-ish
    # safety cap to prevent accidental huge loops
    if n_steps > 5000:
        raise HTTPException(status_code=400, detail={"field": "step", "message": "Too many points (cap 5000). Increase step."})

    for k in range(n_steps + 2):
        price = req.min_price + k * req.step
        if price > req.max_price + 1e-12:
            break

        payload = {
            "decision": {"price": float(price)},
            "assumptions": {
                "demand_model": {
                    "base_demand": req.base_demand,
                    "price_elasticity": req.price_elasticity,
                },
                "cost_model": {
                    "unit_cost": req.unit_cost,
                    "fixed_cost": req.fixed_cost,
                },
            },
            "uncertainty": {
                "demand_noise": {
                    "distribution": req.demand_noise_distribution,
                    "sigma": req.demand_noise_sigma,
                },
                "elasticity_noise": {
                    "distribution": req.elasticity_noise_distribution,
                    "sigma": req.elasticity_noise_sigma,
                },
            },
            "simulation": {
                "num_runs": req.num_runs,
                "random_seed": req.random_seed,
            },
        }

        try:
            config = PricingSimulationConfig.from_request(payload)
        except ConfigValidationError as e:
            raise HTTPException(status_code=400, detail={"field": e.field, "message": str(e)})

        result = run_simulation(config)
        profits = [o.profit for o in result.outcomes]

        mean_profit = result.summary.mean_profit
        std_profit = math.sqrt(result.summary.profit_variance)
        prob_loss = sum(1 for p in profits if p < 0) / len(profits)

        curve.append(
            PricePoint(
                price=float(price),
                mean_profit=float(mean_profit),
                std_profit=float(std_profit),
                prob_loss=float(prob_loss),
            )
        )

    if not curve:
        raise HTTPException(status_code=400, detail={"message": "Price range produced no results."})

    optimal = max(curve, key=lambda p: p.mean_profit)

    return SimulateRangeResponse(
        curve=curve,
        optimal_price=optimal.price,
        max_mean_profit=optimal.mean_profit,
    )