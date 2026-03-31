"""List the figure scripts relevant to BP_T5_Stochastic_Stress_Pair."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_T5_Stochastic_Stress_Pair",
                "recommended_scripts": [
                    "figures/scripts/plot_t5_positive_negative_uncertainty.py",
                    "figures/scripts/plot_t5_confidence_horizon.py",
                    "figures/scripts/plot_stochastic_uncertainty.py"
                ]
            },
            indent=2,
        )
    )
