"""Print the bundled parameter sets for BP_T2_Same_Spectrum_Pair."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from subsystem_emergence.benchmarking import sample_parameters


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "reference": sample_parameters("BP_T2_Same_Spectrum_Pair", parameter_id="reference"),
                "matched_normal": sample_parameters("BP_T2_Same_Spectrum_Pair", parameter_id="matched_normal"),
            },
            indent=2,
        )
    )
