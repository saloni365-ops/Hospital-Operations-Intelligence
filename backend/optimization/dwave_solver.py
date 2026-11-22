"""Ocean simulated annealing by default, with optional D-Wave token support."""

import os
import time

from backend.optimization.common import AllocationProblem, SolverResult, allocation_cost
from backend.optimization.qubo_builder import build_qubo, decode


class DWaveSolver:
    def solve(self, problem: AllocationProblem) -> SolverResult:
        started = time.perf_counter()
        bqm, labels = build_qubo(problem)
        token = os.getenv("DWAVE_API_TOKEN")
        if token:
            try:
                from dwave.system import LeapHybridSampler
                samples = LeapHybridSampler().sample(bqm, time_limit=3)
                name = "dwave-leap-hybrid"
            except Exception:
                import neal
                samples = neal.SimulatedAnnealingSampler().sample(bqm, num_reads=100, seed=7)
                name = "neal-fallback-no-remote-access"
        else:
            import neal
            samples = neal.SimulatedAnnealingSampler().sample(bqm, num_reads=100, seed=7)
            name = "neal-simulated-annealing"
        allocation = decode(samples.first.sample, problem, labels)
        return SolverResult(allocation, allocation_cost(problem, allocation), sum(allocation.values()) <= problem.nurses_available, (time.perf_counter() - started) * 1000, name)
