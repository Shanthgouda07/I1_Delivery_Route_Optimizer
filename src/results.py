import csv
import time

from classical_solver import solve_tsp_brute_force
from permutation_qaoa import (
    generate_routes,
    build_route_costs,
    run_experiment,
    GAMMA_VALUES,
    BETA_VALUES,
    SHOTS,
)
from data import LOCATIONS


def route_to_string(route):
    return " → ".join(LOCATIONS[i] for i in route)


def main():

    print("=" * 60)
    print("I1 DELIVERY ROUTE OPTIMIZER - BENCHMARK")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Classical brute-force benchmark
    # ---------------------------------------------------------

    print("\nRunning classical brute force...")

    start = time.perf_counter()

    classical_route, classical_distance = solve_tsp_brute_force()

    classical_time = time.perf_counter() - start

    print("Classical route:")
    print(route_to_string(classical_route))
    print(f"Classical distance: {classical_distance}")
    print(f"Classical runtime: {classical_time:.6f} seconds")

    # ---------------------------------------------------------
    # 2. Generate permutation space
    # ---------------------------------------------------------

    print("\nGenerating permutation space...")

    routes = generate_routes()
    costs = build_route_costs(routes)

    print(f"Valid routes: {len(routes)}")
    print(f"Quantum states: 128")

    # ---------------------------------------------------------
    # 3. Run QAOA parameter scan
    # ---------------------------------------------------------

    print("\nRunning QAOA experiments...")

    best_result = None
    total_valid_samples = 0
    total_samples = 0

    qaoa_start = time.perf_counter()

    for gamma in GAMMA_VALUES:

        for beta in BETA_VALUES:

            print(f"gamma={gamma}, beta={beta}")

            counts, valid_routes = run_experiment(
                routes,
                costs,
                gamma,
                beta,
            )

            # Count all sampled states
            total_samples += SHOTS

            # Count valid route samples
            valid_sample_count = sum(
                count
                for _, count, _ in valid_routes
            )

            total_valid_samples += valid_sample_count

            if valid_routes:

                valid_routes.sort(key=lambda x: x[0])

                candidate = valid_routes[0]

                candidate_distance = candidate[0]
                candidate_count = candidate[1]
                candidate_route = candidate[2]

                if (
                    best_result is None
                    or candidate_distance < best_result[0]
                ):
                    best_result = (
                        candidate_distance,
                        candidate_count,
                        candidate_route,
                        gamma,
                        beta,
                    )

    qaoa_time = time.perf_counter() - qaoa_start

    # ---------------------------------------------------------
    # 4. Extract QAOA result
    # ---------------------------------------------------------

    if best_result is None:

        print("\nQAOA did not produce a valid route.")

        return

    qaoa_distance = best_result[0]
    qaoa_samples = best_result[1]
    qaoa_route = best_result[2]
    best_gamma = best_result[3]
    best_beta = best_result[4]

    distance_gap = qaoa_distance - classical_distance

    optimality_gap = (
        distance_gap / classical_distance * 100
    )

    valid_sampling_rate = (
        total_valid_samples / total_samples * 100
    )

    # ---------------------------------------------------------
    # 5. Print final benchmark
    # ---------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("FINAL BENCHMARK")
    print("=" * 60)

    print("\nCLASSICAL")
    print(f"Route:    {route_to_string(classical_route)}")
    print(f"Distance: {classical_distance}")
    print(f"Runtime:  {classical_time:.6f} seconds")

    print("\nQAOA")
    print(f"Route:    {route_to_string(qaoa_route)}")
    print(f"Distance: {qaoa_distance}")
    print(f"Runtime:  {qaoa_time:.6f} seconds")
    print(f"Gamma:    {best_gamma}")
    print(f"Beta:     {best_beta}")
    print(f"Samples:  {qaoa_samples}")

    print("\nCOMPARISON")
    print(f"Distance gap:       {distance_gap}")
    print(f"Optimality gap:     {optimality_gap:.2f}%")
    print(f"Valid sampling rate: {valid_sampling_rate:.2f}%")

        # ---------------------------------------------------------
    # 6. Save CSV
    # ---------------------------------------------------------

    output_file = "results/i1_benchmark.csv"

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "method",
            "route",
            "distance",
            "runtime_seconds",
            "optimality_gap_percent",
            "valid_sampling_rate_percent",
        ])

        writer.writerow([
            "Classical Brute Force",
            route_to_string(classical_route),
            classical_distance,
            classical_time,
            0,
            "",
        ])

        writer.writerow([
            "QAOA",
            route_to_string(qaoa_route),
            qaoa_distance,
            qaoa_time,
            optimality_gap,
            valid_sampling_rate,
        ])

        print(f"\nSaved benchmark to {output_file}")


if __name__ == "__main__":
    main()
