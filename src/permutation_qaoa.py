import itertools
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from data import LOCATIONS, DISTANCE_MATRIX


SHOTS = 500

GAMMA_VALUES = [0.2, 0.5, 1.0]
BETA_VALUES = [0.2, 0.5, 1.0]


def generate_routes():
    """
    Generate every possible ordering of the 5 delivery cities.

    There are:

        5! = 120

    possible delivery routes.
    """

    cities = list(range(1, len(LOCATIONS)))

    routes = []

    for permutation in itertools.permutations(cities):

        route = (
            0,
            *permutation,
            0,
        )

        routes.append(route)

    return routes


def route_distance(route):
    """Calculate total route distance."""

    distance = 0

    for i in range(len(route) - 1):

        distance += DISTANCE_MATRIX[
            route[i],
            route[i + 1],
        ]

    return distance


def build_route_costs(routes):
    """Calculate the cost of every possible route."""

    return np.array([
        route_distance(route)
        for route in routes
    ])


def build_cost_operator(costs):
    """
    Convert route costs into diagonal phase coefficients.

    We use 7 qubits because:

        2^7 = 128

    while we have only 120 valid routes.

    The final 8 states are treated as invalid.
    """

    num_qubits = 7

    dimension = 2 ** num_qubits

    diagonal = np.zeros(dimension)

    for index, cost in enumerate(costs):

        diagonal[index] = cost

    # Invalid states receive a large penalty.
    penalty = max(costs) + 100

    for index in range(len(costs), dimension):

        diagonal[index] = penalty

    return diagonal


def build_qaoa_circuit(costs, gamma, beta):
    """
    Build a compact permutation-space QAOA circuit.

    This is deliberately separate from the 25-variable
    QUBO experiment.

    The route cost is encoded directly in the diagonal
    cost operator.
    """

    num_qubits = 7

    qc = QuantumCircuit(
        num_qubits,
        num_qubits,
    )

    # ---------------------------------------------------------
    # Initial equal superposition
    # ---------------------------------------------------------

    qc.h(range(num_qubits))

    # ---------------------------------------------------------
    # Cost layer
    # ---------------------------------------------------------

    diagonal = build_cost_operator(costs)

    # Qiskit Aer allows us to implement the diagonal
    # cost operator through a phase oracle.
    #
    # For this first experiment we use a diagonal unitary.
    #
    phases = np.exp(
        -1j * gamma * diagonal
    )

    cost_operator = np.diag(phases)

    qc.unitary(
        cost_operator,
        list(range(num_qubits)),
        label="Cost",
    )

    # ---------------------------------------------------------
    # Standard mixer
    # ---------------------------------------------------------

    for qubit in range(num_qubits):

        qc.rx(
            2 * beta,
            qubit,
        )

    # ---------------------------------------------------------
    # Measurement
    # ---------------------------------------------------------

    qc.measure(
        range(num_qubits),
        range(num_qubits),
    )

    return qc


def decode_route(index, routes):
    """
    Convert a measured integer into a route.

    States 0-119 are valid.
    States 120-127 are invalid.
    """

    if index >= len(routes):
        return None

    return routes[index]


def run_experiment(routes, costs, gamma, beta):

    circuit = build_qaoa_circuit(
        costs,
        gamma,
        beta,
    )

    simulator = AerSimulator()

    compiled = transpile(
        circuit,
        simulator,
    )

    result = simulator.run(
        compiled,
        shots=SHOTS,
    ).result()

    counts = result.get_counts()

    valid_routes = []

    for bitstring, count in counts.items():

        # Convert binary measurement to integer.
        index = int(
            bitstring,
            2,
        )

        route = decode_route(
            index,
            routes,
        )

        if route is not None:

            distance = route_distance(
                route
            )

            valid_routes.append(
                (
                    distance,
                    count,
                    route,
                )
            )

    return counts, valid_routes


def main():

    print("Generating TSP permutation space...")

    routes = generate_routes()

    print(
        f"Number of valid routes: {len(routes)}"
    )

    print(
        f"Quantum states available: {2 ** 7}"
    )

    costs = build_route_costs(routes)

    classical_best_index = np.argmin(
        costs
    )

    classical_best_route = routes[
        classical_best_index
    ]

    classical_best_distance = costs[
        classical_best_index
    ]

    print("\nClassical optimum:")
    print(
        " → ".join(
            LOCATIONS[i]
            for i in classical_best_route
        )
    )

    print(
        f"Distance: {classical_best_distance}"
    )

    print("\nRunning QAOA parameter scan...")
    print(
        f"Shots per experiment: {SHOTS}"
    )

    best_result = None

    experiment_number = 0

    total_experiments = (
        len(GAMMA_VALUES)
        * len(BETA_VALUES)
    )

    for gamma in GAMMA_VALUES:

        for beta in BETA_VALUES:

            experiment_number += 1

            print(
                f"\nExperiment "
                f"{experiment_number}/"
                f"{total_experiments}"
            )

            print(
                f"gamma={gamma}, "
                f"beta={beta}"
            )

            counts, valid_routes = (
                run_experiment(
                    routes,
                    costs,
                    gamma,
                    beta,
                )
            )

            print(
                f"Unique states: {len(counts)}"
            )

            print(
                f"Valid routes: "
                f"{len(valid_routes)}"
            )

            if valid_routes:

                valid_routes.sort(
                    key=lambda x: x[0]
                )

                candidate = (
                    valid_routes[0]
                )

                if (
                    best_result is None
                    or candidate[0]
                    < best_result[0]
                ):

                    best_result = (
                        candidate[0],
                        candidate[1],
                        candidate[2],
                        gamma,
                        beta,
                    )

    print("\n")
    print("=" * 55)
    print("PERMUTATION-SPACE QAOA RESULT")
    print("=" * 55)

    if best_result is None:

        print(
            "\nNo valid route sampled."
        )

        return

    (
        best_distance,
        best_count,
        best_route,
        best_gamma,
        best_beta,
    ) = best_result

    print("\nBest QAOA route:")

    print(
        " → ".join(
            LOCATIONS[i]
            for i in best_route
        )
    )

    print(
        f"\nQAOA distance: {best_distance}"
    )

    print(
        f"Samples: {best_count}"
    )

    print(
        f"Best gamma: {best_gamma}"
    )

    print(
        f"Best beta: {best_beta}"
    )

    gap = (
        best_distance
        - classical_best_distance
    )

    percentage = (
        gap
        / classical_best_distance
        * 100
    )

    print("\n")
    print("=" * 55)
    print("CLASSICAL COMPARISON")
    print("=" * 55)

    print(
        f"Classical optimum: "
        f"{classical_best_distance}"
    )

    print(
        f"QAOA result:       "
        f"{best_distance}"
    )

    print(
        f"Distance gap:      "
        f"{gap}"
    )

    print(
        f"Optimality gap:    "
        f"{percentage:.2f}%"
    )

    if best_distance == classical_best_distance:

        print(
            "\nQAOA found the classical optimum!"
        )

    else:

        print(
            "\nQAOA did not find the classical optimum."
        )


if __name__ == "__main__":
    main()