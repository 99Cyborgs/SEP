"""List the figure scripts relevant to BP_Support_Portal_Funnel."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Support_Portal_Funnel",
                "recommended_outputs": [
                    "results/evidence/BP_Support_Portal_Funnel/reference/seed_0/run_manifest.json",
                    "results/evidence/BP_Support_Portal_Funnel/negative_detour/seed_0/run_manifest.json"
                ]
            },
            indent=2,
        )
    )

