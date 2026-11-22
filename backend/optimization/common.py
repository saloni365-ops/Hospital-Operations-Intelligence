"""Shared allocation problem and solver result contract."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class AllocationProblem:
    departments: list[str]
    demand: dict[str, float]
    beds: dict[str, int]
    nurses_available: int
    nurses_by_department: dict[str, int]
    minimum_coverage: int = 1


@dataclass
class SolverResult:
    allocation: dict[str, int]
    objective: float
    feasible: bool
    runtime_ms: float
    solver: str


class AllocationSolver(Protocol):
    def solve(self, problem: AllocationProblem) -> SolverResult: ...


def allocation_cost(problem: AllocationProblem, allocation: dict[str, int]) -> float:
    """Penalize unmet nurse demand and uneven patients-per-nurse workload."""
    workloads = [problem.demand[d] / max(1, allocation[d]) for d in problem.departments]
    mean = sum(workloads) / len(workloads)
    balance = sum((value - mean) ** 2 for value in workloads) / len(workloads)
    shortage = sum(max(0.0, problem.demand[d] - allocation[d] * 2.0) ** 2 for d in problem.departments)
    return shortage + 0.15 * balance


def repair(problem: AllocationProblem, allocation: dict[str, int]) -> dict[str, int]:
    result = {d: min(problem.nurses_by_department[d], max(problem.minimum_coverage, allocation.get(d, 0))) for d in problem.departments}
    while sum(result.values()) > problem.nurses_available:
        candidates = [d for d in problem.departments if result[d] > problem.minimum_coverage]
        if not candidates:
            break
        result[max(candidates, key=lambda d: result[d] / max(problem.demand[d], 0.1))] -= 1
    while sum(result.values()) < problem.nurses_available:
        candidates = [d for d in problem.departments if result[d] < problem.nurses_by_department[d]]
        if not candidates:
            break
        chosen = max(candidates, key=lambda d: problem.demand[d] / result[d])
        result[chosen] += 1
    return result
