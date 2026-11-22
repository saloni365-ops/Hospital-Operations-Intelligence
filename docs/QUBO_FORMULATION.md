# QUBO Formulation

## Decision Variables

For ward $d$ and candidate nurse allocation $k$, define binary $x_{d,k}$. The one-hot constraint selects exactly one allocation for each ward:

$$\sum_{k \in K_d} x_{d,k} = 1.$$

The decoded allocation is $n_d = \sum_{k \in K_d} k x_{d,k}$. Candidate sets are bounded by available shared staff and ward-specific caps, keeping the local annealing problem small.

## Objective and Penalties

Let $f_d$ be forecast admissions plus queued patients and let $t_d = \max(n_{min}, f_d/2)$ be the small-model staffing target. The encoded objective is:

$$E(x) = \sum_d \sum_{k \in K_d} (k-t_d)^2 x_{d,k}
 + A\sum_d\left(\sum_{k \in K_d}x_{d,k}-1\right)^2
 + B\,P\left(\sum_d\sum_{k \in K_d} kx_{d,k} \le N\right).$$

The first term favors staffing near ward demand. $A$ penalizes invalid one-hot ward selections. $B$ and the Ocean inequality slack penalty encode the total nurse budget $N$. The implementation uses `dimod.BinaryQuadraticModel.add_linear_equality_constraint` and `add_linear_inequality_constraint`; these expand the constraints into explicit linear/quadratic biases, including slack bits for the inequality.

The shared post-decoder repairs allocation bounds and nurse budget, then reports feasibility and the same operational objective used by the baseline interface. Solver objective values should be interpreted after repair, not as evidence that the raw sample was feasible.

## Scope and Limitations

This compact encoding optimizes nurse counts only. Bed admissions are handled by the simulator's bed state and queue logic, not by binary per-patient bed assignment variables. The QUBO target is a simplified workload proxy, not a validated clinical staffing rule. The experiment runner's quantum-inspired policy uses neal; `QiskitSolver` separately runs small QAOA instances on Aer. Neither is assumed to outperform OR-Tools. Local `neal` is the default and requires no token. Real D-Wave access is attempted only when `DWAVE_API_TOKEN` is configured and the optional `dwave-system` package is installed; otherwise the explicit fallback is local neal.
