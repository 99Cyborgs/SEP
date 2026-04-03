"""Plot native-versus-regrouped T3 carrier deformation and horizon gain."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] in {"BP_Windowed_Transport_Flow", "BP_T3_Window_Sensitivity_Pair"}]
    if not data:
    raise SystemExit("No T3 evidence records found.")
    labels = []
    native_carrier = []
    regrouped_carrier = []
    native_gain = []
    regrouped_gain = []
    for record in data:
        transport = record["observables"]["transportability_metrics"] or {}
        window = transport.get("window_sensitivity", {})
        labels.append(f"{record['benchmark_id']}:{record['parameter_id']}")
        native_carrier.append(float(transport.get("carrier_tracking", {}).get("mean_deformation", 0.0)))
        regrouped_carrier.append(float(window.get("regrouped_carrier_mean_deformation", 0.0)))
        native_gain.append(float(transport.get("coherent_vs_frozen_horizon_gain", 0.0)))
        regrouped_gain.append(float(window.get("regrouped_horizon_gain", 0.0)))
    x = range(len(labels))
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(list(x), native_carrier, marker="o", label="adjacent carrier deformation")
    axes[0].plot(list(x), regrouped_carrier, marker="s", label="regrouped carrier deformation")
    axes[0].set_ylabel("carrier deformation")
    axes[0].legend()
    axes[0].set_title("T3 Window Sensitivity Diagnostics")
    axes[1].plot(list(x), native_gain, marker="o", label="native horizon gain")
    axes[1].plot(list(x), regrouped_gain, marker="s", label="regrouped horizon gain")
    axes[1].set_ylabel("horizon gain")
    axes[1].set_xticks(list(x), labels, rotation=20)
    axes[1].legend()
    save_figure(ensure_output("reports/archive/figures/paper_B/t3_window_sensitivity.png"))

