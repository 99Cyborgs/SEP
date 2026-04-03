"""Plot accepted versus rejected clickstream application cases."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_Clickstream_Docs_Funnel"]
    if len(data) < 2:
    raise SystemExit("Need accepted and rejected BP_Clickstream_Docs_Funnel evidence records.")
    labels = [record["parameter_id"] for record in data]
    gaps = [float(record["observables"]["singular_gap"]) for record in data]
    plt.figure(figsize=(6, 4))
    plt.bar(range(len(labels)), gaps)
    plt.xticks(range(len(labels)), labels)
    plt.ylabel("singular gap")
    plt.title("Clickstream Accepted vs Rejected")
    save_figure(ensure_output("reports/archive/figures/cross_domain_navigation/clickstream_acceptance_comparison.png"))

