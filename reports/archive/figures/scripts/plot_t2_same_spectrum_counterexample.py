"""Plot the same-spectrum T2 counterexample pair."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [
        record
        for record in records()
        if record["benchmark_id"] == "BP_T2_Same_Spectrum_Pair"
    ]
    data.sort(key=lambda record: record["parameter_id"])
    labels = [record["parameter_id"] for record in data]
    spectral = [float(record["observables"]["spectral_gap"] or 0.0) for record in data]
    transient = [float(record["observables"]["transient_amplification_score"] or 0.0) for record in data]
    plt.figure(figsize=(7, 4))
    plt.bar([index - 0.18 for index in range(len(data))], spectral, width=0.32, label="spectral gap", color="#2f5d7c")
    plt.bar([index + 0.18 for index in range(len(data))], transient, width=0.32, label="transient amplification", color="#b85c38")
    plt.xticks(list(range(len(data))), labels)
    plt.ylabel("value")
    plt.title("T2 Same-Spectrum Counterexample Pair")
    plt.legend()
    save_figure(ensure_output("reports/archive/figures/paper_C/same_spectrum_counterexample.png"))

