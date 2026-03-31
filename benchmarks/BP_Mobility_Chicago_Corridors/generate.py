"""Print the bundled parameter sets for BP_Mobility_Chicago_Corridors."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from subsystem_emergence.application.mobility import mobility_evaluation_cases
from subsystem_emergence.benchmarking import sample_parameters


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "reference": sample_parameters("BP_Mobility_Chicago_Corridors", parameter_id="reference"),
                "negative_weekend": sample_parameters("BP_Mobility_Chicago_Corridors", parameter_id="negative_weekend"),
                "evaluation_cases": mobility_evaluation_cases(),
            },
            indent=2,
        )
    )
