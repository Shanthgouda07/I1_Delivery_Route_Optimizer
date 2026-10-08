import matplotlib.pyplot as plt
import networkx as nx

from data import LOCATIONS, DISTANCE_MATRIX
from classical_solver import solve_tsp_brute_force


def create_delivery_graph():
    """Create a graph showing all delivery locations."""

    graph = nx.Graph()

    # Add locations
    for i, location in enumerate(LOCATIONS):
        graph.add_node(location)

    # Add connections and distances
    for i in range(len(LOCATIONS)):
        for j in range(i + 1, len(LOCATIONS)):
            graph.add_edge(
                LOCATIONS[i],
                LOCATIONS[j],
                weight=DISTANCE_MATRIX[i, j],
            )

    return graph


def plot_classical_route():

    route, distance = solve_tsp_brute_force()

    route_names = [LOCATIONS[i] for i in route]

    graph = create_delivery_graph()

    # Fixed positions make the visualization reproducible
    positions = {
        "Warehouse": (0, 0),
        "A": (2, 3),
        "B": (5, 4),
        "C": (8, 2),
        "D": (7, -1),
        "E": (3, -2),
    }

    plt.figure(figsize=(10, 7))

    # Draw all locations
    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=1200,
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        font_size=11,
        font_weight="bold",
    )

    # Draw the route
    route_edges = []

    for i in range(len(route_names) - 1):
        route_edges.append(
            (route_names[i], route_names[i + 1])
        )

    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=route_edges,
        width=3,
        arrows=True,
        arrowsize=20,
    )

    plt.title(
        f"Classical Optimal Delivery Route\n"
        f"Total Distance = {distance}"
    )

    plt.axis("off")
    plt.tight_layout()

    plt.savefig(
        "../results/classical_route.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


if __name__ == "__main__":
    plot_classical_route()