"""List the figure scripts relevant to BP_T3_Window_Sensitivity_Pair."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_T3_Window_Sensitivity_Pair",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_t3_positive_negative_transport.py",
                    "reports/archive/figures/scripts/plot_t3_window_sensitivity.py",
                    "reports/archive/figures/scripts/plot_coherent_transport.py"
                ]
            },
            indent=2,
        )
    )

