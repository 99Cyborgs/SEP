"""Plot positive-versus-breakdown nonlinear locality diagnostics."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_T4_Local_Validity_Pair"]
    if not data:
    raise SystemExit("No BP_T4_Local_Validity_Pair evidence records found.")
    labels = [record["parameters"]["parameter_id"] for record in data]
    margins = [float(record["observables"]["local_validity_metrics"]["local_validity_margin"]) for record in data]
    defects = [float(record["observables"]["local_validity_metrics"]["fast_slaving_defect"]) for record in data]
    x = range(len(labels))
    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    axes[0].bar(list(x), margins)
    axes[0].set_ylabel("local-validity margin")
    axes[0].set_title("T4 Positive vs Breakdown")
    axes[1].bar(list(x), defects)
    axes[1].set_ylabel("fast slaving defect")
    axes[1].set_xticks(list(x), labels)
    save_figure(ensure_output("reports/archive/figures/paper_D/t4_positive_negative_locality.png"))

