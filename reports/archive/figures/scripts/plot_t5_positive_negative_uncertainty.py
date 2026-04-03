"""Plot positive-versus-stress stochastic uncertainty diagnostics."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_T5_Stochastic_Stress_Pair"]
    if not data:
    raise SystemExit("No BP_T5_Stochastic_Stress_Pair evidence records found.")
    labels = [record["parameters"]["parameter_id"] for record in data]
    widths = [float(record["observables"]["stochastic_uncertainty_metrics"]["bootstrap_width"]) for record in data]
    confidence_horizons = [
        float(record["observables"]["stochastic_uncertainty_metrics"]["confidence_bounded_horizon"]) for record in data
    ]
    x = range(len(labels))
    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    axes[0].bar(list(x), widths)
    axes[0].set_ylabel("bootstrap width")
    axes[0].set_title("T5 Positive vs Sample Stress")
    axes[1].bar(list(x), confidence_horizons)
    axes[1].set_ylabel("confidence-bounded horizon")
    axes[1].set_xticks(list(x), labels)
    save_figure(ensure_output("reports/archive/figures/paper_D/t5_positive_negative_uncertainty.png"))

