"""Gate G6: application evidence and identifiability."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import finalize_gate, gate_context, main_dump
from subsystem_emergence.application.acceptance import evaluate_application_acceptance


def _case_key(benchmark_id: str, parameter_id: str, seed: int) -> tuple[str, str, int]:
    return benchmark_id, parameter_id, seed


def _evaluate_required_application_cases(application_records: list[dict], required_cases: list[dict]) -> tuple[list[dict], list[dict]]:
    indexed_records = {
        _case_key(str(record["benchmark_id"]), str(record["parameter_id"]), int(record["seed"])): record
        for record in application_records
    }
    evaluated_cases: list[dict] = []
    missing_cases: list[dict] = []
    for requirement in required_cases:
        key = _case_key(
            str(requirement["benchmark_id"]),
            str(requirement["parameter_id"]),
            int(requirement.get("seed", 0)),
        )
        record = indexed_records.get(key)
        if record is None:
            missing_cases.append(
                {
                    "benchmark_id": requirement["benchmark_id"],
                    "parameter_id": requirement["parameter_id"],
                    "seed": int(requirement.get("seed", 0)),
                    "expected_status": requirement["expected_status"],
                }
            )
            continue
        status = evaluate_application_acceptance(record)
        evaluated_cases.append(
            {
                "benchmark_id": record["benchmark_id"],
                "parameter_id": record["parameter_id"],
                "seed": int(record["seed"]),
                "expected_status": requirement["expected_status"],
                "observed_status": "accepted" if status["accepted"] else "rejected",
                "accepted": status["accepted"],
                "acceptance_profile": status["acceptance_profile"],
                "rejection_reasons": status["rejection_reasons"],
                "failure_labels": status["failure_labels"],
                "metrics": status["metrics"],
            }
        )
    return evaluated_cases, missing_cases


def evaluate(root: Path | None = None) -> dict:
    root, criteria, records = gate_context("G6", root)
    if not records:
        return finalize_gate(root, "G6", criteria, records, False, {}, "No evidence records were found for identifiability checks.")
    primary_benchmark_ids = set(criteria.get("primary_benchmark_ids", criteria["benchmark_ids"]))
    application_benchmark_ids = set(criteria.get("application_benchmark_ids", []))
    primary_thresholds = criteria.get("primary_identifiability_thresholds", {})
    application_evidence = criteria.get("application_evidence", {})
    primary_records = [record for record in records if record["benchmark_id"] in primary_benchmark_ids]
    application_records = [record for record in records if record["benchmark_id"] in application_benchmark_ids]
    primary_benchmark_coverage_count = len({record["benchmark_id"] for record in primary_records})
    primary_records_present = primary_benchmark_coverage_count == len(primary_benchmark_ids)
    coordinate_ok = primary_records_present and all(
        float((record["observables"]["coordinate_sensitivity_metrics"] or {}).get("max_relative_change", 0.0))
        <= primary_thresholds["max_coordinate_sensitivity"]
        for record in primary_records
    )
    refinement_ok = primary_records_present and all(
        float((record["observables"]["numerical_refinement_metrics"] or {}).get("max_relative_span", 0.0))
        <= primary_thresholds["max_refinement_span"]
        for record in primary_records
    )
    application_statuses = [
        {
            "record": record,
            "status": evaluate_application_acceptance(record),
        }
        for record in application_records
    ]
    accepted_application_records = [item for item in application_statuses if item["status"]["accepted"]]
    rejected_application_records = [item for item in application_statuses if not item["status"]["accepted"]]
    required_cases = list(application_evidence.get("required_cases", []))
    evaluated_required_cases, missing_required_cases = _evaluate_required_application_cases(application_records, required_cases)
    mismatched_required_cases = [
        case
        for case in evaluated_required_cases
        if case["expected_status"] != case["observed_status"]
    ]
    expected_case_ok = not missing_required_cases and not mismatched_required_cases
    application_counts_ok = (
        len(accepted_application_records) >= int(application_evidence.get("min_accepted_cases", 0))
        and len(rejected_application_records) >= int(application_evidence.get("min_rejected_cases", 0))
    )
    application_mode = str(application_evidence.get("mode", "advisory"))
    application_enforced = application_mode == "enforced"
    application_enforcement_ok = expected_case_ok and application_counts_ok
    metrics = {
        "primary_record_count": len(primary_records),
        "primary_benchmark_coverage_count": primary_benchmark_coverage_count,
        "primary_records_present": primary_records_present,
        "reported_record_count": len(records),
        "coordinate_ok": coordinate_ok,
        "refinement_ok": refinement_ok,
        "primary_identifiability_enforced": True,
        "application_record_count": len(application_records),
        "application_evidence_mode": application_mode,
        "application_enforced": application_enforced,
        "application_enforcement_ok": application_enforcement_ok,
        "required_application_case_count": len(required_cases),
        "matched_application_case_count": int(
            sum(case["expected_status"] == case["observed_status"] for case in evaluated_required_cases)
        ),
        "mismatched_application_case_count": len(mismatched_required_cases),
        "missing_application_case_count": len(missing_required_cases),
        "accepted_application_case_count": len(accepted_application_records),
        "rejected_application_case_count": len(rejected_application_records),
        "application_failure_label_count": int(
            sum(1 for record in application_records if record.get("failure_labels"))
        ),
        "accepted_application_max_refinement_span": float(
            max(
                (
                    float(item["status"]["metrics"]["max_relative_span"])
                    for item in accepted_application_records
                ),
                default=0.0,
            )
        ),
        "application_case_outcomes": evaluated_required_cases,
        "missing_application_cases": missing_required_cases,
    }
    passed = coordinate_ok and refinement_ok and (not application_enforced or application_enforcement_ok)
    summary = (
        "Primary identifiability thresholds and the declared application evidence matrix were both enforced."
        if application_enforced
        else "Primary identifiability thresholds were enforced; application evidence was reported as advisory only."
    )
    return finalize_gate(root, "G6", criteria, records, passed, metrics, summary)


if __name__ == "__main__":
    main_dump(evaluate())
