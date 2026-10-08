import numpy as np


LOCATIONS = [
    "Warehouse",
    "A",
    "B",
    "C",
    "D",
    "E",
]


DISTANCE_MATRIX = np.array([
    [0, 10, 15, 20, 18, 12],
    [10, 0, 12, 18, 14, 16],
    [15, 12, 0, 10, 16, 14],
    [20, 18, 10, 0, 12, 16],
    [18, 14, 16, 12, 0, 10],
    [12, 16, 14, 16, 10, 0],
])


if __name__ == "__main__":
    print("Locations:")

    for i, location in enumerate(LOCATIONS):
        print(i, location)

    print("\nDistance Matrix:")
    print(DISTANCE_MATRIX)