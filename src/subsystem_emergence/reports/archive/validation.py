"""Archive evidence completeness validation for downstream-only refreshes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from subsystem_emergence.evidence import run_manifest_path
from subsystem_emergence.io.paths import artifact_root, repo_relative_path


GENERAL_REQUIRED_INDEX_PATHS = (
    "results/indexes/run_index.json",
    "results/indexes/failure_index.json",
    "results/indexes/claim_traceability.json",
)

ARCHIVE_TARGET_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "cross_domain": {
        "required_cases": (
            ("BP_Clickstream_Docs_Funnel", "reference", 0),
            ("BP_Clickstream_Docs_Funnel", "negative_detour", 0),
            ("BP_Support_Portal_Funnel", "reference", 0),
            ("BP_Support_Portal_Funnel", "negative_detour", 0),
            ("BP_Workflow_Queue_Funnel", "reference", 0),
            ("BP_Workflow_Queue_Funnel", "negative_detour", 0),
        ),
        "required_relative_paths": (
            "benchmarks/registry.yaml",
            "validation/acceptance_profiles.yaml",
        ),
        "required_summary_paths": (),
    },
    "paper_e": {
        "required_cases": (
            ("BP_Mobility_Chicago_Corridors", "reference", 0),
            ("BP_Mobility_Chicago_Corridors", "negative_weekend", 0),
            ("BP_Mobility_Downtown_Routing_Instability", "reference", 0),
            ("BP_Mobility_NYC_East_Corridor", "reference", 0),
        ),
        "required_relative_paths": (),
        "required_summary_paths": (
            "results/indexes/application_validation/BP_Mobility_Chicago_Corridors_validation_matrix.json",
        ),
    },
}


class ArchiveEvidenceError(RuntimeError):
    """Raised when canonical evidence is incomplete for archive generation."""


def archive_targets(targets: Iterable[str] | None = None) -> tuple[str, ...]:
    """Normalize archive target selection."""

    if targets is None:
        return tuple(ARCHIVE_TARGET_REQUIREMENTS)
    normalized = tuple(dict.fromkeys(str(target) for target in targets))
    unknown = sorted(set(normalized).difference(ARCHIVE_TARGET_REQUIREMENTS))
    if unknown:
        raise KeyError(f"unknown archive target(s): {unknown}")
    return normalized


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _require_file(path: Path, *, root: Path, missing: list[str], validated: list[str]) -> bool:
    if not path.exists():
        missing.append(repo_relative_path(path, root))
        return False
    validated.append(repo_relative_path(path, root))
    return True


def _check_run_index(root: Path, missing: list[str], inconsistent: list[str], validated: list[str]) -> dict[str, Any] | None:
    path = root / GENERAL_REQUIRED_INDEX_PATHS[0]
    if not _require_file(path, root=root, missing=missing, validated=validated):
        return None
    payload = _load_json(path)
    runs = payload.get("runs", [])
    if payload.get("run_count") != len(runs):
        inconsistent.append(
            f"{repo_relative_path(path, root)} reports run_count={payload.get('run_count')} but contains {len(runs)} runs"
        )
    for entry in runs:
        manifest_rel = (entry.get("artifact_paths") or {}).get("run_manifest")
        if manifest_rel and not (root / manifest_rel).exists():
            inconsistent.append(f"{repo_relative_path(path, root)} references missing run manifest {manifest_rel}")
    return payload


def _check_failure_index(root: Path, missing: list[str], inconsistent: list[str], validated: list[str]) -> dict[str, Any] | None:
    path = root / GENERAL_REQUIRED_INDEX_PATHS[1]
    if not _require_file(path, root=root, missing=missing, validated=validated):
        return None
    payload = _load_json(path)
    entries = payload.get("entries", [])
    if payload.get("entry_count") != len(entries):
        inconsistent.append(
            f"{repo_relative_path(path, root)} reports entry_count={payload.get('entry_count')} but contains {len(entries)} entries"
        )
    for entry in entries:
        manifest_rel = entry.get("run_manifest_path")
        if manifest_rel and not (root / manifest_rel).exists():
            inconsistent.append(f"{repo_relative_path(path, root)} references missing run manifest {manifest_rel}")
    return payload


def _check_claim_traceability(root: Path, missing: list[str], inconsistent: list[str], validated: list[str]) -> dict[str, Any] | None:
    path = root / GENERAL_REQUIRED_INDEX_PATHS[2]
    if not _require_file(path, root=root, missing=missing, validated=validated):
        return None
    payload = _load_json(path)
    claims = payload.get("claims", [])
    if payload.get("claim_count") != len(claims):
        inconsistent.append(
            f"{repo_relative_path(path, root)} reports claim_count={payload.get('claim_count')} but contains {len(claims)} claims"
        )
    for claim in claims:
        for case in claim.get("cases", []):
            manifest_rel = (case.get("artifact_paths") or {}).get("run_manifest")
            if case.get("decision_status") != "not_run" and manifest_rel and not (root / manifest_rel).exists():
                inconsistent.append(f"{repo_relative_path(path, root)} references missing run manifest {manifest_rel}")
    return payload


def _case_traceability_present(traceability: dict[str, Any] | None, benchmark_id: str, case_id: str, manifest_rel: str) -> bool:
    if traceability is None:
        return True
    for claim in traceability.get("claims", []):
        for case in claim.get("cases", []):
            if case.get("benchmark_id") != benchmark_id or case.get("case_id") != case_id:
                continue
            if case.get("decision_status") == "not_run":
                continue
            if (case.get("artifact_paths") or {}).get("run_manifest") == manifest_rel:
                return True
    return False


def _validate_required_case(
    root: Path,
    benchmark_id: str,
    case_id: str,
    seed: int,
    *,
    run_index: dict[str, Any] | None,
    traceability: dict[str, Any] | None,
    missing: list[str],
    inconsistent: list[str],
    validated: list[str],
) -> None:
    manifest_path = run_manifest_path(root, benchmark_id, case_id, seed)
    if not _require_file(manifest_path, root=root, missing=missing, validated=validated):
        return
    manifest = _load_json(manifest_path)
    artifact_paths = manifest.get("artifact_paths") or {}
    required_artifacts = ("run_manifest", "observables_summary", "acceptance_decision")
    manifest_rel = repo_relative_path(manifest_path, root)
    if artifact_paths.get("run_manifest") != manifest_rel:
        inconsistent.append(
            f"{manifest_rel} declares run_manifest={artifact_paths.get('run_manifest')!r} instead of {manifest_rel!r}"
        )
    for artifact_name in required_artifacts:
        artifact_rel = artifact_paths.get(artifact_name)
        if not artifact_rel:
            inconsistent.append(f"{manifest_rel} omits required artifact path {artifact_name!r}")
            continue
        artifact_path = root / artifact_rel
        if not _require_file(artifact_path, root=root, missing=missing, validated=validated):
            continue
    if run_index is not None:
        indexed = next(
            (
                entry
                for entry in run_index.get("runs", [])
                if entry.get("benchmark_id") == benchmark_id
                and entry.get("case_id") == case_id
                and int(entry.get("seed", -1)) == seed
            ),
            None,
        )
        if indexed is None:
            inconsistent.append(f"results/indexes/run_index.json is missing {benchmark_id}:{case_id}:seed{seed}")
        elif ((indexed.get("artifact_paths") or {}).get("run_manifest")) != manifest_rel:
            inconsistent.append(
                f"results/indexes/run_index.json points {benchmark_id}:{case_id}:seed{seed} at "
                f"{(indexed.get('artifact_paths') or {}).get('run_manifest')!r} instead of {manifest_rel!r}"
            )
    if not _case_traceability_present(traceability, benchmark_id, case_id, manifest_rel):
        inconsistent.append(
            "results/indexes/claim_traceability.json does not expose "
            f"{benchmark_id}:{case_id}:seed{seed} as a canonical evidence-backed case"
        )


def _validate_paper_e_summary(
    root: Path,
    summary_path: Path,
    *,
    missing: list[str],
    inconsistent: list[str],
    validated: list[str],
) -> None:
    if not _require_file(summary_path, root=root, missing=missing, validated=validated):
        return
    payload = _load_json(summary_path)
    case_ids = {case.get("case_id") for case in payload.get("cases", [])}
    for case_id in ("reference", "negative_weekend"):
        if case_id not in case_ids:
            inconsistent.append(
                f"{repo_relative_path(summary_path, root)} is missing required mobility application case {case_id!r}"
            )


def validate_archive_evidence(root: str | Path, *, targets: Iterable[str] | None = None) -> dict[str, Any]:
    """Validate that canonical evidence is complete enough for archive generation."""

    repo_root = artifact_root(root)
    selected_targets = archive_targets(targets)
    missing: list[str] = []
    inconsistent: list[str] = []
    validated: list[str] = []

    run_index = _check_run_index(repo_root, missing, inconsistent, validated)
    _check_failure_index(repo_root, missing, inconsistent, validated)
    traceability = _check_claim_traceability(repo_root, missing, inconsistent, validated)

    for target in selected_targets:
        requirements = ARCHIVE_TARGET_REQUIREMENTS[target]
        for relative_path in requirements["required_relative_paths"]:
            _require_file(repo_root / relative_path, root=repo_root, missing=missing, validated=validated)
        for relative_path in requirements["required_summary_paths"]:
            summary_path = repo_root / relative_path
            if target == "paper_e":
                _validate_paper_e_summary(repo_root, summary_path, missing=missing, inconsistent=inconsistent, validated=validated)
            else:
                _require_file(summary_path, root=repo_root, missing=missing, validated=validated)
        for benchmark_id, case_id, seed in requirements["required_cases"]:
            _validate_required_case(
                repo_root,
                benchmark_id,
                case_id,
                seed,
                run_index=run_index,
                traceability=traceability,
                missing=missing,
                inconsistent=inconsistent,
                validated=validated,
            )

    if missing or inconsistent:
        lines = [
            "Canonical archive evidence is incomplete.",
            f"Validated root: {repo_root}",
            f"Archive targets: {', '.join(selected_targets)}",
        ]
        if missing:
            lines.append("Missing canonical artifacts:")
            lines.extend(f"- {item}" for item in sorted(dict.fromkeys(missing)))
        if inconsistent:
            lines.append("Inconsistent canonical artifacts:")
            lines.extend(f"- {item}" for item in sorted(dict.fromkeys(inconsistent)))
        raise ArchiveEvidenceError("\n".join(lines))

    return {
        "root": str(repo_root),
        "targets": list(selected_targets),
        "validated_artifact_count": len(dict.fromkeys(validated)),
        "validated_artifacts": sorted(dict.fromkeys(validated)),
    }
