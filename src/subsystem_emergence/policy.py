"""Centralized acceptance and failure-policy loading."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from subsystem_emergence.core.types import AcceptanceDecision, AcceptanceProfile, BenchmarkCaseDefinition
from subsystem_emergence.io.paths import repository_root


def load_acceptance_policy(path: str | Path | None = None) -> dict:
    """Load the centralized acceptance-policy document."""

    policy_path = Path(path) if path is not None else repository_root() / "validation" / "acceptance_profiles.yaml"
    return yaml.safe_load(policy_path.read_text())


def failure_taxonomy_thresholds(
    profile_id: str = "default",
    path: str | Path | None = None,
) -> dict[str, float]:
    """Return one named failure-taxonomy threshold set."""

    policy = load_acceptance_policy(path)
    profiles = policy.get("failure_taxonomy_profiles", {})
    try:
        return deepcopy(profiles[profile_id])
    except KeyError as exc:
        raise KeyError(f"unknown failure taxonomy profile: {profile_id!r}") from exc


def acceptance_profile(profile_id: str, path: str | Path | None = None) -> AcceptanceProfile:
    """Return one named acceptance profile."""

    policy = load_acceptance_policy(path)
    profiles = policy.get("acceptance_profiles", {})
    try:
        payload = profiles[profile_id]
    except KeyError as exc:
        raise KeyError(f"unknown acceptance profile: {profile_id!r}") from exc
    return AcceptanceProfile(
        profile_id=profile_id,
        decision_mode=payload["decision_mode"],
        metric_rules=list(payload.get("metric_rules", [])),
        blocking_failure_labels=list(payload.get("blocking_failure_labels", [])),
        advisory_failure_labels=list(payload.get("advisory_failure_labels", [])),
        notes=list(payload.get("notes", [])),
    )


def _resolve_path(payload: dict[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for token in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(token)
        else:
            current = getattr(current, token)
    return current


def _check_rule(value: Any, operator: str, threshold: Any) -> bool:
    if value is None:
        return False
    numeric = float(value)
    numeric_threshold = float(threshold)
    if operator == "gte":
        return numeric >= numeric_threshold
    if operator == "lte":
        return numeric <= numeric_threshold
    if operator == "gt":
        return numeric > numeric_threshold
    if operator == "lt":
        return numeric < numeric_threshold
    if operator == "eq":
        return numeric == numeric_threshold
    raise KeyError(f"unsupported rule operator: {operator!r}")


def evaluate_case_acceptance(
    record: dict[str, Any],
    case_definition: BenchmarkCaseDefinition,
    *,
    policy_path: str | Path | None = None,
) -> AcceptanceDecision:
    """Evaluate one run against its named acceptance profile and expected role."""

    profile = acceptance_profile(case_definition.acceptance_profile, policy_path)
    failure_labels = sorted(str(label) for label in record.get("failure_labels", []))
    blocking_failures = sorted(set(failure_labels).intersection(profile.blocking_failure_labels))
    advisory_failures = sorted(set(failure_labels).intersection(profile.advisory_failure_labels))

    metrics: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    failing_rules: list[str] = []
    for rule in profile.metric_rules:
        metric_id = str(rule["metric_id"])
        value = _resolve_path(record, str(rule["path"]))
        passed = _check_rule(value, str(rule["operator"]), rule["threshold"])
        metrics[metric_id] = value
        checks[metric_id] = passed
        if not passed:
            failing_rules.append(metric_id)
    checks["blocking_failure_labels"] = not blocking_failures

    reasons: list[str] = []
    if blocking_failures:
        reasons.extend(f"blocking_failure_label:{label}" for label in blocking_failures)
    reasons.extend(f"metric_rule_failed:{metric_id}" for metric_id in failing_rules)

    expected_failures = sorted(set(case_definition.expected_failure_modes).intersection(failure_labels))
    if profile.decision_mode == "positive":
        success = not reasons
        decision_status = "accepted" if success else "rejected"
    elif profile.decision_mode == "expected_failure":
        expected_failure_checks = [checks[str(rule["metric_id"])] for rule in profile.metric_rules]
        success = bool(
            expected_failures
            or blocking_failures
            or (expected_failure_checks and all(expected_failure_checks))
        )
        decision_status = "expected_failure_confirmed" if success else "unexpected_pass"
        if not success:
            reasons.append("expected_failure_not_observed")
    elif profile.decision_mode == "qualified":
        success = not reasons
        decision_status = "qualified" if success else "rejected"
    else:
        raise KeyError(f"unsupported decision mode: {profile.decision_mode!r}")

    return AcceptanceDecision(
        benchmark_id=str(record["benchmark_id"]),
        case_id=case_definition.case_id,
        acceptance_profile=profile.profile_id,
        decision_mode=profile.decision_mode,
        decision_status=decision_status,
        success=success,
        checks=checks,
        metrics=metrics,
        blocking_failures_present=blocking_failures,
        advisory_failures_present=advisory_failures,
        failure_labels=failure_labels,
        reasons=reasons,
        notes=list(profile.notes),
    )
