"""Run the fixed mobility application validation matrix."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from subsystem_emergence.benchmarking import run_mobility_application_evaluation


if __name__ == "__main__":
    print(json.dumps(run_mobility_application_evaluation(seed=0), indent=2))
