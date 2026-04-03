"""Gate G1: linear validity."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import finalize_gate, gate_context, main_dump


def evaluate(root: Path | None = None) -> dict:
    root, criteria, records = gate_context("G1", root)
    if not records:
        return finalize_gate(root, "G1", criteria, records, False, {}, "No linear evidence records were found.")
    gap_ok = all(float(record["observables"]["spectral_gap"]) >= criteria["min_gap"] for record in records)
    deformation_ok = all(
        float(record["observables"]["projector_deformation"] or 0.0) <= criteria["max_projector_deformation"]
        for record in records
    )
    residual_ok = all(
        float(record["observables"]["block_residual_norm"] or 0.0) <= criteria["max_block_residual"]
        for record in records
    )
    l1_ok = all(
        float(record["law_fits"]["L1"]["test_rmse"]) <= criteria["max_l1_test_rmse"]
        for record in records
    )
    horizon_ok = all(
        float(record["observables"]["autonomy_horizon"] or 0.0)
        / max(
            min(
                float(record["observables"]["predicted_autonomy_horizon"] or 1.0),
                float(max((record["parameters"].get("times") or record["parameters"].get("windows") or [1]))),
            ),
            1.0e-12,
        )
        >= criteria["min_horizon_ratio"]
        for record in records
    )
    metrics = {
        "record_count": len(records),
        "gap_ok": gap_ok,
        "deformation_ok": deformation_ok,
        "residual_ok": residual_ok,
        "l1_ok": l1_ok,
        "horizon_ok": horizon_ok,
    }
    passed = all(metrics[key] for key in ("gap_ok", "deformation_ok", "residual_ok", "l1_ok", "horizon_ok"))
    return finalize_gate(root, "G1", criteria, records, passed, metrics, "Linear validity gate completed.")


if __name__ == "__main__":
    main_dump(evaluate())
