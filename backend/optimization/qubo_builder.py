"""Explicit one-hot nurse-allocation QUBO with coverage and budget penalties."""

from dimod import BinaryQuadraticModel, BINARY

from backend.optimization.common import AllocationProblem, allocation_cost, repair


def build_qubo(problem: AllocationProblem) -> tuple[BinaryQuadraticModel, dict[tuple[str, int], str]]:
    """Encode each ward's nurse count as one-hot bits and add a budget penalty.

    The objective rewards allocations near demand/2. One-hot penalties enforce one
    count per ward; a quadratic budget penalty discourages exceeding the pool.
    """
    bqm = BinaryQuadraticModel({}, {}, 0.0, BINARY)
    labels: dict[tuple[str, int], str] = {}
    penalty = 40.0
    for dept in problem.departments:
        options = range(problem.minimum_coverage, problem.nurses_by_department[dept] + 1)
        names = []
        target = max(problem.minimum_coverage, problem.demand[dept] / 2)
        for count in options:
            name = f"{dept}:{count}"
            labels[(dept, count)] = name
            names.append(name)
            bqm.add_variable(name, (count - target) ** 2)
        bqm.add_linear_equality_constraint([(name, 1) for name in names], lagrange_multiplier=penalty, constant=-1)
    terms = [(name, count) for (dept, count), name in labels.items()]
    bqm.add_linear_inequality_constraint(terms, lagrange_multiplier=penalty, label="nurse-budget", constant=0, lb=0, ub=problem.nurses_available)
    return bqm, labels


def decode(sample: dict[str, int], problem: AllocationProblem, labels: dict[tuple[str, int], str]) -> dict[str, int]:
    allocation = {}
    for dept in problem.departments:
        chosen = [count for (ward, count), bit in labels.items() if ward == dept and sample.get(bit, 0) > 0]
        allocation[dept] = chosen[0] if chosen else problem.minimum_coverage
    return repair(problem, allocation)
