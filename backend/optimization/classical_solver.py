"""OR-Tools CP-SAT allocation baseline."""

import time

from ortools.sat.python import cp_model

from backend.optimization.common import AllocationProblem, SolverResult, allocation_cost, repair


class ClassicalSolver:
    def solve(self, problem: AllocationProblem) -> SolverResult:
        started = time.perf_counter()
        model = cp_model.CpModel()
        variables = {d: model.new_int_var(problem.minimum_coverage, problem.nurses_by_department[d], f"n_{i}") for i, d in enumerate(problem.departments)}
        model.add(sum(variables.values()) <= problem.nurses_available)
        costs = []
        for dept in problem.departments:
            target = max(problem.minimum_coverage, round(problem.demand[dept] / 2))
            deviation = model.new_int_var(0, 1000, f"shortage_{dept}")
            model.add(deviation >= target - variables[dept])
            costs.append(deviation * 100)
        model.minimize(sum(costs))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 1.0
        status = solver.solve(model)
        allocation = {d: solver.value(variables[d]) for d in problem.departments} if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else {d: problem.minimum_coverage for d in problem.departments}
        allocation = repair(problem, allocation)
        return SolverResult(allocation, allocation_cost(problem, allocation), sum(allocation.values()) <= problem.nurses_available, (time.perf_counter() - started) * 1000, "ortools-cp-sat")
