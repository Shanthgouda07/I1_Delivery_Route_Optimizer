import matplotlib.pyplot as plt

methods = [
    "QAOA"
]

optimality_gap = [
    0.00
]

plt.figure(figsize=(7, 5))

bars = plt.bar(methods, optimality_gap)

plt.ylabel("Optimality Gap (%)")
plt.title("QAOA Optimality Gap")

plt.ylim(0, 5)

for bar, value in zip(bars, optimality_gap):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.15,
        f"{value:.2f}%",
        ha="center",
        fontsize=14
    )

plt.tight_layout()

plt.savefig(
    "../results/qaoa_optimality_gap.png",
    dpi=300
)

plt.show()