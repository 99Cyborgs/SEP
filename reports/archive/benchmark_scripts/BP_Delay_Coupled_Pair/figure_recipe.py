"""List the figure scripts relevant to BP_Delay_Coupled_Pair."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Delay_Coupled_Pair",
                "recommended_scripts": [
                    "reports/archive/figures/scripts/plot_delay_refinement_ladder.py",
                    "reports/archive/figures/scripts/plot_transient_amplification.py",
                    "reports/archive/figures/scripts/plot_failure_atlas.py"
                ]
            },
            indent=2,
        )
    )

