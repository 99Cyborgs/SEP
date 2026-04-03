"""Canonical benchmark-registry IO helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from subsystem_emergence.core.types import BenchmarkCaseDefinition, BenchmarkDefinition, ClaimDefinition
from subsystem_emergence.io.paths import repository_root


def load_registry(path: str | Path | None = None) -> dict:
    """Load the canonical benchmark registry YAML file."""

    registry_path = Path(path) if path is not None else repository_root() / "benchmarks" / "registry.yaml"
    return yaml.safe_load(registry_path.read_text())


def claim_definitions(path: str | Path | None = None) -> list[ClaimDefinition]:
    """Return typed claim definitions from the canonical registry."""

    data = load_registry(path)
    return [
        ClaimDefinition(
            claim_id=item["claim_id"],
            title=item["title"],
            claim_document_path=item["claim_document_path"],
            gate=item["gate"],
            observables=list(item.get("observables", [])),
            tags=list(item.get("tags", [])),
        )
        for item in data.get("claims", [])
    ]


def benchmark_definitions(path: str | Path | None = None) -> list[BenchmarkDefinition]:
    """Return typed benchmark definitions from the canonical registry."""

    data = load_registry(path)
    definitions: list[BenchmarkDefinition] = []
    for item in data["benchmarks"]:
        cases = [
            BenchmarkCaseDefinition(
                family_id=item["family_id"],
                case_id=case["case_id"],
                title=case["title"],
                parameter_id=str(case.get("parameter_id", case["case_id"])),
                base_parameter_id=str(case.get("base_parameter_id", case.get("parameter_id", case["case_id"]))),
                role=case["role"],
                tier=str(case.get("tier", item["tier"])),
                claim_status=case["claim_status"],
                implementation_status=case.get("implementation_status", item["implementation_status"]),
                evidence_class=case.get("evidence_class", item["evidence_class"]),
                observables=list(case.get("observables", item.get("observables", []))),
                fixtures=list(case.get("fixtures", item.get("fixtures", []))),
                acceptance_profile=case["acceptance_profile"],
                expected_failure_modes=list(case.get("expected_failure_modes", item.get("expected_failure_modes", []))),
                run_modes=list(case.get("run_modes", item.get("run_modes", []))),
                tags=list(case.get("tags", [])),
                overrides=dict(case.get("overrides", {})),
                notes=list(case.get("notes", [])),
            )
            for case in item.get("cases", [])
        ]
        definitions.append(
            BenchmarkDefinition(
                family_id=item["family_id"],
                title=item["title"],
                branch=item["branch"],
                theorem_tier=item["tier"],
                description=item["description"],
                phase=int(item["phase"]),
                system_class=item["system_class"],
                state_dimension=item["state_dimension"],
                formal_system=item["formal_system"],
                implementation_status=item["implementation_status"],
                evidence_class=item["evidence_class"],
                claim_refs=list(item.get("claim_refs", [])),
                observables=list(item.get("observables", [])),
                fixtures=list(item.get("fixtures", [])),
                expected_failure_modes=list(item.get("expected_failure_modes", [])),
                run_modes=list(item.get("run_modes", [])),
                tags=list(item.get("tags", [])),
                ground_truth_notes=list(item.get("ground_truth_notes", [])),
                spec_path=item["spec_path"],
                readme_path=item["readme_path"],
                reference_script=item["reference_script"],
                legacy_expected_metrics_path=item.get("legacy_expected_metrics_path", ""),
                legacy_figure_recipe_path=item.get("legacy_figure_recipe_path", ""),
                cases=cases,
            )
        )
    return definitions


def benchmark_definition(benchmark_id: str, path: str | Path | None = None) -> BenchmarkDefinition:
    """Return one benchmark family definition by id."""

    for definition in benchmark_definitions(path):
        if definition.family_id == benchmark_id:
            return definition
    raise KeyError(f"unknown benchmark family: {benchmark_id}")


def benchmark_case_definition(
    benchmark_id: str,
    case_id: str,
    path: str | Path | None = None,
) -> BenchmarkCaseDefinition:
    """Return one benchmark case definition by family id and case id."""

    definition = benchmark_definition(benchmark_id, path)
    for case in definition.cases:
        if case.case_id == case_id or case.parameter_id == case_id:
            return case
    raise KeyError(f"unknown benchmark case for {benchmark_id!r}: {case_id!r}")


def default_case_id(benchmark_id: str, path: str | Path | None = None) -> str:
    """Return the canonical default case id for a benchmark family."""

    definition = benchmark_definition(benchmark_id, path)
    for case in definition.cases:
        if case.role == "reference":
            return case.case_id
    if not definition.cases:
        raise KeyError(f"benchmark family has no registered cases: {benchmark_id}")
    return definition.cases[0].case_id
