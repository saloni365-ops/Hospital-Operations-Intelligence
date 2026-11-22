# Architecture

## Runtime Flow

```text
React control room
  | REST controls / polling
  v
FastAPI routes ---- WebSocket /ws/state
  |
  +-- HospitalSimulation (seeded hourly arrivals, LOS, beds, queues, events)
  +-- Predictive allocation (calendar and recent ward arrivals)
  +-- Hybrid: OR-Tools CP-SAT allocation
  +-- Quantum mode: explicit QUBO + Ocean neal simulated annealing
  `-- Optional Qiskit QAOA/Aer adapter with a clearly named neal fallback
          |
          +-- Phaser generated-shape floor map
          `-- Plotly time series and matched scenario comparison
```

## Boundaries

- `backend/simulation/engine.py` owns clock progression, seeded randomness, patient LOS, resource state, events, and step metrics.
- `backend/predictive/forecaster.py` owns causal features, chronological train/test split, per-department model persistence, and forecast metrics.
- `backend/optimization/` owns the shared allocation contract, repair logic, OR-Tools baseline, QUBO encoding, Ocean annealing, and Qiskit adapter.
- `backend/api/routes.py` owns stateful local-demo controls, metric aggregation, matched comparisons, and WebSocket broadcasts.
- `frontend/src/api/` contains the typed API contract; Phaser and Plotly consume the same simulation response.
- `scripts/` provides deterministic data generation, optional external CSV ingestion, model training, and repeatable experiments.

The API currently stores one in-memory simulation per process. Use a single worker for local runs; persistence, multi-user isolation, and production authentication are outside this research demo.

## Decision Modes

- Predictive AI distributes a fixed staff pool greedily using per-ward expected admissions.
- Quantum Optimization comparison solves the small one-hot allocation QUBO with local Ocean/neal by default. This is quantum-inspired simulated annealing, not a quantum hardware run. `QiskitSolver` separately executes a small QAOA circuit on local Aer for direct solver experiments; it is not used in the multi-hour mode comparison to keep the matched experiment tractable.
- Dynamic Hybrid Intelligence uses OR-Tools CP-SAT with demand forecasts and queue pressure and replans every step, including after events.

The Qiskit QAOA adapter uses Aer SamplerV2 and a preset transpiler. If the optional Qiskit stack raises at runtime, its result names the fallback to neal. This adapter is not used to produce the baseline comparison numbers.
