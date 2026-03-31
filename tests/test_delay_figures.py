from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from subsystem_emergence.benchmarking import run_reference_benchmark


def test_delay_refinement_figure_script_writes_output() -> None:
    run_reference_benchmark("BP_Delay_Coupled_Pair", seed=0)
    root = Path(__file__).resolve().parents[1]
    script = root / "figures" / "scripts" / "plot_delay_refinement_ladder.py"
    subprocess.run([sys.executable, str(script)], cwd=root, check=True)
    output = root / "figures" / "paper_C" / "delay_refinement_ladder.png"
    assert output.exists()
