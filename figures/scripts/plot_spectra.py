"""Plot spectral and singular gaps across ledgers."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = records()
    labels = [record["benchmark_id"] for record in data]
    values = [
        float(
            record["observables"]["spectral_gap"]
            if record["observables"]["spectral_gap"] is not None
            else record["observables"]["singular_gap"] or 0.0
        )
        for record in data
    ]
    plt.figure(figsize=(10, 4))
    plt.bar(labels, values, color="#315c73")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("gap")
    plt.title("Spectral / Singular Gap Ladder")
    save_figure(ensure_output("figures/paper_A/spectra_and_singular_gaps.png"))
