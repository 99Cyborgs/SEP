"""Run the BP_T5_Stochastic_Stress_Pair stressed reference configuration."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from subsystem_emergence.benchmarking import run_reference_benchmark


if __name__ == "__main__":
    print(run_reference_benchmark("BP_T5_Stochastic_Stress_Pair", parameter_id="reference"))
