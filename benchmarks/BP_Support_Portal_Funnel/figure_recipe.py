"""List the figure scripts relevant to BP_Support_Portal_Funnel."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Support_Portal_Funnel",
                "recommended_outputs": [
                    "results/ledgers/BP_Support_Portal_Funnel/reference_seed0.json",
                    "results/ledgers/BP_Support_Portal_Funnel/negative_detour_seed0.json"
                ]
            },
            indent=2,
        )
    )
