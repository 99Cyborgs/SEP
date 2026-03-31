"""Gate G2: nonnormal correction."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import finalize_gate, gate_context, main_dump


def evaluate() -> dict:
    root, criteria, records = gate_context("G2")
    if not records:
        return finalize_gate(root, "G2", criteria, records, False, {}, "No nonnormal ledgers were found.")
    evaluation_records = [
        record
        for record in records
        if not (
            record["benchmark_id"] == "BP_T2_Same_Spectrum_Pair"
            and record["parameter_id"] == "matched_normal"
        )
    ]
    delay_records = [record for record in records if record["benchmark_id"] == "BP_Delay_Coupled_Pair"]
    delay_metrics = [record["observables"].get("delay_semigroup_metrics") or {} for record in delay_records]
    proxy_values = [
        float(record["observables"].get("pseudospectral_proxy", 0.0))
        for record in records
        if record["observables"].get("pseudospectral_proxy") is not None
    ]
    counterexample_records = [
        record
        for record in records
        if record["benchmark_id"] == "BP_T2_Same_Spectrum_Pair" and record["parameter_id"] == "reference"
    ]
    transient_ok = all(
        float(record["observables"]["transient_amplification_score"] or 0.0) >= criteria["min_transient_amplification"]
        for record in evaluation_records
    )
    law_ok = any(
        record["law_selection_summary"]["best_law"] == criteria["required_best_law"]
        for record in evaluation_records
    ) and all(record["law_selection_summary"]["best_law"] != "L1" for record in evaluation_records)
    improvement_ok = all(
        float(record["law_selection_summary"]["improvement_over_l1"]) >= criteria["min_improvement_over_l1"]
        for record in evaluation_records
    )
    delay_refinement_ok = all(
        float(record["observables"]["numerical_refinement_metrics"].get("autonomy_horizon_relative_span", 0.0))
        <= criteria["max_delay_horizon_span"]
        and float(record["observables"]["numerical_refinement_metrics"].get("transient_relative_span", 0.0))
        <= criteria["max_delay_transient_span"]
        and float(record["observables"]["numerical_refinement_metrics"].get("block_residual_relative_span", 0.0))
        <= criteria["max_delay_residual_span"]
        and float(record["observables"]["numerical_refinement_metrics"].get("surrogate_relative_span", 0.0))
        <= criteria["max_delay_surrogate_variation"]
        for record in delay_records
    )
    metrics = {
        "record_count": len(evaluation_records),
        "reported_record_count": len(records),
        "transient_ok": transient_ok,
        "law_ok": law_ok,
        "improvement_ok": improvement_ok,
        "delay_record_count": len(delay_records),
        "delay_refinement_ok": delay_refinement_ok,
        "delay_horizon_span_max": float(
            max((metric.get("autonomy_horizon_span", 0.0) for metric in delay_metrics), default=0.0)
        ),
        "delay_transient_span_max": float(
            max((metric.get("transient_amplification_span", 0.0) for metric in delay_metrics), default=0.0)
        ),
        "delay_residual_span_max": float(
            max((metric.get("reduced_coupling_span", 0.0) for metric in delay_metrics), default=0.0)
        ),
        "delay_surrogate_span_max": float(
            max((metric.get("sampled_surrogate_span", 0.0) for metric in delay_metrics), default=0.0)
        ),
        "delay_correspondence_deformation_max": float(
            max(
                (
                    metric.get("bounded_correspondence_summary", {}).get("constant_history_projector_deformation", 0.0)
                    for metric in delay_metrics
                ),
                default=0.0,
            )
        ),
        "delay_adjacent_stability_max": float(
            max((metric.get("adjacent_terminal_projector_deformation_max", 0.0) for metric in delay_metrics), default=0.0)
        ),
        "pseudospectral_proxy_mean": float(sum(proxy_values) / len(proxy_values)) if proxy_values else 0.0,
        "pseudospectral_proxy_max": float(max(proxy_values)) if proxy_values else 0.0,
        "same_spectrum_counterexample_count": len(counterexample_records),
    }
    if counterexample_records:
        contrast = counterexample_records[0]["observables"]["transportability_metrics"]["same_spectrum_counterexample"]
        metrics["same_spectrum_gap_difference"] = float(contrast["gap_difference"])
        metrics["same_spectrum_transient_amplification_ratio"] = float(contrast["transient_amplification_ratio"])
        metrics["same_spectrum_l3_minus_l1_rmse"] = float(contrast["current_l3_minus_l1_rmse"])
    passed = transient_ok and law_ok and improvement_ok and delay_refinement_ok
    return finalize_gate(
        root,
        "G2",
        criteria,
        records,
        passed,
        metrics,
        "Nonnormal correction gate completed, including delay semigroup correspondence evidence for the fixed-lag sampled-history path.",
    )


if __name__ == "__main__":
    main_dump(evaluate())
