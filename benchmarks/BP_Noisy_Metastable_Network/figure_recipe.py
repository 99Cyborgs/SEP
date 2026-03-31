"""List the figure scripts relevant to BP_Noisy_Metastable_Network."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Noisy_Metastable_Network",
                "recommended_scripts": [
                    "figures/scripts/plot_stochastic_uncertainty.py",
                    "figures/scripts/plot_law_comparison.py",
                    "figures/scripts/plot_failure_atlas.py"
                ]
            },
            indent=2,
        )
    )
