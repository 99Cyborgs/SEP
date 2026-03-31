"""Plot held-out law-fit errors across benchmarks."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = records()
    laws = ["L1", "L2", "L3"]
    plt.figure(figsize=(10, 4))
    width = 0.22
    x_positions = list(range(len(data)))
    for offset, law in enumerate(laws):
        values = [float(record["law_fits"].get(law, {}).get("test_rmse", 0.0)) for record in data]
        shifted = [position + (offset - 1) * width for position in x_positions]
        plt.bar(shifted, values, width=width, label=law)
    plt.xticks(x_positions, [record["benchmark_id"] for record in data], rotation=45, ha="right")
    plt.ylabel("held-out RMSE")
    plt.title("Leakage Law Comparison")
    plt.legend()
    save_figure(ensure_output("figures/paper_C/law_comparison.png"))
