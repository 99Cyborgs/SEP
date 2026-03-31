from __future__ import annotations

from subsystem_emergence.benchmarking import run_reference_benchmark


def test_linear_reference_smoke() -> None:
    record = run_reference_benchmark("BP_Linear_Two_Block", seed=3)
    assert record["observables"]["spectral_gap"] is not None
    assert len(record["observables"]["leakage_trajectory"]) > 3
    assert record["law_selection_summary"]["best_law"] in {"L1", "L2", "L3"}
