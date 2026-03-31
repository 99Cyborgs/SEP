"""List the figure scripts relevant to BP_T2_Same_Spectrum_Pair."""

from __future__ import annotations

import json


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "benchmark_id": "BP_T2_Same_Spectrum_Pair",
                "recommended_scripts": [
                    "figures/scripts/plot_t2_same_spectrum_counterexample.py",
                    "figures/scripts/plot_t2_pseudospectral_proxy.py",
                    "figures/scripts/plot_law_comparison.py"
                ]
            },
            indent=2,
        )
    )
