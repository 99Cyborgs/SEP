"""List the figure scripts relevant to BP_Mobility_Chicago_Corridors."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Mobility_Chicago_Corridors",
                "application_summary": "results/application/BP_Mobility_Chicago_Corridors/paper_e_application_summary.json",
                "package_manifest": "figures/paper_E/package_manifest.json",
                "panels": [
                    {
                        "panel_id": "weekday_leakage",
                        "purpose": "Show coherent leakage over the accepted weekday reference windows.",
                        "generator": "benchmarks/BP_Mobility_Chicago_Corridors/generate_paper_e_package.py",
                        "output_png": "figures/paper_E/weekday_leakage.png",
                        "ledger_json": "results/ledgers/BP_Mobility_Chicago_Corridors/weekday_reference_seed0.json",
                    },
                    {
                        "panel_id": "weekday_horizon",
                        "purpose": "Compare observed and predicted horizons for the accepted weekday reference.",
                        "generator": "benchmarks/BP_Mobility_Chicago_Corridors/generate_paper_e_package.py",
                        "output_png": "figures/paper_E/weekday_horizon.png",
                        "ledger_json": "results/ledgers/BP_Mobility_Chicago_Corridors/weekday_reference_seed0.json",
                    },
                    {
                        "panel_id": "negative_failure_comparison",
                        "purpose": "Show why the weekend-night and downtown slices are rejected and how the NYC corridor remains mixed while the weekday sweep remains usable.",
                        "generator": "benchmarks/BP_Mobility_Chicago_Corridors/generate_paper_e_package.py",
                        "output_png": "figures/paper_E/weekend_failure_comparison.png",
                        "ledgers": [
                            "results/ledgers/BP_Mobility_Chicago_Corridors/weekday_reference_seed0.json",
                            "results/ledgers/BP_Mobility_Chicago_Corridors/weekend_negative_seed0.json",
                            "results/ledgers/BP_Mobility_Downtown_Routing_Instability/reference_seed0.json",
                            "results/ledgers/BP_Mobility_NYC_East_Corridor/reference_seed0.json",
                        ],
                    },
                    {
                        "panel_id": "robustness_table",
                        "purpose": "Summarize the fixed robustness sweep as a JSON-backed table for Paper E.",
                        "summary_json": "results/application/BP_Mobility_Chicago_Corridors/paper_e_application_summary.json",
                        "output_markdown": "figures/paper_E/robustness_summary.md",
                    },
                ],
            },
            indent=2,
        )
    )
