"""Print the reference parameter set for BP_Windowed_Transport_Flow."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from subsystem_emergence.benchmarking import sample_parameters


if __name__ == "__main__":
    print(sample_parameters("BP_Windowed_Transport_Flow"))
