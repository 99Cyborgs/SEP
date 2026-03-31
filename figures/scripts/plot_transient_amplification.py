"""Plot transient amplification diagnostics."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = records()
    labels = [record["benchmark_id"] for record in data]
    values = [float(record["observables"]["transient_amplification_score"] or 0.0) for record in data]
    plt.figure(figsize=(10, 4))
    plt.bar(labels, values, color="#5b7742")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Gamma_T")
    plt.title("Transient Amplification Diagnostics")
    save_figure(ensure_output("figures/paper_C/transient_amplification.png"))
