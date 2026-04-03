"""Gate G5: stochastic robustness."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import finalize_gate, gate_context, main_dump


def evaluate(root: Path | None = None) -> dict:
    root, criteria, records = gate_context("G5", root)
    if not records:
        return finalize_gate(root, "G5", criteria, records, False, {}, "No stochastic evidence records were found.")
    primary_records = [record for record in records if record["benchmark_id"] == "BP_Noisy_Metastable_Network"]
    if not primary_records:
        return finalize_gate(
            root,
            "G5",
            criteria,
            records,
            False,
            {"record_count": len(records)},
            "No primary BP_Noisy_Metastable_Network evidence record was found.",
        )
    record = primary_records[0]
    transport = record["observables"]["transportability_metrics"] or {}
    uncertainty = record["observables"].get("stochastic_uncertainty_metrics") or {}
    pair_records = [record for record in records if record["benchmark_id"] == "BP_T5_Stochastic_Stress_Pair"]
    pair_reference = next((record for record in pair_records if record.get("parameter_id") == "reference"), None)
    pair_uncertainty = {}
    pair_transport = {}
    pair_summary = {}
    if pair_reference is not None:
        pair_uncertainty = pair_reference["observables"].get("stochastic_uncertainty_metrics") or {}
        pair_transport = pair_reference["observables"].get("transportability_metrics") or {}
        pair_summary = pair_transport.get("stochastic_uncertainty_pair", {})
    width = float(transport.get("bootstrap_ci_upper", 0.0)) - float(transport.get("bootstrap_ci_lower", 0.0))
    metrics = {
        "record_count": len(primary_records),
        "reported_record_count": len(records),
        "leakage_variance": float(record["observables"]["leakage_variance"] or 0.0),
        "bootstrap_width": width,
        "autonomy_horizon": float(record["observables"]["autonomy_horizon"] or 0.0),
        "confidence_bounded_horizon": float(uncertainty.get("confidence_bounded_horizon", 0.0)),
        "estimation_error_proxy": float(uncertainty.get("estimation_error_proxy", 0.0)),
        "stochastic_pair_count": len(pair_records),
        "stress_bootstrap_width": float(pair_uncertainty.get("bootstrap_width", 0.0)),
        "stress_confidence_bounded_horizon": float(pair_uncertainty.get("confidence_bounded_horizon", 0.0)),
        "stochastic_pair_width_delta": float(
            pair_summary.get("current_bootstrap_width", 0.0) - pair_summary.get("paired_bootstrap_width", 0.0)
        ),
    }
    passed = (
        metrics["leakage_variance"] <= criteria["max_leakage_variance"]
        and metrics["bootstrap_width"] <= criteria["max_bootstrap_width"]
        and metrics["autonomy_horizon"] >= criteria["min_autonomy_horizon"]
    )
    return finalize_gate(root, "G5", criteria, records, passed, metrics, "Stochastic robustness gate completed.")


if __name__ == "__main__":
    main_dump(evaluate())
