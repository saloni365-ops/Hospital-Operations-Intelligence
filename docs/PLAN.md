# Project Plan

## Phased Checklist

- [x] **Phase 1: Scaffolding, environment, dependencies, config**
  - Establish the backend, frontend, data, model, experiment, docs, and script directories.
  - Pin Python and JavaScript dependencies; add environment examples, Docker files, Makefile, and starter application configuration.
  - Record assumptions and run dependency/configuration checks.
- [x] **Phase 2: Synthetic data and simulation engine**
  - Generate deterministic seasonal department admissions and reusable scenario data.
  - Implement the hourly hospital state machine, queues, bed states, staffing, disruptions, metrics, and scenario scripts.
  - Add focused engine and synthetic-data tests.
- [x] **Phase 3: Predictive models**
  - Implement lag, rolling, calendar, and disruption features with time-based validation.
  - Train per-department scikit-learn and XGBoost models; persist artifacts and expose horizon predictions.
  - Test training, inference, and reported metrics.
- [x] **Phase 4: Optimization solvers**
  - Define the shared bed and nurse allocation problem and classical OR-Tools baseline.
  - Build and document an explicit QUBO with a decoder and feasibility repair.
  - Add Qiskit/Aer QAOA and Ocean/neal solvers with optional token-based D-Wave selection and honest fallback behavior.
  - Test objective consistency, feasibility, and common solver results.
- [x] **Phase 5: Decision modes and comparison runner**
  - Wire Predictive AI, Quantum Optimization, and Dynamic Hybrid Intelligence into simulation control.
  - Re-run identical seeded scenarios for fair mode comparisons.
  - Test deterministic behavior and disruption-triggered hybrid re-optimization.
- [x] **Phase 6: FastAPI backend**
  - Implement simulation controls, mode selection, event injection, metrics, comparison, and live WebSocket state.
  - Add API and WebSocket tests; verify generated OpenAPI docs.
- [x] **Phase 7: Frontend experience**
  - Build the responsive Phaser hospital map, controls, alerts/event log, and typed API client.
  - Add Plotly operational analytics and mode comparison views.
  - Run frontend tests, lint/type checks, and production build.
- [x] **Phase 8: Experiments, results, documentation, and polish**
  - Run multi-seed disruption experiments and save actual CSV/figure outputs and an evidence-based summary.
  - Complete architecture, QUBO, experiment, assumptions, and research draft documentation.
  - Polish the README and developer commands; verify documented limitations and fallbacks.

## Planned File Tree

```text
hospital-ai-platform/
|-- backend/
|   |-- app/
|   |-- simulation/
|   |-- predictive/
|   |-- optimization/
|   |-- api/
|   `-- tests/
|-- frontend/
|   `-- src/
|       |-- game/
|       |-- components/
|       |-- charts/
|       `-- api/
|-- data/synthetic/
|-- models/
|-- results/
|-- scripts/
|-- docs/
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- Makefile
|-- README.md
|-- requirements.txt
`-- frontend/package.json
```

The checklist is intentionally ordered; later phases will be checked off only after their focused tests or build checks pass. Experimental outcomes will be generated from runs, never pre-filled as claimed results.

## Final Validation

- Backend: `python -m pytest backend/tests -q` passed 9 tests, including WebSocket delivery, solver feasibility, and a local Qiskit Aer QAOA solve.
- Frontend: `npm --prefix frontend test` passed 1 test; `npm --prefix frontend run build` completed successfully.
- Live checks: Vite and FastAPI started; browser Run advanced simulation hours, hybrid surge injection logged staff transfers, `/docs` loaded, and `/comparison` returned numeric results for all three modes.
- Experiments: `scripts/run_experiments.py` generated CSV, Plotly HTML, and `results/SUMMARY.md` from three seeds over 72 hours.
- Limitations: QAOA is not used by the longer experiment comparison due to runtime. The compared quantum-inspired mode uses neal; no quantum advantage or clinical claim is made. npm reported audit advisories for the pinned dependency tree.
