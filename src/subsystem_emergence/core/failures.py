"""Failure taxonomy and archive helpers."""

from __future__ import annotations

import json
from pathlib import Path

from .types import FailureReport


DEFAULT_FAILURE_TAXONOMY_THRESHOLDS = {
    "min_gap": 0.03,
    "max_projector_deformation": 0.35,
    "max_block_residual": 0.35,
    "max_transient_amplification": 6.0,
    "min_horizon_ratio": 0.45,
    "max_coordinate_sensitivity": 0.5,
    "max_refinement_span": 0.3,
}


FAILURE_ARCHIVE_MAP = {
    "gap_failure": "G1_linear_validity",
    "carrier_failure": "G1_linear_validity",
    "coupling_failure": "G1_linear_validity",
    "transient_growth_failure": "G2_nonnormal",
    "horizon_failure": "G3_transport",
    "coordinate_artifact_failure": "G6_application",
    "numerical_artifact_failure": "G6_application",
}


def evaluate_failure_signatures(record: dict, criteria: dict) -> list[FailureReport]:
    """Apply the repository-wide failure taxonomy to a benchmark record."""

    merged_criteria = {**DEFAULT_FAILURE_TAXONOMY_THRESHOLDS, **criteria}
    observables = record.get("observables", {})
    predicted_horizon = float(observables.get("predicted_autonomy_horizon") or 0.0)
    observed_horizon = float(observables.get("autonomy_horizon") or 0.0)
    coordinate_metrics = observables.get("coordinate_sensitivity_metrics") or {}
    refinement_metrics = observables.get("numerical_refinement_metrics") or {}
    candidate_gap = observables.get("spectral_gap")
    if candidate_gap is None:
        candidate_gap = observables.get("singular_gap")
    candidate_deformation = observables.get("projector_deformation")
    if candidate_deformation is None:
        candidate_deformation = observables.get("coherent_projector_deformation")
    sampled_horizon = 0.0
    if "times" in record.get("parameters", {}):
        sampled_horizon = float(max(record["parameters"]["times"]))
    elif "windows" in record.get("parameters", {}):
        sampled_horizon = float(max(record["parameters"]["windows"]))
    comparison_horizon = predicted_horizon
    if comparison_horizon > 0.0 and sampled_horizon > 0.0:
        comparison_horizon = min(comparison_horizon, sampled_horizon)
    horizon_ratio = observed_horizon / comparison_horizon if comparison_horizon > 0.0 else 1.0
    reports = [
        FailureReport(
            label="gap_failure",
            triggered=(
                candidate_gap is not None and float(candidate_gap) < float(merged_criteria["min_gap"])
            ),
            metric=float(candidate_gap) if candidate_gap is not None else None,
            threshold=float(merged_criteria["min_gap"]),
            direction="lt",
            message="Slow-mode separation is below the admissible gate threshold.",
        ),
        FailureReport(
            label="carrier_failure",
            triggered=(
                candidate_deformation is not None
                and float(candidate_deformation) > float(merged_criteria["max_projector_deformation"])
            ),
            metric=float(candidate_deformation) if candidate_deformation is not None else None,
            threshold=float(merged_criteria["max_projector_deformation"]),
            direction="gt",
            message="Estimated carrier is too far from the planted or baseline carrier.",
        ),
        FailureReport(
            label="coupling_failure",
            triggered=(
                observables.get("block_residual_norm") is not None
                and float(observables["block_residual_norm"]) > float(merged_criteria["max_block_residual"])
            ),
            metric=float(observables["block_residual_norm"])
            if observables.get("block_residual_norm") is not None
            else None,
            threshold=float(merged_criteria["max_block_residual"]),
            direction="gt",
            message="Reduced slow dynamics is too strongly coupled for the claimed regime.",
        ),
        FailureReport(
            label="transient_growth_failure",
            triggered=(
                observables.get("transient_amplification_score") is not None
                and float(observables["transient_amplification_score"])
                > float(merged_criteria["max_transient_amplification"])
            ),
            metric=float(observables["transient_amplification_score"])
            if observables.get("transient_amplification_score") is not None
            else None,
            threshold=float(merged_criteria["max_transient_amplification"]),
            direction="gt",
            message="Transient amplification exceeds the admissible gate threshold.",
        ),
        FailureReport(
            label="horizon_failure",
            triggered=horizon_ratio < float(merged_criteria["min_horizon_ratio"]),
            metric=horizon_ratio,
            threshold=float(merged_criteria["min_horizon_ratio"]),
            direction="lt",
            message="Observed autonomy horizon is too short relative to the affine prediction.",
        ),
        FailureReport(
            label="coordinate_artifact_failure",
            triggered=float(coordinate_metrics.get("max_relative_change", 0.0))
            > float(merged_criteria["max_coordinate_sensitivity"]),
            metric=float(coordinate_metrics.get("max_relative_change", 0.0)),
            threshold=float(merged_criteria["max_coordinate_sensitivity"]),
            direction="gt",
            message="Coordinate sensitivity is too large for a robust subsystem claim.",
        ),
        FailureReport(
            label="numerical_artifact_failure",
            triggered=float(refinement_metrics.get("max_relative_span", 0.0))
            > float(merged_criteria["max_refinement_span"]),
            metric=float(refinement_metrics.get("max_relative_span", 0.0)),
            threshold=float(merged_criteria["max_refinement_span"]),
            direction="gt",
            message="Observable variation across refinement levels is too large.",
        ),
    ]
    return reports


def archive_failure_reports(root: Path, gate: str, record: dict, reports: list[FailureReport]) -> list[str]:
    """Archive triggered failure reports in the expected gate directories."""

    archived_paths: list[str] = []
    benchmark_id = record["benchmark_id"]
    parameter_id = record["parameter_id"]
    seed = record["seed"]
    for report in reports:
        if not report.triggered:
            continue
        archive_dir = root / "failures" / FAILURE_ARCHIVE_MAP.get(report.label, gate)
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / f"{benchmark_id}_{parameter_id}_seed{seed}_{report.label}.json"
        report.archive_path = str(archive_path.relative_to(root))
        archive_path.write_text(json.dumps(report.to_dict(), indent=2))
        archived_paths.append(report.archive_path)
    return archived_paths
