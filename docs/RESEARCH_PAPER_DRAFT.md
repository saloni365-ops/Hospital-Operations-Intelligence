# Adaptive Healthcare Operations Intelligence Platform Using Predictive AI and Quantum Optimization

## Abstract

Draft. This work presents a reproducible synthetic hospital operations simulator for comparing demand-informed staffing policies, classical constrained allocation, and a QUBO-based quantum-inspired allocation. Quantitative claims will be inserted only from committed experiment outputs. This prototype is not a clinical decision-support system.

## 1. Introduction

Hospitals must balance uncertain admissions against finite beds and staffing. This project studies the engineering workflow for evaluating predictive, classical optimization, and quantum-inspired allocation policies under matched simulated demand and injected disruptions.

## 2. Related Work

Placeholder: review hospital demand forecasting, nurse rostering, OR-Tools constraint programming, QUBO encodings, quantum approximate optimization, and quantum-inspired annealing. Add verified citations during research review; none are asserted in this prototype draft.

## 3. Methodology

Four simulated departments receive seeded hourly admissions with daily/weekly seasonality, noise, length-of-stay variation, bed closures, staffing shortages, and surge events. Predictive features include calendar values, causal lags, rolling means, and disruption markers. Allocation modes share the same nurse budget and deterministic arrival sequence. The QUBO selects a small candidate nurse count per ward with one-hot and budget penalties; OR-Tools CP-SAT is the classical baseline.

## 4. Experiments

Matched seeds are `11`, `23`, and `42`, with a 30% admissions surge at hour 24. Primary outcomes are cumulative unmet demand, average utilization, workload-balance standard deviation, and solver wall-clock time. See `docs/EXPERIMENT_DESIGN.md` for protocol details.

## 5. Results

To be generated from actual runs in `results/SUMMARY.md` and `results/mode_comparison.csv`. No values are pre-populated here.

## 6. Limitations

Admissions and length-of-stay distributions are synthetic, capacity and staffing policies are simplified, and staffing proxies are not clinically validated. The experiments are small and do not establish external validity or quantum advantage. API state is in-memory and single-process. The Qiskit Aer path may fall back to local neal if the pinned primitive stack cannot execute the encoded circuit.

## 7. Conclusion

Placeholder: summarize measured simulator findings, discuss trade-offs relative to OR-Tools, and outline future work only after experiment runs and model review.