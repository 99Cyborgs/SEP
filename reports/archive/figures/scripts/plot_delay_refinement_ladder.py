"""Plot the delay refinement ladder and adjacent stability diagnostics."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = [record for record in records() if record["benchmark_id"] == "BP_Delay_Coupled_Pair"]
    if not data:
    raise SystemExit("No BP_Delay_Coupled_Pair evidence record found.")
    record = data[0]
    delay = record["observables"]["delay_semigroup_metrics"]
    levels = delay["levels"]
    dimensions = [level["history_operator_dimension"] for level in levels]
    surrogate = [level["singular_gap"] for level in levels]
    transient = [level["transient_amplification_score"] for level in levels]
    plt.figure(figsize=(8, 4.5))
    plt.plot(dimensions, surrogate, marker="o", label="singular gap")
    plt.plot(dimensions, transient, marker="s", label="transient amplification")
    plt.xlabel("history operator dimension")
    plt.ylabel("diagnostic value")
    plt.title("Delay Refinement Ladder")
    plt.legend()
    save_figure(ensure_output("reports/archive/figures/paper_C/delay_refinement_ladder.png"))

