import matplotlib.pyplot as plt
import networkx as nx

from data import LOCATIONS, DISTANCE_MATRIX


# Optimal route found by both classical and QAOA
route = [0, 1, 2, 3, 4, 5, 0]

G = nx.DiGraph()

# Add locations
for i, location in enumerate(LOCATIONS):
    G.add_node(location)

# Add route edges
for i in range(len(route) - 1):
    from_city = route[i]
    to_city = route[i + 1]

    distance = DISTANCE_MATRIX[from_city, to_city]

    G.add_edge(
        LOCATIONS[from_city],
        LOCATIONS[to_city],
        distance=distance
    )


# Manually position the locations for a clean presentation
positions = {
    "Warehouse": (0, 0),
    "A": (1, 2),
    "B": (3, 3),
    "C": (5, 2),
    "D": (5, -1),
    "E": (2, -2),
}


plt.figure(figsize=(10, 7))

# Draw locations
nx.draw_networkx_nodes(
    G,
    positions,
    node_size=1800
)

# Draw route
nx.draw_networkx_edges(
    G,
    positions,
    arrows=True,
    arrowsize=20,
    width=2
)

# Draw location names
nx.draw_networkx_labels(
    G,
    positions,
    font_size=12,
    font_weight="bold"
)

# Draw distances
edge_labels = nx.get_edge_attributes(G, "distance")

nx.draw_networkx_edge_labels(
    G,
    positions,
    edge_labels=edge_labels,
    font_size=11
)


plt.title(
    "Optimized Delivery Route\n"
    "Total Distance = 66"
)

plt.axis("off")
plt.tight_layout()

plt.savefig(
    "../results/optimized_delivery_route.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()