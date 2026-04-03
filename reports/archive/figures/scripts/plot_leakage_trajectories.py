"""Plot leakage trajectories from all available evidence records."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = records()
    plt.figure(figsize=(8, 4))
    for record in data:
        leakage = record["observables"]["leakage_trajectory"] or []
        horizon = record["parameters"].get("times") or record["parameters"].get("windows") or list(range(len(leakage)))
        plt.plot(horizon[: len(leakage)], leakage, label=record["benchmark_id"])
    plt.xlabel("time / window")
    plt.ylabel("leakage")
    plt.title("Leakage Trajectories")
    plt.legend(fontsize=7)
    save_figure(ensure_output("reports/archive/figures/paper_A/leakage_trajectories.png"))

