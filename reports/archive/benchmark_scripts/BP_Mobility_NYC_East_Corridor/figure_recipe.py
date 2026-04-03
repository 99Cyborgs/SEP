"""List the figure scripts relevant to BP_Mobility_NYC_East_Corridor."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Mobility_NYC_East_Corridor",
                "recommended_outputs": [
                    "results/evidence/BP_Mobility_NYC_East_Corridor/reference/seed_0/run_manifest.json",
                    "reports/archive/figures/paper_E/package_manifest.json"
                ]
            },
            indent=2,
        )
    )

