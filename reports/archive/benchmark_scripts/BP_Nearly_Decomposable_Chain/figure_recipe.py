"""List the figure scripts relevant to BP_Nearly_Decomposable_Chain."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Nearly_Decomposable_Chain",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_spectra.py",
                    "reports/archive/figures/scripts/plot_leakage_trajectories.py",
                    "reports/archive/figures/scripts/plot_law_comparison.py"
                ]
            },
            indent=2,
        )
    )

