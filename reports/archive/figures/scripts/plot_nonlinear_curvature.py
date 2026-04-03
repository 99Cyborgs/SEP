"""Plot weakly nonlinear curvature diagnostics."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_Weakly_Nonlinear_Slow_Manifold"]
    if not data:
    raise SystemExit("No nonlinear evidence record found.")
    record = data[0]
    curvature = float((record["observables"]["transportability_metrics"] or {}).get("curvature_indicator", 0.0))
    leakage = record["observables"]["leakage_trajectory"] or []
    horizon = record["parameters"]["times"][: len(leakage)]
    plt.figure(figsize=(7, 4))
    plt.plot(horizon, leakage, label="leakage")
    plt.axhline(curvature, linestyle="--", color="black", label="curvature indicator")
    plt.xlabel("time")
    plt.ylabel("value")
    plt.title("Nonlinear Curvature Correction")
    plt.legend()
    save_figure(ensure_output("reports/archive/figures/paper_D/nonlinear_curvature.png"))

