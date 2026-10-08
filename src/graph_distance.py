import matplotlib.pyplot as plt

methods = [
    "Classical\nBrute Force",
    "QAOA"
]

distances = [
    66,
    66
]

plt.figure(figsize=(8, 5))

bars = plt.bar(methods, distances)

plt.ylabel("Total Route Distance")
plt.title("Classical vs QAOA Route Distance")

plt.ylim(0, 80)

for bar, value in zip(bars, distances):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1,
        str(value),
        ha="center",
        fontsize=12
    )

plt.tight_layout()

plt.savefig(
    "../results/classical_vs_qaoa_distance.png",
    dpi=300
)

plt.show()