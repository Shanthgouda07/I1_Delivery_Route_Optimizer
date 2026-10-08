from itertools import permutations

from data import LOCATIONS, DISTANCE_MATRIX


def calculate_route_distance(route):
    """Calculate the total distance of a complete route."""

    total_distance = 0

    for i in range(len(route) - 1):
        from_city = route[i]
        to_city = route[i + 1]

        total_distance += DISTANCE_MATRIX[from_city, to_city]

    return total_distance


def solve_tsp_brute_force():
    """Try every possible delivery order and return the shortest route."""

    warehouse = 0
    delivery_locations = list(range(1, len(LOCATIONS)))

    best_route = None
    best_distance = float("inf")

    for permutation in permutations(delivery_locations):

        route = (warehouse,) + permutation + (warehouse,)

        distance = calculate_route_distance(route)

        if distance < best_distance:
            best_distance = distance
            best_route = route

    return best_route, best_distance


if __name__ == "__main__":

    route, distance = solve_tsp_brute_force()

    route_names = [LOCATIONS[i] for i in route]

    print("Best classical route:")
    print(" → ".join(route_names))

    print(f"\nTotal distance: {distance}")