from dataclasses import dataclass
from typing import Literal

class ConfigValidationError(ValueError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(message)

@dataclass(frozen=True)
class PricingSimulationConfig:
    # decision
    price: float

    # demand model
    base_demand: float
    price_elasticity: float

    # cost model
    unit_cost: float
    fixed_cost: float

    # uncertainty
    demand_noise_distribution: Literal["normal", "lognormal"]
    demand_noise_sigma: float

    elasticity_noise_distribution: Literal["normal", "lognormal"]
    elasticity_noise_sigma: float

    # simulation
    num_runs: int
    random_seed: int

    @staticmethod
    def from_request(request: dict) -> "PricingSimulationConfig":
        try:
            price = float(request["decision"]["price"])
        except KeyError:
            raise ConfigValidationError("decision.price", "Missing field")
        except (TypeError, ValueError):
            raise ConfigValidationError("decision.price", "Must be a number")

        if price <= 0:
            raise ConfigValidationError("decision.price", "Must be > 0")
        
        try:
            dm = request["assumptions"]["demand_model"]
            base_demand = float(dm["base_demand"])
            price_elasticity = float(dm["price_elasticity"])
        except KeyError as e:
            raise ConfigValidationError(
                "assumptions.demand_model",
                f"Missing field: {e}"
            )
        except (TypeError, ValueError):
            raise ConfigValidationError(
                "assumptions.demand_model",
                "Invalid numeric value"
            )

        try:
            cm = request["assumptions"]["cost_model"]
            unit_cost = float(cm["unit_cost"])
            fixed_cost = float(cm["fixed_cost"])
        except KeyError as e:
            raise ConfigValidationError(
                "assumptions.cost_model",
                f"Missing field: {e}"
            )
        except (TypeError, ValueError):
            raise ConfigValidationError(
                "assumptions.cost_model",
                "Invalid numeric value"
            )
        
        try:
            un = request["uncertainty"]

            dn = un["demand_noise"]
            demand_noise_distribution = dn["distribution"]
            demand_noise_sigma = float(dn["sigma"])

            en = un["elasticity_noise"]
            elasticity_noise_distribution = en["distribution"]
            elasticity_noise_sigma = float(en["sigma"])
        except KeyError as e:
            raise ConfigValidationError(
                "uncertainty",
                f"Missing field: {e.args[0]}"
            )
        except (TypeError, ValueError):
            raise ConfigValidationError(
                "uncertainty",
                "Invalid numeric value"
            )

        if demand_noise_sigma <= 0:
            raise ConfigValidationError("uncertainty.demand_noise.sigma", "Must be > 0")

        if elasticity_noise_sigma <= 0:
            raise ConfigValidationError("uncertainty.elasticity_noise.sigma", "Must be > 0")
        
        if elasticity_noise_sigma > 0.5:
            raise ConfigValidationError("uncertainty.elasticity_noise.sigma", "Too large; may cause instability")
        
        if demand_noise_distribution not in ("normal", "lognormal"):
            raise ConfigValidationError(
                "uncertainty.demand_noise.distribution",
                "Unsupported distribution"
            )
        
        if elasticity_noise_distribution not in ("normal", "lognormal"):
            raise ConfigValidationError(
                "uncertainty.elasticity_noise.distribution",
                "Unsupported distribution"
            )
        
        try:
            sim = request["simulation"]
            num_runs = int(sim["num_runs"])
            random_seed = int(sim["random_seed"])
        except KeyError as e:
            raise ConfigValidationError(
                "simulation",
                f"Missing field: {e.args[0]}"
            )
        except (TypeError, ValueError):
            raise ConfigValidationError(
                "simulation",
                "Invalid numeric value"
            )


        if num_runs < 1:
            raise ConfigValidationError("simulation.num_runs", "Must be >= 1")
        
        return PricingSimulationConfig(
            price=price,
            base_demand=base_demand,
            price_elasticity=price_elasticity,
            unit_cost=unit_cost,
            fixed_cost=fixed_cost,
            demand_noise_distribution=demand_noise_distribution,
            demand_noise_sigma=demand_noise_sigma,
            elasticity_noise_distribution=elasticity_noise_distribution,
            elasticity_noise_sigma=elasticity_noise_sigma,
            num_runs=num_runs,
            random_seed=random_seed,
        )
