"""Plot accepted versus rejected support-navigation application cases."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_Support_Portal_Funnel"]
    if len(data) < 2:
        raise SystemExit("Need accepted and rejected BP_Support_Portal_Funnel ledgers.")
    labels = [record["parameter_id"] for record in data]
    gaps = [float(record["observables"]["singular_gap"]) for record in data]
    plt.figure(figsize=(6, 4))
    plt.bar(range(len(labels)), gaps)
    plt.xticks(range(len(labels)), labels)
    plt.ylabel("singular gap")
    plt.title("Support Navigation Accepted vs Rejected")
    save_figure(ensure_output("figures/cross_domain_navigation/support_navigation_acceptance_comparison.png"))
