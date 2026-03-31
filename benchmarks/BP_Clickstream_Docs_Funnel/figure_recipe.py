"""List the figure scripts relevant to BP_Clickstream_Docs_Funnel."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Clickstream_Docs_Funnel",
                "recommended_outputs": [
                    "results/ledgers/BP_Clickstream_Docs_Funnel/reference_seed0.json",
                    "results/ledgers/BP_Clickstream_Docs_Funnel/negative_detour_seed0.json"
                ]
            },
            indent=2,
        )
    )
