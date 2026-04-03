"""Plot T5 confidence-bounded horizon comparisons."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [
        record
        for record in records()
        if record["benchmark_id"] in {"BP_Noisy_Metastable_Network", "BP_T5_Stochastic_Stress_Pair"}
    ]
    if not data:
    raise SystemExit("No T5 evidence records found.")
    labels = [f"{record['benchmark_id']}:{record['parameter_id']}" for record in data]
    estimated = [float(record["observables"]["stochastic_uncertainty_metrics"]["estimated_horizon"]) for record in data]
    bounded = [float(record["observables"]["stochastic_uncertainty_metrics"]["confidence_bounded_horizon"]) for record in data]
    x = range(len(labels))
    plt.figure(figsize=(9, 4))
    plt.plot(list(x), estimated, marker="o", label="estimated horizon")
    plt.plot(list(x), bounded, marker="s", label="confidence-bounded horizon")
    plt.xticks(list(x), labels, rotation=20)
    plt.ylabel("horizon")
    plt.title("T5 Confidence-Bounded Horizon")
    plt.legend()
    save_figure(ensure_output("reports/archive/figures/paper_D/t5_confidence_horizon.png"))

