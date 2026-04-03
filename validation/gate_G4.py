"""Gate G4: weakly nonlinear extension."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import finalize_gate, gate_context, main_dump


def evaluate(root: Path | None = None) -> dict:
    root, criteria, records = gate_context("G4", root)
    if not records:
        return finalize_gate(root, "G4", criteria, records, False, {}, "No nonlinear evidence records were found.")
    primary_records = [record for record in records if record["benchmark_id"] == "BP_Weakly_Nonlinear_Slow_Manifold"]
    if not primary_records:
        return finalize_gate(
            root,
            "G4",
            criteria,
            records,
            False,
            {"record_count": len(records)},
            "No primary BP_Weakly_Nonlinear_Slow_Manifold evidence record was found.",
        )
    record = primary_records[0]
    local_validity = record["observables"].get("local_validity_metrics") or {}
    pair_records = [record for record in records if record["benchmark_id"] == "BP_T4_Local_Validity_Pair"]
    pair_reference = next((record for record in pair_records if record.get("parameter_id") == "reference"), None)
    pair_local = {}
    pair_transport = {}
    pair_summary = {}
    if pair_reference is not None:
        pair_local = pair_reference["observables"].get("local_validity_metrics") or {}
        pair_transport = pair_reference["observables"].get("transportability_metrics") or {}
        pair_summary = pair_transport.get("local_validity_pair", {})
    metrics = {
        "record_count": len(primary_records),
        "reported_record_count": len(records),
        "best_law": record["law_selection_summary"]["best_law"],
        "projector_deformation": float(record["observables"]["projector_deformation"] or 0.0),
        "autonomy_horizon": float(record["observables"]["autonomy_horizon"] or 0.0),
        "local_validity_margin": float(local_validity.get("local_validity_margin", 0.0)),
        "fast_slaving_defect": float(local_validity.get("fast_slaving_defect", 0.0)),
        "anchor_projector_deformation": float(local_validity.get("anchor_projector_deformation", 0.0)),
        "nonlinear_pair_count": len(pair_records),
        "breakdown_local_validity_margin": float(pair_local.get("local_validity_margin", 0.0)),
        "breakdown_fast_slaving_defect": float(pair_local.get("fast_slaving_defect", 0.0)),
        "breakdown_anchor_projector_deformation": float(pair_local.get("anchor_projector_deformation", 0.0)),
        "nonlinear_pair_margin_delta": float(
            pair_summary.get("paired_local_validity_margin", 0.0) - pair_summary.get("current_local_validity_margin", 0.0)
        ),
    }
    passed = (
        metrics["best_law"] == criteria["required_best_law"]
        and metrics["projector_deformation"] <= criteria["max_projector_deformation"]
        and metrics["autonomy_horizon"] >= criteria["min_autonomy_horizon"]
    )
    return finalize_gate(root, "G4", criteria, records, passed, metrics, "Nonlinear extension gate completed.")


if __name__ == "__main__":
    main_dump(evaluate())
