"""Typed records used across the repository."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


JsonDict = dict[str, Any]


@dataclass(slots=True)
class ObservableDefinition:
    """Machine-readable observable definition."""

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
    """Serialized failure label with numerical evidence."""

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
    """Gate outcome plus serialized criteria and metrics."""

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
class BenchmarkDefinition:
    """Registry entry for a benchmark family."""

    benchmark_id: str
    branch: str
    theorem_tier: str
    description: str
    spec_path: str
    readme_path: str
    reference_script: str
    expected_metrics_path: str
    figure_recipe_path: str

    def to_dict(self) -> JsonDict:
        return asdict(self)
