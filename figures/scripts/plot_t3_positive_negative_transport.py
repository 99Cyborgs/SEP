"""Plot positive-versus-mixed transport horizons for Paper B."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_T3_Window_Sensitivity_Pair"]
    if not data:
        raise SystemExit("No BP_T3_Window_Sensitivity_Pair ledgers found.")
    data.sort(key=lambda record: record["parameter_id"])
    labels = [record["parameters"]["case_label"] for record in data]
    transport = [record["observables"]["transportability_metrics"] for record in data]
    coherent = [entry["coherent_horizon"] for entry in transport]
    frozen = [entry["frozen_horizon"] for entry in transport]
    x = range(len(labels))
    plt.figure(figsize=(7, 4))
    plt.bar([index - 0.18 for index in x], coherent, width=0.36, label="coherent horizon")
    plt.bar([index + 0.18 for index in x], frozen, width=0.36, label="frozen horizon")
    plt.xticks(list(x), labels, rotation=12)
    plt.ylabel("autonomy horizon")
    plt.title("T3 Positive vs Mixed Transport Horizons")
    plt.legend()
    save_figure(ensure_output("figures/paper_B/t3_positive_negative_transport.png"))
