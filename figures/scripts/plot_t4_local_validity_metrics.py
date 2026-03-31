"""Plot T4 local-validity metric comparisons."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [
        record
        for record in records()
        if record["benchmark_id"] in {"BP_Weakly_Nonlinear_Slow_Manifold", "BP_T4_Local_Validity_Pair"}
    ]
    if not data:
        raise SystemExit("No T4 ledgers found.")
    labels = [f"{record['benchmark_id']}:{record['parameter_id']}" for record in data]
    anchors = [float(record["observables"]["local_validity_metrics"]["anchor_projector_deformation"]) for record in data]
    l2_gain = [float(record["observables"]["local_validity_metrics"]["l2_minus_l1_rmse"]) for record in data]
    x = range(len(labels))
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(list(x), anchors, marker="o")
    axes[0].set_ylabel("anchor deformation")
    axes[0].set_title("T4 Local Validity Metrics")
    axes[1].plot(list(x), l2_gain, marker="o")
    axes[1].set_ylabel("L2 - L1 RMSE gain")
    axes[1].set_xticks(list(x), labels, rotation=20)
    save_figure(ensure_output("figures/paper_D/t4_local_validity_metrics.png"))
