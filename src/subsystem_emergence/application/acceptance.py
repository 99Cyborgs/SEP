"""Backward-compatible acceptance helpers routed through centralized policy."""

from __future__ import annotations

from pathlib import Path

from subsystem_emergence.io.registry import benchmark_case_definition
from subsystem_emergence.policy import acceptance_profile, evaluate_case_acceptance


def application_acceptance_profile(profile_id: str) -> dict:
    """Backward-compatible named-profile lookup."""

    return acceptance_profile(profile_id).to_dict()


def evaluate_application_acceptance(
    record: dict,
    *,
    registry_path: str | Path | None = None,
    policy_path: str | Path | None = None,
) -> dict:
    """Evaluate acceptance for an application record through the centralized policy layer."""

    case_definition = benchmark_case_definition(
        str(record["benchmark_id"]),
        str(record.get("case_id") or record["parameter_id"]),
        path=registry_path,
    )
    decision = evaluate_case_acceptance(record, case_definition, policy_path=policy_path).to_dict()
    return {
        **decision,
        "accepted": decision["decision_status"] in {"accepted", "qualified"},
        "rejection_reasons": list(decision["reasons"]),
        "blocking_failure_labels": list(decision["blocking_failures_present"]),
        "advisory_failure_labels": list(decision["advisory_failures_present"]),
    }
