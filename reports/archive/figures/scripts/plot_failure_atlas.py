"""Plot failure-label counts across archived evidence records."""

from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    counter = Counter()
    for record in records():
        counter.update(record.get("failure_labels", []))
    labels = list(counter)
    values = [counter[label] for label in labels]
    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color="#8a5c2a")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("count")
    plt.title("Failure Atlas")
    save_figure(ensure_output("reports/archive/figures/paper_C/failure_atlas.png"))

