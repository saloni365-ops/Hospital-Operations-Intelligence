"""Small QAOA-on-Aer adapter with a disclosed annealing fallback."""

import time

from backend.optimization.common import AllocationProblem, SolverResult, allocation_cost
from backend.optimization.dwave_solver import DWaveSolver
from backend.optimization.qubo_builder import build_qubo, decode


class QiskitSolver:
    def solve(self, problem: AllocationProblem) -> SolverResult:
        started = time.perf_counter()
        try:
            from qiskit.transpiler import generate_preset_pass_manager
            from qiskit_aer import AerSimulator
            from qiskit_aer.primitives import SamplerV2
            from qiskit_algorithms import QAOA
            from qiskit_algorithms.optimizers import COBYLA
            from qiskit_optimization import QuadraticProgram
            from qiskit_optimization.algorithms import MinimumEigenOptimizer
            bqm, labels = build_qubo(problem)
            qp = QuadraticProgram("hospital_allocation")
            for var in bqm.variables:
                qp.binary_var(var)
            linear = {var: float(bqm.get_linear(var)) for var in bqm.variables if bqm.get_linear(var)}
            quadratic = {(u, v): float(bias) for (u, v), bias in bqm.quadratic.items() if bias}
            qp.minimize(linear=linear, quadratic=quadratic, constant=float(bqm.offset))
            backend = AerSimulator()
            sampler = SamplerV2.from_backend(backend, default_shots=512, seed=7)
            pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
            qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=max(12, len(bqm.variables) + 2)), reps=1, transpiler=pass_manager)
            result = MinimumEigenOptimizer(qaoa).solve(qp)
            allocation = decode(dict(zip(result.variables, result.x.astype(int))), problem, labels)
            return SolverResult(allocation, allocation_cost(problem, allocation), sum(allocation.values()) <= problem.nurses_available, (time.perf_counter() - started) * 1000, "qiskit-qaoa-aer")
        except Exception as error:
            result = DWaveSolver().solve(problem)
            result.solver = f"qiskit-fallback[{type(error).__name__}: {error}]:" + result.solver
            result.runtime_ms = (time.perf_counter() - started) * 1000
            return result
