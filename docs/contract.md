# RiskLens API Contract (Conceptual)

This document defines the **conceptual API contract** for RiskLens.

The API is **not implemented in the MVP**.  
Its purpose is to freeze the **interface boundary** between the decision engine and any future delivery layer (CLI, API service, frontend, batch runner).

---

## Purpose

- Define stable inputs and outputs for the simulation engine
- Prevent interface drift as internal logic evolves
- Enable future wrappers without refactoring core logic
- Make assumptions and uncertainty explicit

This contract is **technology-agnostic**.

---

## Endpoint

### Pricing Simulation

#### simulate_pricing_decision

Runs a Monte Carlo simulation to evaluate a single pricing decision under uncertainty.

---

## Request Contract

### Object: PricingSimulationRequest

All fields are required.  
There are no implicit defaults.

---

### Structure

```text
decision
- price: number

assumptions
- demand_model
  - base_demand: number
  - price_elasticity: number
- cost_model
  - unit_cost: number
  - fixed_cost: number

uncertainty
- demand_noise
  - distribution: string
  - sigma: number
- elasticity_noise
  - distribution: string
  - sigma: number

simulation
- num_runs: integer
- random_seed: integer
```

### Validation Rules

- decision.price > 0
- simulation.num_runs >= 1
- uncertainty.\*.sigma > 0

### Example Request

```json
{
  "decision": {
    "price": 120
  },
  "assumptions": {
    "demand_model": {
      "base_demand": 1000,
      "price_elasticity": -1.3
    },
    "cost_model": {
      "unit_cost": 60,
      "fixed_cost": 20000
    }
  },
  "uncertainty": {
    "demand_noise": {
      "distribution": "lognormal",
      "sigma": 0.25
    },
    "elasticity_noise": {
      "distribution": "normal",
      "sigma": 0.1
    }
  },
  "simulation": {
    "num_runs": 10000,
    "random_seed": 42
  }
}
```

---

## Response Contract

### Object: PricingSimulationResult

### Structure

```text
decision
- price: number

summary_metrics
- expected_profit: number
- profit_std_dev: number
- probability_of_loss: number
- value_at_risk_95: number

distributions
- profit
  - mean: number
  - percentiles: map<number, number>
- demand
  - mean: number
  - percentiles: map<number, number>

metadata
- num_runs: integer
- random_seed: integer
- model_version: string
```

### Example Response

```json
{
  "decision": {
    "price": 120
  },
  "summary_metrics": {
    "expected_profit": 185000,
    "profit_std_dev": 42000,
    "probability_of_loss": 0.08,
    "value_at_risk_95": -25000
  },
  "distributions": {
    "profit": {
      "mean": 185000,
      "percentiles": {
        "5": -25000,
        "50": 180000,
        "95": 260000
      }
    },
    "demand": {
      "mean": 920,
      "percentiles": {
        "5": 600,
        "50": 900,
        "95": 1250
      }
    }
  },
  "metadata": {
    "num_runs": 10000,
    "random_seed": 42,
    "model_version": "v0.1"
  }
}
```

---

## Error Contract

### Error Object

```text
error
code: string
message: string
details: object
```

Error Codes:

- INVALID_INPUT
- MODEL_CONFIG_ERROR
- SIMULATION_ERROR

### Example Error

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "price must be greater than unit_cost",
    "details": {
      "field": "decision.price"
    }
  }
}
```
