"""List the figure scripts relevant to BP_Non_Normal_Shear."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Non_Normal_Shear",
                "recommended_scripts": [
                    "figures/scripts/plot_transient_amplification.py",
                    "figures/scripts/plot_law_comparison.py",
                    "figures/scripts/plot_failure_atlas.py"
                ]
            },
            indent=2,
        )
    )
