# Quantum Delivery Route Optimizer

Qiskit Fall Fest 2026 — Industry Challenge I1

A small-scale quantum optimization experiment for delivery route planning using Qiskit and QAOA.

## Problem

A delivery vehicle starts at a warehouse, visits five delivery locations, and returns to the warehouse.

The goal is to find the shortest valid route.

For this project, the locations are:

- Warehouse
- A
- B
- C
- D
- E

The experiment compares:

1. Classical brute-force optimization
2. A QAOA-based quantum optimization approach

## Approach

### Classical baseline

A brute-force solver evaluates all possible permutations of the five delivery locations.

The classical solver finds:

`Warehouse → A → B → C → D → E → Warehouse`

with a total distance of:

**66**

### QUBO formulation

The TSP is formulated as a Quadratic Unconstrained Binary Optimization (QUBO) problem.

The binary variable

`x(i,t)`

represents whether location `i` is visited at position `t`.

The full QUBO formulation contains:

- 25 binary variables
- 10 equality constraints before QUBO conversion

A penalty formulation is used to convert the constrained problem into a QUBO.

### Permutation-space QAOA

A compact permutation-space experiment is also used for the final QAOA benchmark.

There are:

- 5! = 120 valid delivery routes
- 128 computational basis states using 7 qubits

The valid routes are encoded into the 7-qubit state space, while invalid states receive a penalty.

QAOA is then used to sample candidate routes.

## Final Benchmark

The final benchmark was run on a Qiskit Aer simulator.

| Metric | Classical | QAOA |
|---|---:|---:|
| Route distance | 66 | 66 |
| Optimality gap | 0.00% | 0.00% |

The classical brute-force solver found:

Warehouse → A → B → C → D → E → Warehouse

QAOA found the reverse route:

Warehouse → E → D → C → B → A → Warehouse

Because the distance matrix is symmetric, both routes have the same total distance of **66**.

The final QAOA run produced a valid sampling rate of **94.38%**.

Runtime is also recorded in the benchmark CSV, but simulator runtime can vary between runs and should not be interpreted as a measure of quantum advantage.

## Interpretation

The QAOA experiment successfully sampled an optimal delivery route with a **0% optimality gap**.

However, the classical brute-force solver was much faster for this small problem.

Therefore, this experiment does **not** claim quantum advantage.

Instead, it demonstrates how a delivery routing problem can be formulated as a quantum optimization problem and benchmarked fairly against a classical baseline.

## Results


The `results/` directory contains:

- Classical route visualization
- Classical vs QAOA distance comparison
- Classical vs QAOA runtime comparison
- QAOA optimality-gap graph
- Optimized delivery route visualization
- Benchmark CSV

## Project Structure

```text
I1_Delivery_Route_Optimizer/
│
├── src/
│   ├── classical_solver.py
│   ├── data.py
│   ├── graph_builder.py
│   ├── graph_distance.py
│   ├── graph_gap.py
│   ├── graph_runtime.py
│   ├── permutation_qaoa.py
│   ├── quantum_solver.py
│   ├── qubo.py
│   ├── results.py
│   ├── route_visualization.py
│   └── visualization.py
│
├── results/
│   ├── classical_route.png
│   ├── classical_vs_qaoa_distance.png
│   ├── classical_vs_qaoa_runtime.png
│   ├── i1_benchmark.csv
│   ├── optimized_delivery_route.png
│   └── qaoa_optimality_gap.png
│
├── requirements.txt
└── README.md


Save the file and close Notepad.

### Important

This README is specifically for **I1 only**. It does not mention the I7 project.

After saving, run:

```powershell
Get-Content .\I1_Delivery_Route_Optimizer\README.md | Select-Object -First 10
