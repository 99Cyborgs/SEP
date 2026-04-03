"""Plot a cross-domain comparison across non-mobility navigation benchmarks."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [
        record
        for record in records()
        if record["benchmark_id"] in {"BP_Clickstream_Docs_Funnel", "BP_Support_Portal_Funnel"}
    ]
    if not data:
    raise SystemExit("No cross-domain navigation evidence records found.")
    labels = [f"{record['benchmark_id']}:{record['parameter_id']}" for record in data]
    deformation = [float(record["observables"]["coherent_projector_deformation"]) for record in data]
    plt.figure(figsize=(9, 4))
    plt.bar(range(len(labels)), deformation)
    plt.xticks(range(len(labels)), labels, rotation=20)
    plt.ylabel("coherent projector deformation")
    plt.title("Cross-Domain Navigation Comparison")
    save_figure(ensure_output("reports/archive/figures/cross_domain_navigation/cross_domain_navigation_comparison.png"))

