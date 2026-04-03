"""Typed serialization contracts shared across evidence, validation, and reports.

These dataclasses are audit-facing schema objects. Field names and default
shapes are part of the repository's on-disk contract and should remain stable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


JsonDict = dict[str, Any]


@dataclass(slots=True)
class ObservableDefinition:
    """Machine-readable observable schema entry serialized into catalogs and reports."""

    key: str
    name: str
    symbol: str
    definition: str
    units: str
    norm_convention: str
    diagnostic_status: str
    estimation_procedure: str
    acceptance_tolerance: str | None = None

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class FailureReport:
    """Serialized failure label plus the numerical evidence that triggered it."""

    label: str
    triggered: bool
    metric: float | None
    threshold: float | None
    direction: str
    message: str
    archive_path: str = ""

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class GateResult:
    """Canonical gate artifact payload written to JSON and Markdown reports."""

    gate: str
    passed: bool
    criteria: JsonDict
    summary: str
    metrics: JsonDict
    failure_labels: list[str] = field(default_factory=list)
    report_json: str = ""
    report_markdown: str = ""

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class ClaimDefinition:
    """Traceability anchor linking a machine-readable claim id to validation scope."""

    claim_id: str
    title: str
    claim_document_path: str
    gate: str
    observables: list[str]
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class BenchmarkCaseDefinition:
    """Canonical machine-readable declaration for one benchmark parameterization."""

    family_id: str
    case_id: str
    title: str
    parameter_id: str
    base_parameter_id: str
    role: str
    tier: str
    claim_status: str
    implementation_status: str
    evidence_class: str
    observables: list[str]
    fixtures: list[JsonDict]
    acceptance_profile: str
    expected_failure_modes: list[str]
    run_modes: list[str]
    tags: list[str] = field(default_factory=list)
    overrides: JsonDict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class BenchmarkDefinition:
    """Canonical registry entry for a benchmark family and its declared cases."""

    family_id: str
    title: str
    branch: str
    theorem_tier: str
    description: str
    phase: int
    system_class: str
    state_dimension: int | str
    formal_system: str
    implementation_status: str
    evidence_class: str
    claim_refs: list[str]
    observables: list[str]
    fixtures: list[JsonDict]
    expected_failure_modes: list[str]
    run_modes: list[str]
    tags: list[str]
    ground_truth_notes: list[str]
    spec_path: str
    readme_path: str
    reference_script: str
    legacy_expected_metrics_path: str = ""
    legacy_figure_recipe_path: str = ""
    cases: list[BenchmarkCaseDefinition] = field(default_factory=list)

    @property
    def benchmark_id(self) -> str:
        """Compatibility alias preserved for ledger and registry consumers."""

        return self.family_id

    def to_dict(self) -> JsonDict:
        payload = asdict(self)
        payload["benchmark_id"] = self.family_id
        return payload


@dataclass(slots=True)
class AcceptanceProfile:
    """Named acceptance policy shared across benchmark families."""

    profile_id: str
    decision_mode: str
    metric_rules: list[JsonDict]
    blocking_failure_labels: list[str] = field(default_factory=list)
    advisory_failure_labels: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class AcceptanceDecision:
    """Per-run acceptance verdict with machine-readable supporting checks."""

    benchmark_id: str
    case_id: str
    acceptance_profile: str
    decision_mode: str
    decision_status: str
    success: bool
    checks: JsonDict
    metrics: JsonDict
    blocking_failures_present: list[str] = field(default_factory=list)
    advisory_failures_present: list[str] = field(default_factory=list)
    failure_labels: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class RunManifest:
    """Canonical manifest for the evidence bundle produced by one case execution."""

    run_id: str
    persistence_model: str
    benchmark_id: str
    case_id: str
    parameter_id: str
    seed: int
    branch: str
    theorem_tier: str
    acceptance_profile: str
    claim_status: str
    implementation_status: str
    evidence_class: str
    decision_status: str
    artifact_paths: JsonDict
    compatibility_mode: str = "disabled"
    compatibility_artifacts: JsonDict = field(default_factory=dict)
    claim_refs: list[str] = field(default_factory=list)
    failure_labels: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return asdict(self)
