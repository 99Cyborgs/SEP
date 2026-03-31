"""Print the bundled parameter sets for BP_Clickstream_Docs_Funnel."""

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
                "reference": sample_parameters("BP_Clickstream_Docs_Funnel", parameter_id="reference"),
                "negative_detour": sample_parameters("BP_Clickstream_Docs_Funnel", parameter_id="negative_detour"),
            },
            indent=2,
        )
    )
