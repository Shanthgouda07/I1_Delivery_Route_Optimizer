import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qubo import create_tsp_problem
from data import LOCATIONS, DISTANCE_MATRIX


SHOTS = 200

GAMMA_VALUES = [0.2, 0.5, 1.0]
BETA_VALUES = [0.2, 0.5, 1.0]


def qubo_to_ising(problem):
    """
    Convert the QUBO objective into an Ising Hamiltonian.

    x_i = (1 - Z_i) / 2
    """

    num_vars = problem.get_num_vars()

    linear = np.zeros(num_vars)

    for i, coefficient in problem.objective.linear.to_dict().items():
        linear[i] = float(coefficient)

    quadratic = problem.objective.quadratic.to_dict()

    # Handle diagonal terms.
    for (i, j), coefficient in quadratic.items():

        if i == j:
            linear[i] += float(coefficient)

    h = np.zeros(num_vars)
    J = {}

    # Linear:
    #
    # a*x = a/2 - a/2 Z
    #
    for i in range(num_vars):
        h[i] = -linear[i] / 2.0

    # Quadratic:
    #
    # b*x_i*x_j
    #
    # = b/4 (1 - Zi - Zj + ZiZj)
    #
    for (i, j), coefficient in quadratic.items():

        coefficient = float(coefficient)

        if i == j:
            continue

        h[i] -= coefficient / 4.0
        h[j] -= coefficient / 4.0

        J[(i, j)] = coefficient / 4.0

    return h, J


def create_valid_initial_state():
    """
    Create a known valid TSP route.

    Our classical route is:

        Warehouse -> A -> B -> C -> D -> E -> Warehouse

    x_city_position = 1 for the selected city/position.
    """

    num_cities = len(LOCATIONS) - 1
    num_qubits = num_cities * num_cities

    qc = QuantumCircuit(num_qubits)

    # Route:
    #
    # position 0 -> A
    # position 1 -> B
    # position 2 -> C
    # position 3 -> D
    # position 4 -> E
    #
    route = [1, 3, 5, 2, 4]

    for position, city in enumerate(route):

        index = (city - 1) * num_cities + position

        qc.x(index)

    return qc


def build_qaoa_circuit(h, J, gamma, beta):
    """
    QAOA circuit starting from a valid TSP state.

    This is an engineering experiment:
    we initialize in a feasible route instead of |+>^25.
    """

    num_qubits = len(h)

    max_coefficient = max(
        np.max(np.abs(h)),
        max(
            (abs(value) for value in J.values()),
            default=0.0,
        ),
        1.0,
    )

    h_scaled = h / max_coefficient

    J_scaled = {
        pair: value / max_coefficient
        for pair, value in J.items()
    }

    qc = create_valid_initial_state()

    # ---------------------------------------------------------
    # Cost layer
    # ---------------------------------------------------------

    for qubit in range(num_qubits):

        if abs(h_scaled[qubit]) > 1e-12:

            angle = 2.0 * gamma * h_scaled[qubit]

            qc.rz(angle, qubit)

    for (i, j), coefficient in J_scaled.items():

        if abs(coefficient) > 1e-12:

            angle = 2.0 * gamma * coefficient

            qc.cx(i, j)
            qc.rz(angle, j)
            qc.cx(i, j)

    # ---------------------------------------------------------
    # Mixer
    # ---------------------------------------------------------

    for qubit in range(num_qubits):

        qc.rx(2.0 * beta, qubit)

    # ---------------------------------------------------------
    # Measurement
    # ---------------------------------------------------------

    qc.measure_all()

    return qc


def decode_route(bitstring):
    """
    Decode a 25-bit measurement into a TSP route.

    Returns None for an invalid route.
    """

    num_cities = len(LOCATIONS) - 1

    bits = bitstring[::-1]

    route = [0]

    for position in range(num_cities):

        selected_city = None

        for city in range(1, len(LOCATIONS)):

            index = (
                (city - 1) * num_cities
                + position
            )

            if bits[index] == "1":

                if selected_city is not None:
                    return None

                selected_city = city

        if selected_city is None:
            return None

        route.append(selected_city)

    route.append(0)

    # Every delivery city must appear exactly once.
    if len(set(route[1:-1])) != num_cities:
        return None

    return route


def calculate_route_distance(route):

    total_distance = 0

    for i in range(len(route) - 1):

        total_distance += DISTANCE_MATRIX[
            route[i],
            route[i + 1],
        ]

    return total_distance


def run_single_experiment(h, J, gamma, beta):

    circuit = build_qaoa_circuit(
        h,
        J,
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

        route = decode_route(bitstring)

        if route is not None:

            distance = calculate_route_distance(route)

            valid_routes.append(
                (
                    distance,
                    count,
                    bitstring,
                    route,
                )
            )

    return counts, valid_routes


def run_qaoa():

    print("Creating QUBO...")

    problem = create_tsp_problem()

    print(
        f"Number of qubits: "
        f"{problem.get_num_vars()}"
    )

    print("\nConverting QUBO to Ising...")

    h, J = qubo_to_ising(problem)

    print(f"Z terms:  {len(h)}")
    print(f"ZZ terms: {len(J)}")

    print("\nCreating valid initial route...")

    initial_route = [
        "Warehouse",
        "A",
        "C",
        "E",
        "B",
        "D",
        "Warehouse",
    ]

    print(" → ".join(initial_route))

    print("\nRunning QAOA parameter scan...")
    print(f"Shots per experiment: {SHOTS}")

    best_result = None

    total_experiments = (
        len(GAMMA_VALUES)
        * len(BETA_VALUES)
    )

    experiment_number = 0

    for gamma in GAMMA_VALUES:

        for beta in BETA_VALUES:

            experiment_number += 1

            print(
                f"\nExperiment "
                f"{experiment_number}/{total_experiments}"
            )

            print(
                f"gamma={gamma}, beta={beta}"
            )

            counts, valid_routes = run_single_experiment(
                h,
                J,
                gamma,
                beta,
            )

            print(
                f"Unique states: {len(counts)}"
            )

            print(
                f"Valid routes:  {len(valid_routes)}"
            )

            if valid_routes:

                valid_routes.sort(
                    key=lambda x: x[0]
                )

                candidate = valid_routes[0]

                if (
                    best_result is None
                    or candidate[0] < best_result[0]
                ):

                    best_result = (
                        candidate[0],
                        candidate[1],
                        candidate[2],
                        candidate[3],
                        gamma,
                        beta,
                    )

    print("\n")
    print("=" * 50)
    print("FINAL QAOA RESULT")
    print("=" * 50)

    if best_result is None:

        print(
            "\nNo valid route was sampled."
        )

        return

    (
        best_distance,
        best_count,
        best_bitstring,
        best_route,
        best_gamma,
        best_beta,
    ) = best_result

    route_names = [
        LOCATIONS[i]
        for i in best_route
    ]

    print("\nBest QAOA route:")

    print(
        " → ".join(route_names)
    )

    print(
        f"\nQAOA distance: {best_distance}"
    )

    print(
        f"Samples of route: {best_count}"
    )

    print(
        f"Best gamma: {best_gamma}"
    )

    print(
        f"Best beta: {best_beta}"
    )

    classical_distance = 66

    print("\n")
    print("=" * 50)
    print("CLASSICAL COMPARISON")
    print("=" * 50)

    print(
        f"Classical optimum: {classical_distance}"
    )

    print(
        f"QAOA result:       {best_distance}"
    )

    gap = best_distance - classical_distance

    percentage = (
        gap / classical_distance
    ) * 100

    print(
        f"\nDistance gap: {gap}"
    )

    print(
        f"Optimality gap: {percentage:.2f}%"
    )

    if best_distance == classical_distance:

        print(
            "\nQAOA found the classical optimum!"
        )

    else:

        print(
            "\nQAOA did not find the classical optimum."
        )


if __name__ == "__main__":

    run_qaoa()