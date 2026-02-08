# RiskLens Architecture (MVP)

This document describes the **high-level architecture** of RiskLens for the MVP phase.

The MVP focuses exclusively on the **decision engine**: a causal, probabilistic simulation that evaluates pricing decisions under uncertainty. No frontend, backend service, or learning system is included at this stage.

---

## Architectural Goals

The architecture is designed to:

- Isolate decision logic from presentation and delivery layers
- Make assumptions explicit and inspectable
- Support reproducible and explainable simulations
- Allow future extension without refactoring core logic

---

## Scope (MVP)

### Included

- Pricing decision simulation
- Causal model with uncertainty
- Monte Carlo execution
- Deterministic, reproducible outputs

### Explicitly Excluded

- Web frontend
- API service
- Machine learning / model training
- Persistent storage
- Authentication or deployment concerns

---

## High-Level Structure

```
risklens/
├── simulation/
│   ├── config.py
│   ├── model.py
│   ├── monte_carlo.py
│   └── run.py
│
├── docs/
│   ├── architecture.md
│   └── api.md
│
└── README.md
```

Each module has a **single responsibility** and no hidden coupling.

---

## Module Responsibilities

### `config.py`

Defines the **world assumptions** for the simulation.

Responsibilities:

- Baseline business constants
- Distribution parameters for uncertainty
- Simulation horizon and limits

Non-responsibilities:

- No random sampling
- No business logic
- No side effects

---

### `model.py`

Encodes the **causal relationships** between variables.

Responsibilities:

- Price → demand transformation
- Demand → revenue calculation
- Cost → margin calculation
- Margin / demand → retention dynamics (lagged)

Non-responsibilities:

- No looping
- No aggregation
- No randomness

---

### `monte_carlo.py`

Executes the simulation under uncertainty.

Responsibilities:

- Sampling from distributions
- Repeated simulation runs
- Aggregation of outcomes
- Percentiles and risk metrics

Non-responsibilities:

- No causal logic
- No configuration definition
- No I/O or visualization

---

### `run.py`

Provides a simple **local execution entry point**.

Responsibilities:

- Accepting scenario inputs
- Triggering simulation runs
- Printing or exporting results

This is intended for:

- development
- testing
- validation of assumptions

---

## Data Flow

1. A pricing scenario is defined (e.g. +0%, +5%, +10%)
2. `config.py` provides constants and distribution parameters
3. `monte_carlo.py` samples uncertainty variables
4. For each sample:
   - `model.py` computes outcomes
5. Results are aggregated into distributions and summary statistics

There are **no feedback loops** in the MVP.

---

## Design Principles

- **Explicit over implicit:** all assumptions are visible in code or docs
- **Deterministic structure:** randomness is isolated and controlled
- **Explainability first:** every output maps to a causal path
- **Minimal surface area:** no premature abstractions

---

## Future Extensions (Non-Binding)

The architecture intentionally allows future additions such as:

- API wrapper around the simulation engine
- Frontend visualization layer
- Learned parameter distributions
- Scenario comparison dashboards

These extensions should wrap the existing modules without modifying their core responsibilities.

---

## Summary

The RiskLens MVP architecture prioritizes **clarity, correctness, and extensibility** over completeness. By focusing on the decision engine first, the system establishes a reliable foundation for future productization.
