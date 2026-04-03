"""List the figure scripts relevant to BP_Mobility_Chicago_Corridors."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_Mobility_Chicago_Corridors",
                "application_summary": "results/indexes/application_validation/BP_Mobility_Chicago_Corridors_validation_matrix.json",
                "package_manifest": "reports/archive/figures/paper_E/package_manifest.json",
                "panels": [
                    {
                        "panel_id": "weekday_leakage",
                        "purpose": "Show coherent leakage over the accepted weekday reference windows.",
                        "generator": "reports/archive/benchmark_scripts/generate_paper_e_package.py",
                        "output_png": "reports/archive/figures/paper_E/weekday_leakage.png",
                        "run_manifest": "results/evidence/BP_Mobility_Chicago_Corridors/reference/seed_0/run_manifest.json",
                    },
                    {
                        "panel_id": "weekday_horizon",
                        "purpose": "Compare observed and predicted horizons for the accepted weekday reference.",
                        "generator": "reports/archive/benchmark_scripts/generate_paper_e_package.py",
                        "output_png": "reports/archive/figures/paper_E/weekday_horizon.png",
                        "run_manifest": "results/evidence/BP_Mobility_Chicago_Corridors/reference/seed_0/run_manifest.json",
                    },
                    {
                        "panel_id": "negative_failure_comparison",
                        "purpose": "Show why the weekend-night and downtown slices are rejected and how the NYC corridor remains mixed while the weekday sweep remains usable.",
                        "generator": "reports/archive/benchmark_scripts/generate_paper_e_package.py",
                        "output_png": "reports/archive/figures/paper_E/weekend_failure_comparison.png",
                        "run_manifests": [
                            "results/evidence/BP_Mobility_Chicago_Corridors/reference/seed_0/run_manifest.json",
                            "results/evidence/BP_Mobility_Chicago_Corridors/negative_weekend/seed_0/run_manifest.json",
                            "results/evidence/BP_Mobility_Downtown_Routing_Instability/reference/seed_0/run_manifest.json",
                            "results/evidence/BP_Mobility_NYC_East_Corridor/reference/seed_0/run_manifest.json",
                        ],
                    },
                    {
                        "panel_id": "robustness_table",
                        "purpose": "Summarize the fixed robustness sweep as a JSON-backed table for Paper E.",
                        "summary_json": "results/indexes/application_validation/BP_Mobility_Chicago_Corridors_validation_matrix.json",
                        "output_markdown": "reports/archive/figures/paper_E/robustness_summary.md",
                    },
                ],
            },
            indent=2,
        )
    )

