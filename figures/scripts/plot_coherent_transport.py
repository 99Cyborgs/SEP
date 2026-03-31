"""Plot coherent transport benchmark summaries."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_Windowed_Transport_Flow"]
    if not data:
        raise SystemExit("No transport ledger found.")
    record = data[0]
    leakage = record["observables"]["leakage_trajectory"] or []
    windows = record["parameters"]["windows"][: len(leakage)]
    plt.figure(figsize=(7, 4))
    plt.plot(windows, leakage, marker="o", label="coherent leakage")
    plt.xlabel("window")
    plt.ylabel("leakage")
    plt.title("Coherent Transport Leakage")
    plt.legend()
    save_figure(ensure_output("figures/paper_B/coherent_transport.png"))
