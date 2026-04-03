"""List the figure scripts relevant to BP_Random_Gap_Ensemble."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Random_Gap_Ensemble",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_spectra.py",
                    "reports/archive/figures/scripts/plot_law_comparison.py",
                    "reports/archive/figures/scripts/plot_transient_amplification.py",
                    "reports/archive/figures/scripts/plot_failure_atlas.py"
                ]
            },
            indent=2,
        )
    )

