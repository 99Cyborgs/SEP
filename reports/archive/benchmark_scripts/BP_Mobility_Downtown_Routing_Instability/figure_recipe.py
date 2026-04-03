"""List the figure scripts relevant to BP_Mobility_Downtown_Routing_Instability."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Mobility_Downtown_Routing_Instability",
                "recommended_outputs": [
                    "results/evidence/BP_Mobility_Downtown_Routing_Instability/reference/seed_0/run_manifest.json",
                    "reports/archive/figures/paper_E/package_manifest.json"
                ]
            },
            indent=2,
        )
    )

