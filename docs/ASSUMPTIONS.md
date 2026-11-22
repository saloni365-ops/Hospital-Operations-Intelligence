# Assumptions

- The simulation clock advances in one-hour increments; a default scenario spans 168 steps (seven days), while API clients may request another bounded horizon.
- The four named departments are independent wards with configurable bed and nurse capacity. A shared, configurable staff/bed pool is allocated by decision mode; patients remain queued if no feasible bed is available.
- Synthetic operations data is the reproducible default and does not represent real patients. The optional public-data fetcher will only use openly accessible, non-identifiable aggregate data and will fall back without blocking development when unavailable.
- Models and experiment outputs are generated locally. No pre-trained model or result is presented as an empirical finding until scripts actually produce it.
- Quantum Optimization means solving a small, explicit binary allocation encoding with quantum or quantum-inspired methods. It is not assumed to outperform the OR-Tools baseline; QAOA may be expensive and a deterministic classical fallback will be disclosed when local execution is unavailable.
- `DWAVE_API_TOKEN` is optional. Without it, the Ocean workflow uses local simulated annealing. No credentials are committed.
- A disruption changes operational availability/demand at the event's start step and duration; hybrid mode may replan after each event and each subsequent step.
- The initial user-facing app is a local research/demo simulator, not a clinical decision-support system. It must not be used for real patient care or staffing decisions.
- Python dependencies target Python 3.11. Frontend and backend run separately in development and can run together through Docker Compose.
