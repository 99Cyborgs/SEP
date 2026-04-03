"""List the figure scripts relevant to BP_T4_Local_Validity_Pair."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_T4_Local_Validity_Pair",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_t4_positive_negative_locality.py",
                    "reports/archive/figures/scripts/plot_t4_local_validity_metrics.py",
                    "reports/archive/figures/scripts/plot_nonlinear_curvature.py"
                ]
            },
            indent=2,
        )
    )

