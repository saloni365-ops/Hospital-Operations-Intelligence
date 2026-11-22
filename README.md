# Adaptive Healthcare Operations Intelligence Platform

![Hospital Control Room](results/control-room-1920x1080.png)

A reproducible hospital operations simulator for comparing Predictive AI, QUBO-based Quantum Optimization, and Dynamic Hybrid Intelligence across General Medicine, Cardiology, Orthopedics, and Neurology. The interface combines a Phaser ward floor plan, live controls/event feed, and Plotly operational analytics. This is a research/demo system, not clinical software.

## Requirements

- Python 3.11
- Node.js 20 or newer with npm
- Optional Docker Compose

## Local Development

From the repository root, create and activate a Python virtual environment, then install pinned packages:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm --prefix frontend install
Copy-Item .env.example .env
```

Run the API and frontend in separate terminals:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8001
```

```powershell
npm --prefix frontend run dev
```

The API docs are served at `http://127.0.0.1:8001/docs`; Vite serves the UI at `http://127.0.0.1:5173/control`.

## Features

- Seeded hourly simulation with seasonal arrivals, stochastic length of stay, bed availability, queues, and temporary surge, staffing, bed-closure, and emergency overload events.
- Per-department chronological forecasting with lag/rolling/calendar/disruption features; XGBoost and scikit-learn baseline artifacts are saved under `models/`.
- Shared nurse allocation interface: OR-Tools CP-SAT for Hybrid, local Ocean/neal simulated annealing for the QUBO policy, and a separately callable Qiskit QAOA/Aer solver.
- Browser controls for seed, speed, play/pause, single-step, decision mode, and disruption injection; responsive ward visualization and live operational charts.
- FastAPI endpoints: `/simulation/start`, `/simulation/pause`, `/simulation/reset`, `/simulation/step`, `/simulation/mode`, `/simulation/events`, `/simulation/state`, `/metrics`, `/comparison`, and `/ws/state`.
- Comparison and experiment runs use matched deterministic seeds/scenarios. Measured run outputs are in `results/`; see [results/SUMMARY.md](results/SUMMARY.md).

## Data, Models, Experiments

```powershell
python scripts/generate_synthetic_data.py
python scripts/train_models.py
python scripts/run_experiments.py
python scripts/export_report_figures.py
```

`scripts/fetch_public_data.py` optionally reads a user-provided aggregate CSV URL from `PUBLIC_HEALTH_DATA_URL`; if unavailable or invalid it creates synthetic data. No external dataset is bundled. Synthetic records are not patient data. Experiment outputs describe this simulator only and do not establish clinical validity or quantum advantage.

Run checks with `python -m pytest backend/tests -q`, `npm --prefix frontend test`, and `npm --prefix frontend run build`. The Makefile provides equivalent targets where GNU Make is installed.

## Docker

Copy `.env.example` to `.env`, then run `docker compose up --build`. The frontend is exposed on port 5173 and the API on port 8001.

## Project Status

See [docs/PLAN.md](docs/PLAN.md) for completed phase checks, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for components, [docs/QUBO_FORMULATION.md](docs/QUBO_FORMULATION.md) for the binary model, [docs/EXPERIMENT_DESIGN.md](docs/EXPERIMENT_DESIGN.md) for methodology, and [docs/RESEARCH_PAPER_DRAFT.md](docs/RESEARCH_PAPER_DRAFT.md) for the paper skeleton. Modeling defaults and safety boundaries are recorded in [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md).

## Known Limitations

- The simulation is deliberately simplified and synthetic; nurse coverage heuristics are not clinically validated.
- The API keeps one in-memory simulation per process. Use a single backend worker for local development.
- QUBO optimization covers nurse counts; bed occupancy/queues are simulated separately rather than encoded as per-patient binary decisions.
- Qiskit QAOA is available for small local Aer runs but is not used in the multi-hour comparison because of execution cost. The compared Quantum mode uses local neal annealing by default. D-Wave remote access needs both `DWAVE_API_TOKEN` and the optional `dwave-system` client.
- npm reports dependency audit advisories for the pinned frontend graph. Review `npm audit` before deployment; no forced upgrade was applied because it may break reproducibility.
