"""Shared acceptance profiles for application-facing evidence."""

from __future__ import annotations

from copy import deepcopy

from subsystem_emergence.core.failures import DEFAULT_FAILURE_TAXONOMY_THRESHOLDS


APPLICATION_ACCEPTANCE_PROFILES = {
    "BP_Mobility_Chicago_Corridors": {
        "acceptance_profile": "paper_e_weekday_mobility",
        "package_acceptance_thresholds": {
            "min_singular_gap": 0.4,
            "max_coherent_projector_deformation": 0.4,
            "min_autonomy_horizon": 3.0,
            "max_refinement_span": 0.2,
        },
        "blocking_failure_labels": ["carrier_failure", "numerical_artifact_failure"],
        "advisory_failure_labels": ["coupling_failure"],
        "acceptance_notes": [
            "Hyde Park weekday acceptance is benchmark-local and allows coupling_failure to remain advisory.",
            "The package is accepted only when gap, deformation, horizon, and refinement remain within the declared Paper E bounds.",
        ],
    },
    "BP_Clickstream_Docs_Funnel": {
        "acceptance_profile": "cross_domain_navigation",
        "package_acceptance_thresholds": {
            "min_singular_gap": 0.35,
            "max_coherent_projector_deformation": 0.15,
            "min_autonomy_horizon": 3.0,
            "max_refinement_span": 0.2,
        },
        "blocking_failure_labels": ["carrier_failure", "coupling_failure", "numerical_artifact_failure"],
        "advisory_failure_labels": [],
        "acceptance_notes": [
            "The clickstream package is a bounded cross-domain acceptance overlay, not a theorem-grade positive family.",
        ],
    },
    "BP_Support_Portal_Funnel": {
        "acceptance_profile": "cross_domain_navigation",
        "package_acceptance_thresholds": {
            "min_singular_gap": 0.35,
            "max_coherent_projector_deformation": 0.15,
            "min_autonomy_horizon": 3.0,
            "max_refinement_span": 0.2,
        },
        "blocking_failure_labels": ["carrier_failure", "coupling_failure", "numerical_artifact_failure"],
        "advisory_failure_labels": [],
        "acceptance_notes": [
            "Support-navigation acceptance uses the same bounded navigation overlay as the clickstream benchmark.",
        ],
    },
    "BP_Workflow_Queue_Funnel": {
        "acceptance_profile": "cross_domain_workflow",
        "package_acceptance_thresholds": {
            "min_singular_gap": 0.27,
            "max_coherent_projector_deformation": 0.18,
            "min_autonomy_horizon": 3.0,
            "max_refinement_span": 0.2,
        },
        "blocking_failure_labels": ["carrier_failure", "coupling_failure", "numerical_artifact_failure"],
        "advisory_failure_labels": [],
        "acceptance_notes": [
            "Workflow acceptance is benchmark-local and slightly looser on the singular-gap floor than the navigation overlays.",
        ],
    },
    "BP_Mobility_Downtown_Routing_Instability": {
        "acceptance_profile": "paper_e_external_mobility",
        "package_acceptance_thresholds": {
            "min_singular_gap": 0.4,
            "max_coherent_projector_deformation": 0.4,
            "min_autonomy_horizon": 3.0,
            "max_refinement_span": 0.2,
        },
        "blocking_failure_labels": ["carrier_failure", "numerical_artifact_failure"],
        "advisory_failure_labels": ["coupling_failure"],
        "acceptance_notes": [
            "External mobility slices are still judged against the Hyde Park Paper E overlay and are expected to remain rejected here.",
        ],
    },
    "BP_Mobility_NYC_East_Corridor": {
        "acceptance_profile": "paper_e_external_mobility",
        "package_acceptance_thresholds": {
            "min_singular_gap": 0.4,
            "max_coherent_projector_deformation": 0.4,
            "min_autonomy_horizon": 3.0,
            "max_refinement_span": 0.2,
        },
        "blocking_failure_labels": ["carrier_failure", "numerical_artifact_failure"],
        "advisory_failure_labels": ["coupling_failure"],
        "acceptance_notes": [
            "The NYC corridor is tracked as mixed external evidence but remains package-rejected under the same acceptance overlay as Hyde Park.",
        ],
    },
}


def application_acceptance_profile(benchmark_id: str) -> dict:
    """Return the declared acceptance profile for one application benchmark."""

    try:
        return deepcopy(APPLICATION_ACCEPTANCE_PROFILES[benchmark_id])
    except KeyError as exc:
        raise KeyError(f"no application acceptance profile is defined for {benchmark_id!r}") from exc


def evaluate_application_acceptance(record: dict) -> dict:
    """Evaluate benchmark-local package acceptance for one application ledger."""

    profile = application_acceptance_profile(str(record["benchmark_id"]))
    observables = record["observables"]
    refinement = observables["numerical_refinement_metrics"]
    thresholds = profile["package_acceptance_thresholds"]
    failure_labels = sorted(record.get("failure_labels", []))
    blocking_failures = sorted(set(failure_labels).intersection(profile["blocking_failure_labels"]))
    advisory_failures = sorted(set(failure_labels).intersection(profile["advisory_failure_labels"]))
    checks = {
        "singular_gap": float(observables["singular_gap"]) >= thresholds["min_singular_gap"],
        "coherent_projector_deformation": float(observables["coherent_projector_deformation"])
        <= thresholds["max_coherent_projector_deformation"],
        "autonomy_horizon": float(observables["autonomy_horizon"]) >= thresholds["min_autonomy_horizon"],
        "max_relative_span": float(refinement["max_relative_span"]) <= thresholds["max_refinement_span"],
        "blocking_failure_labels": not blocking_failures,
    }
    rejection_reasons: list[str] = []
    if not checks["singular_gap"]:
        rejection_reasons.append("singular_gap_below_package_floor")
    if not checks["coherent_projector_deformation"]:
        rejection_reasons.append("carrier_deformation_above_package_ceiling")
    if not checks["autonomy_horizon"]:
        rejection_reasons.append("autonomy_horizon_below_package_floor")
    if not checks["max_relative_span"]:
        rejection_reasons.append("refinement_span_above_package_ceiling")
    rejection_reasons.extend(f"blocking_failure_label:{label}" for label in blocking_failures)
    return {
        "accepted": not rejection_reasons,
        "acceptance_profile": profile["acceptance_profile"],
        "package_acceptance_thresholds": thresholds,
        "taxonomy_thresholds": deepcopy(DEFAULT_FAILURE_TAXONOMY_THRESHOLDS),
        "blocking_failure_labels": list(profile["blocking_failure_labels"]),
        "blocking_failures_present": blocking_failures,
        "advisory_failure_labels": list(profile["advisory_failure_labels"]),
        "advisory_failures_present": advisory_failures,
        "metrics": {
            "singular_gap": float(observables["singular_gap"]),
            "coherent_projector_deformation": float(observables["coherent_projector_deformation"]),
            "autonomy_horizon": float(observables["autonomy_horizon"]),
            "max_relative_span": float(refinement["max_relative_span"]),
            "block_residual_norm": float(observables["block_residual_norm"]),
        },
        "checks": checks,
        "failure_labels": failure_labels,
        "rejection_reasons": rejection_reasons,
        "acceptance_notes": list(profile["acceptance_notes"]),
    }
