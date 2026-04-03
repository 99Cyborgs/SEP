"""List the figure scripts relevant to BP_Windowed_Transport_Flow."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Windowed_Transport_Flow",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_coherent_transport.py",
                    "reports/archive/figures/scripts/plot_horizon_predictions.py",
                    "reports/archive/figures/scripts/plot_law_comparison.py"
                ]
            },
            indent=2,
        )
    )

