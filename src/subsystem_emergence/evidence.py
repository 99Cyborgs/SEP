"""Structured evidence-bundle writers, readers, and index builders."""

from __future__ import annotations

import json
import platform
import sys
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

import numpy as np

from subsystem_emergence.core.types import (
    AcceptanceDecision,
    BenchmarkCaseDefinition,
    BenchmarkDefinition,
    FailureReport,
    RunManifest,
)
from subsystem_emergence.io.paths import artifact_root, evidence_root, indexes_root, repo_relative_path
from subsystem_emergence.io.registry import benchmark_definitions, claim_definitions


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_ready(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2))


def evidence_bundle_dir(root: str | Path, benchmark_id: str, case_id: str, seed: int) -> Path:
    """Return the canonical evidence-bundle directory for one run."""

    return evidence_root(root) / benchmark_id / case_id / f"seed_{seed}"


def run_manifest_path(root: str | Path, benchmark_id: str, case_id: str, seed: int) -> Path:
    """Return the canonical run-manifest path for one run."""

    return evidence_bundle_dir(root, benchmark_id, case_id, seed) / "run_manifest.json"


def _package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for package_name in ("numpy", "scipy", "pandas", "matplotlib", "pyyaml"):
        try:
            versions[package_name] = importlib_metadata.version(package_name)
        except importlib_metadata.PackageNotFoundError:
            versions[package_name] = None
    return versions


def environment_fingerprint(record: dict[str, Any]) -> dict[str, Any]:
    """Build a machine-readable environment fingerprint for one run."""

    metadata = record.get("metadata", {})
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "python_implementation": platform.python_implementation(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "code_hash": metadata.get("code_hash"),
        "package_versions": _package_versions(),
    }


def write_evidence_bundle(
    root: str | Path,
    family_definition: BenchmarkDefinition,
    case_definition: BenchmarkCaseDefinition,
    record: dict[str, Any],
    decision: AcceptanceDecision,
    failure_reports: list[FailureReport],
) -> dict[str, str]:
    """Write the canonical evidence-bundle files for one run."""

    repo_root = artifact_root(root)
    bundle_dir = evidence_bundle_dir(repo_root, family_definition.family_id, case_definition.case_id, int(record["seed"]))
    bundle_dir.mkdir(parents=True, exist_ok=True)

    environment_path = bundle_dir / "environment_fingerprint.json"
    solver_path = bundle_dir / "solver_config.json"
    seed_path = bundle_dir / "seed_record.json"
    case_snapshot_path = bundle_dir / "benchmark_case_snapshot.json"
    observables_path = bundle_dir / "observables_summary.json"
    residuals_path = bundle_dir / "residual_diagnostics.json"
    gate_path = bundle_dir / "gate_report.json"
    decision_path = bundle_dir / "acceptance_decision.json"
    regression_path = bundle_dir / "regression_check.json"
    failure_path = bundle_dir / "failure_record.json"
    manifest_path = bundle_dir / "run_manifest.json"

    _write_json(environment_path, environment_fingerprint(record))
    _write_json(
        solver_path,
        {
            "solver": record["metadata"].get("solver"),
            "runtime_seconds": record["metadata"].get("runtime_seconds"),
            "code_hash": record["metadata"].get("code_hash"),
            "source_of_truth": record["metadata"].get("source_of_truth", {}),
        },
    )
    _write_json(
        seed_path,
        {
            "seed": int(record["seed"]),
            "parameter_id": record["parameter_id"],
            "base_parameter_id": case_definition.base_parameter_id,
            "resolved_parameters": record["parameters"],
        },
    )
    _write_json(
        case_snapshot_path,
        {
            "family": family_definition.to_dict(),
            "case": case_definition.to_dict(),
        },
    )
    _write_json(
        observables_path,
        {
            "benchmark_id": record["benchmark_id"],
            "case_id": case_definition.case_id,
            "observables": record["observables"],
        },
    )
    _write_json(
        residuals_path,
        {
            "law_fits": record.get("law_fits", {}),
            "law_selection_summary": record.get("law_selection_summary", {}),
            "notes": list(record.get("notes", [])),
        },
    )
    _write_json(
        gate_path,
        {
            "acceptance_profile": decision.acceptance_profile,
            "decision_mode": decision.decision_mode,
            "checks": decision.checks,
            "blocking_failures_present": decision.blocking_failures_present,
            "advisory_failures_present": decision.advisory_failures_present,
            "failure_labels": decision.failure_labels,
            "reasons": decision.reasons,
        },
    )
    _write_json(decision_path, decision.to_dict())
    _write_json(
        regression_path,
        {
            "expected_decision_mode": decision.decision_mode,
            "observed_decision_status": decision.decision_status,
            "successful_against_expectation": decision.success,
            "profile": decision.acceptance_profile,
            "reasons": decision.reasons,
        },
    )

    triggered_reports = [report.to_dict() for report in failure_reports if report.triggered]
    if triggered_reports:
        _write_json(
            failure_path,
            {
                "benchmark_id": record["benchmark_id"],
                "case_id": case_definition.case_id,
                "seed": int(record["seed"]),
                "failure_reports": triggered_reports,
            },
        )

    artifact_paths = {
        "environment_fingerprint": repo_relative_path(environment_path, repo_root),
        "solver_config": repo_relative_path(solver_path, repo_root),
        "seed_record": repo_relative_path(seed_path, repo_root),
        "benchmark_case_snapshot": repo_relative_path(case_snapshot_path, repo_root),
        "observables_summary": repo_relative_path(observables_path, repo_root),
        "residual_diagnostics": repo_relative_path(residuals_path, repo_root),
        "gate_report": repo_relative_path(gate_path, repo_root),
        "acceptance_decision": repo_relative_path(decision_path, repo_root),
        "regression_check": repo_relative_path(regression_path, repo_root),
    }
    if triggered_reports:
        artifact_paths["failure_record"] = repo_relative_path(failure_path, repo_root)
    artifact_paths["run_manifest"] = repo_relative_path(manifest_path, repo_root)

    manifest = RunManifest(
        run_id=f"{family_definition.family_id}:{case_definition.case_id}:seed{int(record['seed'])}",
        persistence_model="evidence_bundle",
        benchmark_id=family_definition.family_id,
        case_id=case_definition.case_id,
        parameter_id=str(record["parameter_id"]),
        seed=int(record["seed"]),
        branch=str(record["branch"]),
        theorem_tier=str(record["theorem_tier"]),
        acceptance_profile=decision.acceptance_profile,
        claim_status=case_definition.claim_status,
        implementation_status=case_definition.implementation_status,
        evidence_class=case_definition.evidence_class,
        decision_status=decision.decision_status,
        artifact_paths=artifact_paths,
        compatibility_mode=str(record.get("metadata", {}).get("compatibility_mode", "disabled")),
        compatibility_artifacts=dict(record.get("metadata", {}).get("compatibility_artifacts", {})),
        claim_refs=list(family_definition.claim_refs),
        failure_labels=list(decision.failure_labels),
    )
    _write_json(manifest_path, manifest.to_dict())
    return artifact_paths


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_evidence_record_from_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Load one canonical run record from its run manifest."""

    manifest_file = Path(manifest_path).resolve()
    repo_root = artifact_root(manifest_file.parents[5])
    manifest = _load_json(manifest_file)
    artifact_paths = manifest["artifact_paths"]
    seed_record = _load_json(repo_root / artifact_paths["seed_record"])
    solver_config = _load_json(repo_root / artifact_paths["solver_config"])
    observables = _load_json(repo_root / artifact_paths["observables_summary"])
    residuals = _load_json(repo_root / artifact_paths["residual_diagnostics"])
    decision = _load_json(repo_root / artifact_paths["acceptance_decision"])
    case_snapshot = _load_json(repo_root / artifact_paths["benchmark_case_snapshot"])
    return {
        "benchmark_id": manifest["benchmark_id"],
        "case_id": manifest["case_id"],
        "branch": manifest["branch"],
        "theorem_tier": manifest["theorem_tier"],
        "parameter_id": manifest["parameter_id"],
        "seed": int(manifest["seed"]),
        "parameters": seed_record["resolved_parameters"],
        "metadata": {
            "solver": solver_config.get("solver"),
            "runtime_seconds": solver_config.get("runtime_seconds"),
            "code_hash": solver_config.get("code_hash"),
            "source_of_truth": solver_config.get("source_of_truth", {}),
            "artifact_paths": artifact_paths,
            "compatibility_mode": manifest.get("compatibility_mode", "disabled"),
            "compatibility_artifacts": dict(manifest.get("compatibility_artifacts", {})),
        },
        "observables": observables["observables"],
        "law_fits": residuals.get("law_fits", {}),
        "law_selection_summary": residuals.get("law_selection_summary", {}),
        "failure_labels": list(manifest.get("failure_labels", [])),
        "notes": list(residuals.get("notes", [])),
        "acceptance_decision": decision,
        "claim_refs": list(manifest.get("claim_refs", [])),
        "case_snapshot": case_snapshot,
    }


def load_evidence_records(root: str | Path) -> list[dict[str, Any]]:
    """Load canonical run records by reconstructing them from evidence bundles."""

    records: list[dict[str, Any]] = []
    for manifest in sorted(evidence_root(root).rglob("run_manifest.json")):
        records.append(load_evidence_record_from_manifest(manifest))
    return records


def build_run_index(root: str | Path) -> Path:
    """Generate an index of all canonical evidence bundles."""

    repo_root = artifact_root(root)
    records = load_evidence_records(repo_root)
    output_path = indexes_root(repo_root) / "run_index.json"
    _write_json(
        output_path,
        {
            "run_count": len(records),
            "runs": [
                {
                    "benchmark_id": record["benchmark_id"],
                    "case_id": record["case_id"],
                    "seed": record["seed"],
                    "acceptance_profile": record["acceptance_decision"]["acceptance_profile"],
                    "claim_status": record["case_snapshot"]["case"]["claim_status"],
                    "implementation_status": record["case_snapshot"]["case"]["implementation_status"],
                    "evidence_class": record["case_snapshot"]["case"]["evidence_class"],
                    "decision_status": record["acceptance_decision"]["decision_status"],
                    "artifact_paths": record["metadata"]["artifact_paths"],
                    "compatibility_mode": record["metadata"].get("compatibility_mode", "disabled"),
                    "compatibility_artifacts": record["metadata"].get("compatibility_artifacts", {}),
                }
                for record in records
            ],
        },
    )
    return output_path


def build_failure_index(root: str | Path) -> Path:
    """Generate a queryable index of failures, negative controls, and qualified cases."""

    repo_root = artifact_root(root)
    family_lookup = {definition.family_id: definition for definition in benchmark_definitions()}
    entries: list[dict[str, Any]] = []
    for record in load_evidence_records(repo_root):
        family = family_lookup[record["benchmark_id"]]
        case_payload = record["case_snapshot"]["case"]
        include_entry = (
            bool(record["failure_labels"])
            or record["acceptance_decision"]["decision_status"] != "accepted"
            or case_payload["role"] != "reference"
            or case_payload["implementation_status"] != "complete"
        )
        if not include_entry:
            continue
        entries.append(
            {
                "benchmark_id": record["benchmark_id"],
                "case_id": record["case_id"],
                "role": case_payload["role"],
                "decision_status": record["acceptance_decision"]["decision_status"],
                "implementation_status": case_payload["implementation_status"],
                "claim_status": case_payload["claim_status"],
                "failure_labels": list(record["failure_labels"]),
                "claim_refs": list(family.claim_refs),
                "failure_record_path": record["metadata"]["artifact_paths"].get("failure_record"),
                "run_manifest_path": record["metadata"]["artifact_paths"]["run_manifest"],
            }
        )
    output_path = indexes_root(repo_root) / "failure_index.json"
    _write_json(
        output_path,
        {
            "entry_count": len(entries),
            "entries": entries,
        },
    )
    return output_path


def build_claim_traceability(root: str | Path) -> Path:
    """Generate machine-readable claim-to-evidence traceability."""

    repo_root = artifact_root(root)
    records = load_evidence_records(repo_root)
    by_case = {(record["benchmark_id"], record["case_id"]): record for record in records}
    families = benchmark_definitions()
    claims = claim_definitions()
    traceability_entries: list[dict[str, Any]] = []
    for claim in claims:
        related_cases: list[dict[str, Any]] = []
        for family in families:
            if claim.claim_id not in family.claim_refs:
                continue
            for case in family.cases:
                record = by_case.get((family.family_id, case.case_id))
                artifact_paths = record["metadata"]["artifact_paths"] if record is not None else {}
                related_cases.append(
                    {
                        "benchmark_id": family.family_id,
                        "case_id": case.case_id,
                        "role": case.role,
                        "claim_status": case.claim_status,
                        "acceptance_profile": case.acceptance_profile,
                        "observables": case.observables,
                        "expected_failure_modes": case.expected_failure_modes,
                        "decision_status": record["acceptance_decision"]["decision_status"] if record is not None else "not_run",
                        "artifact_paths": artifact_paths,
                    }
                )
        traceability_entries.append(
            {
                "claim": claim.to_dict(),
                "cases": related_cases,
            }
        )
    output_path = indexes_root(repo_root) / "claim_traceability.json"
    _write_json(
        output_path,
        {
            "claim_count": len(traceability_entries),
            "claims": traceability_entries,
        },
    )
    return output_path


def refresh_indexes(root: str | Path) -> dict[str, str]:
    """Refresh the canonical derived indexes after a run."""

    repo_root = artifact_root(root)
    run_index = build_run_index(repo_root)
    failure_index = build_failure_index(repo_root)
    claim_traceability = build_claim_traceability(repo_root)
    return {
        "run_index": repo_relative_path(run_index, repo_root),
        "failure_index": repo_relative_path(failure_index, repo_root),
        "claim_traceability": repo_relative_path(claim_traceability, repo_root),
    }


def find_evidence_record(
    root: str | Path,
    benchmark_id: str,
    case_id: str,
    *,
    seed: int = 0,
) -> dict[str, Any]:
    """Return one canonical record by benchmark, case, and seed."""

    manifest = run_manifest_path(root, benchmark_id, case_id, seed)
    if not manifest.exists():
        raise FileNotFoundError(f"missing canonical run manifest: {repo_relative_path(manifest, root)}")
    return load_evidence_record_from_manifest(manifest)
