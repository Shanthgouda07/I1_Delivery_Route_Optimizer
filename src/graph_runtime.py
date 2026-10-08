import matplotlib.pyplot as plt

methods = [
    "Classical\nBrute Force",
    "QAOA"
]

runtimes = [
    0.000296,
    1.320606
]

plt.figure(figsize=(8, 5))

bars = plt.bar(methods, runtimes)

plt.ylabel("Runtime (seconds)")
plt.title("Classical vs QAOA Runtime")

plt.ylim(0, 1.5)

for bar, value in zip(bars, runtimes):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.03,
        f"{value:.6f}",
        ha="center",
        fontsize=11
    )

plt.tight_layout()

plt.savefig(
    "../results/classical_vs_qaoa_runtime.png",
    dpi=300
)

plt.show()