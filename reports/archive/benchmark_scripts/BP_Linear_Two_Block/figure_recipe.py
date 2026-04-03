"""List the figure scripts relevant to BP_Linear_Two_Block."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Linear_Two_Block",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_spectra.py",
                    "reports/archive/figures/scripts/plot_projector_scaling.py",
                    "reports/archive/figures/scripts/plot_leakage_trajectories.py",
                    "reports/archive/figures/scripts/plot_horizon_predictions.py",
                ],
            },
            indent=2,
        )
    )

