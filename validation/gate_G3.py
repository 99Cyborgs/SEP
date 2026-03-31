"""Gate G3: finite-time transport."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import finalize_gate, gate_context, main_dump


def evaluate() -> dict:
    root, criteria, records = gate_context("G3")
    if not records:
        return finalize_gate(root, "G3", criteria, records, False, {}, "No transport ledgers were found.")
    primary_records = [record for record in records if record["benchmark_id"] == "BP_Windowed_Transport_Flow"]
    if not primary_records:
        return finalize_gate(
            root,
            "G3",
            criteria,
            records,
            False,
            {"record_count": len(records)},
            "No primary BP_Windowed_Transport_Flow ledger was found.",
        )
    record = primary_records[0]
    transport = record["observables"]["transportability_metrics"] or {}
    window_sensitivity = transport.get("window_sensitivity", {})
    mixed_records = [record for record in records if record["benchmark_id"] == "BP_T3_Window_Sensitivity_Pair"]
    mixed_reference = next((record for record in mixed_records if record.get("parameter_id") == "reference"), None)
    mixed_transport = {}
    mixed_window = {}
    if mixed_reference is not None:
        mixed_transport = mixed_reference["observables"]["transportability_metrics"] or {}
        mixed_window = mixed_transport.get("window_sensitivity", {})
    mixed_pair = mixed_transport.get("positive_negative_transport_pair", {})
    metrics = {
        "record_count": len(primary_records),
        "reported_record_count": len(records),
        "singular_gap": float(record["observables"]["singular_gap"] or 0.0),
        "horizon_gain": float(transport.get("coherent_vs_frozen_horizon_gain", 0.0)),
        "autonomy_horizon": float(record["observables"]["autonomy_horizon"] or 0.0),
        "window_sensitivity_autonomy_span": float(window_sensitivity.get("autonomy_horizon_relative_span", 0.0)),
        "window_sensitivity_horizon_gain_span": float(window_sensitivity.get("horizon_gain_relative_span", 0.0)),
        "window_sensitivity_regrouped_horizon_gain": float(window_sensitivity.get("regrouped_horizon_gain", 0.0)),
        "window_sensitivity_regrouped_carrier_mean_deformation": float(
            window_sensitivity.get("regrouped_carrier_mean_deformation", 0.0)
        ),
        "mixed_transport_pair_count": len(mixed_records),
        "mixed_transport_horizon_gain": float(mixed_transport.get("coherent_vs_frozen_horizon_gain", 0.0)),
        "mixed_transport_carrier_deformation": float(mixed_transport.get("carrier_tracking", {}).get("mean_deformation", 0.0)),
        "mixed_transport_regrouped_horizon_gain": float(mixed_window.get("regrouped_horizon_gain", 0.0)),
        "mixed_transport_pair_horizon_delta": float(
            mixed_pair.get("paired_horizon_gain", 0.0) - mixed_pair.get("current_horizon_gain", 0.0)
        ),
        "mixed_transport_pair_carrier_delta": float(
            mixed_pair.get("current_carrier_deformation", 0.0) - mixed_pair.get("paired_carrier_deformation", 0.0)
        ),
    }
    passed = (
        metrics["singular_gap"] >= criteria["min_singular_gap"]
        and metrics["horizon_gain"] >= criteria["min_horizon_gain"]
        and metrics["autonomy_horizon"] >= criteria["min_autonomy_horizon"]
    )
    return finalize_gate(root, "G3", criteria, records, passed, metrics, "Finite-time transport gate completed.")


if __name__ == "__main__":
    main_dump(evaluate())
