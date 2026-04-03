"""List the figure scripts relevant to BP_Weakly_Nonlinear_Slow_Manifold."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Weakly_Nonlinear_Slow_Manifold",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_nonlinear_curvature.py",
                    "reports/archive/figures/scripts/plot_leakage_trajectories.py",
                    "reports/archive/figures/scripts/plot_law_comparison.py"
                ]
            },
            indent=2,
        )
    )

