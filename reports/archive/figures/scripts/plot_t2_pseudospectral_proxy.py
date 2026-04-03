"""Plot T2 pseudospectral proxy diagnostics."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [
        record
        for record in records()
        if record["benchmark_id"] in {"BP_Non_Normal_Shear", "BP_Random_Gap_Ensemble", "BP_Delay_Coupled_Pair", "BP_T2_Same_Spectrum_Pair"}
    ]
    labels = [f"{record['benchmark_id']}:{record['parameter_id']}" for record in data]
    values = [float(record["observables"].get("pseudospectral_proxy") or 0.0) for record in data]
    plt.figure(figsize=(10, 4))
    plt.bar(labels, values, color="#7a4f9a")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("proxy")
    plt.title("T2 Pseudospectral Proxy Diagnostics")
    save_figure(ensure_output("reports/archive/figures/paper_C/pseudospectral_proxy.png"))

