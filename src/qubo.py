from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo

from data import LOCATIONS, DISTANCE_MATRIX


def create_tsp_problem():
    """
    Create a TSP as a binary quadratic optimization problem.

    x[i,t] = 1 means:
    city i is visited at position t.
    """

    problem = QuadraticProgram("DeliveryRoute")

    # We don't include the warehouse in the permutation.
    # The route starts and ends at the warehouse.
    cities = list(range(1, len(LOCATIONS)))

    num_cities = len(cities)

    # ---------------------------------------------------------
    # 1. Create binary variables
    # ---------------------------------------------------------

    for city in cities:
        for position in range(num_cities):
            variable_name = f"x_{city}_{position}"
            problem.binary_var(name=variable_name)

    # ---------------------------------------------------------
    # 2. Each city must be visited exactly once
    # ---------------------------------------------------------

    for city in cities:

        variables = [
            f"x_{city}_{position}"
            for position in range(num_cities)
        ]

        problem.linear_constraint(
            linear={
                variable: 1
                for variable in variables
            },
            sense="==",
            rhs=1,
            name=f"city_{city}_visited_once",
        )

    # ---------------------------------------------------------
    # 3. Each route position must contain exactly one city
    # ---------------------------------------------------------

    for position in range(num_cities):

        variables = [
            f"x_{city}_{position}"
            for city in cities
        ]

        problem.linear_constraint(
            linear={
                variable: 1
                for variable in variables
            },
            sense="==",
            rhs=1,
            name=f"position_{position}_has_one_city",
        )

    # ---------------------------------------------------------
    # 4. Minimize total travel distance
    # ---------------------------------------------------------

    linear = {}
    quadratic = {}

    warehouse = 0

    # Distance from warehouse to first city
    for city in cities:

        variable = f"x_{city}_0"

        linear[variable] = DISTANCE_MATRIX[
            warehouse, city
        ]

    # Distance between consecutive cities
    for position in range(num_cities - 1):

        for city_a in cities:
            for city_b in cities:

                variable_a = f"x_{city_a}_{position}"
                variable_b = f"x_{city_b}_{position + 1}"

                quadratic[
                    (variable_a, variable_b)
                ] = DISTANCE_MATRIX[
                    city_a, city_b
                ]

    # Distance from final city back to warehouse
    for city in cities:

        variable = f"x_{city}_{num_cities - 1}"

        linear[variable] = (
            linear.get(variable, 0)
            + DISTANCE_MATRIX[city, warehouse]
        )

    problem.minimize(
        linear=linear,
        quadratic=quadratic,
    )

    return problem


if __name__ == "__main__":

    # Create the TSP
    problem = create_tsp_problem()

    print("===== TSP PROBLEM =====")
    print(problem.prettyprint())

    print("\nNumber of variables:")
    print(problem.get_num_vars())

    print("\nNumber of constraints:")
    print(problem.get_num_linear_constraints())

    # ---------------------------------------------------------
    # Convert TSP to QUBO
    # ---------------------------------------------------------

    converter = QuadraticProgramToQubo(
        penalty=100
    )

    qubo = converter.convert(problem)

    print("\n===== QUBO =====")
    print(qubo.prettyprint())

    print("\nQUBO variables:")
    print(qubo.get_num_vars())

    print("\nQUBO constraints:")
    print(qubo.get_num_linear_constraints())