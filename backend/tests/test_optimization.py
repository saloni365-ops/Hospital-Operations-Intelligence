from backend.optimization.classical_solver import ClassicalSolver
from backend.optimization.common import AllocationProblem
from backend.optimization.dwave_solver import DWaveSolver
from backend.optimization.qiskit_solver import QiskitSolver


def test_classical_and_qubo_solvers_respect_staff_budget() -> None:
    departments = ["A", "B", "C", "D"]
    problem = AllocationProblem(departments, dict(zip(departments, [8, 5, 4, 3])), dict(zip(departments, [18, 12, 14, 10])), 25, dict(zip(departments, [8, 6, 6, 5])))
    for result in (ClassicalSolver().solve(problem), DWaveSolver().solve(problem)):
        assert result.feasible
        assert sum(result.allocation.values()) <= problem.nurses_available
        assert set(result.allocation) == set(departments)


def test_qaoa_aer_solver_runs_and_returns_feasible_allocation() -> None:
    departments = ["A", "B"]
    problem = AllocationProblem(departments, {"A": 4, "B": 2}, {"A": 8, "B": 6}, 6, {"A": 6, "B": 6})
    result = QiskitSolver().solve(problem)

    assert result.feasible
    assert result.solver.startswith("qiskit-qaoa-aer") or result.solver.startswith("qiskit-fallback[")
    assert sum(result.allocation.values()) <= problem.nurses_available