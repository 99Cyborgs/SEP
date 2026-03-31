"""Plot predicted versus observed autonomy horizon."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = records()
    observed = [float(record["observables"]["autonomy_horizon"] or 0.0) for record in data]
    predicted = [float(record["observables"].get("predicted_autonomy_horizon") or 0.0) for record in data]
    labels = [record["benchmark_id"] for record in data]
    plt.figure(figsize=(6, 4))
    plt.scatter(predicted, observed, color="#aa4c31")
    for label, x_value, y_value in zip(labels, predicted, observed, strict=True):
        plt.text(x_value, y_value, label, fontsize=7)
    upper = max(predicted + observed + [1.0])
    plt.plot([0.0, upper], [0.0, upper], linestyle="--", color="black", linewidth=1)
    plt.xlabel("predicted horizon")
    plt.ylabel("observed horizon")
    plt.title("Predicted vs Observed Autonomy Horizon")
    save_figure(ensure_output("figures/paper_A/horizon_predictions.png"))
