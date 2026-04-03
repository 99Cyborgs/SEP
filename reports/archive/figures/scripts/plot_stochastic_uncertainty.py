"""Plot stochastic leakage with uncertainty bands."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_Noisy_Metastable_Network"]
    if not data:
    raise SystemExit("No stochastic evidence record found.")
    record = data[0]
    leakage = record["observables"]["leakage_trajectory"] or []
    horizon = record["parameters"]["times"][: len(leakage)]
    transport = record["observables"]["transportability_metrics"] or {}
    lower = float(transport.get("bootstrap_ci_lower", 0.0))
    upper = float(transport.get("bootstrap_ci_upper", 0.0))
    plt.figure(figsize=(7, 4))
    plt.plot(horizon, leakage, label="leakage")
    plt.fill_between(horizon, [lower] * len(horizon), [upper] * len(horizon), alpha=0.25, label="bootstrap band")
    plt.xlabel("step")
    plt.ylabel("leakage")
    plt.title("Stochastic Ensemble Leakage")
    plt.legend()
    save_figure(ensure_output("reports/archive/figures/paper_D/stochastic_uncertainty.png"))

