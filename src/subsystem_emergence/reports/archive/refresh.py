"""Formal scratch-rooted archive refresh driver."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

from subsystem_emergence.evidence import run_manifest_path
from subsystem_emergence.io.paths import artifact_root, create_scratch_root, repo_relative_path, repository_root

from .cross_domain import generate_cross_domain_application_package
from .paper_e import generate_paper_e_package
from .runtime import refresh_driver_context
from .validation import ARCHIVE_TARGET_REQUIREMENTS, GENERAL_REQUIRED_INDEX_PATHS, archive_targets, validate_archive_evidence


def _copy_file(source_root: Path, scratch_root: Path, relative_path: str, copied: list[str]) -> None:
    source_path = source_root / relative_path
    if not source_path.exists():
        return
    destination_path = scratch_root / relative_path
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)
    copied.append(relative_path)


def _copy_bundle_directory(source_root: Path, scratch_root: Path, benchmark_id: str, case_id: str, seed: int, copied: list[str]) -> None:
    manifest_path = run_manifest_path(source_root, benchmark_id, case_id, seed)
    if not manifest_path.exists():
        return
    bundle_root = manifest_path.parent
    relative_bundle = repo_relative_path(bundle_root, source_root)
    destination_root = scratch_root / relative_bundle
    destination_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundle_root, destination_root, dirs_exist_ok=True)
    copied.append(relative_bundle)


def _copy_manifest_references_from_indexes(source_root: Path, scratch_root: Path, copied: list[str]) -> None:
    manifest_paths: set[str] = set()
    for relative_path in GENERAL_REQUIRED_INDEX_PATHS:
        source_path = source_root / relative_path
        if not source_path.exists():
            continue
        payload = json.loads(source_path.read_text())
        if relative_path.endswith("run_index.json"):
            manifest_paths.update(
                (entry.get("artifact_paths") or {}).get("run_manifest")
                for entry in payload.get("runs", [])
                if (entry.get("artifact_paths") or {}).get("run_manifest")
            )
        elif relative_path.endswith("failure_index.json"):
            manifest_paths.update(
                entry.get("run_manifest_path")
                for entry in payload.get("entries", [])
                if entry.get("run_manifest_path")
            )
        elif relative_path.endswith("claim_traceability.json"):
            for claim in payload.get("claims", []):
                for case in claim.get("cases", []):
                    manifest_rel = (case.get("artifact_paths") or {}).get("run_manifest")
                    if manifest_rel:
                        manifest_paths.add(manifest_rel)
    for manifest_rel in sorted(manifest_paths):
        manifest_path = source_root / manifest_rel
        if not manifest_path.exists():
            continue
        relative_bundle = repo_relative_path(manifest_path.parent, source_root)
        destination_root = scratch_root / relative_bundle
        destination_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(manifest_path.parent, destination_root, dirs_exist_ok=True)
        copied.append(relative_bundle)


def materialize_archive_inputs(
    source_root: str | Path,
    scratch_root: str | Path,
    *,
    config_root: str | Path | None = None,
    targets: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Copy the canonical evidence and support files needed for archive refresh into scratch."""

    source = artifact_root(source_root)
    scratch = Path(scratch_root).resolve()
    config = artifact_root(config_root) if config_root is not None else repository_root()
    selected_targets = archive_targets(targets)
    copied: list[str] = []

    for relative_path in GENERAL_REQUIRED_INDEX_PATHS:
        _copy_file(source, scratch, relative_path, copied)
    _copy_manifest_references_from_indexes(source, scratch, copied)
    for target in selected_targets:
        requirements = ARCHIVE_TARGET_REQUIREMENTS[target]
        for relative_path in requirements["required_relative_paths"]:
            _copy_file(config, scratch, relative_path, copied)
        for relative_path in requirements["required_summary_paths"]:
            _copy_file(source, scratch, relative_path, copied)
        for benchmark_id, case_id, seed in requirements["required_cases"]:
            _copy_bundle_directory(source, scratch, benchmark_id, case_id, seed, copied)

    return {
        "source_root": str(source),
        "config_root": str(config),
        "scratch_root": str(scratch),
        "targets": list(selected_targets),
        "copied_count": len(dict.fromkeys(copied)),
        "copied_paths": sorted(dict.fromkeys(copied)),
    }


def _archive_output_paths(manifest: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("manifest_json", "summary_json", "summary_markdown"):
        value = manifest.get(key)
        if isinstance(value, str) and value.startswith("reports/archive/"):
            paths.append(value)
    for value in (manifest.get("outputs") or {}).values():
        if isinstance(value, str) and value.startswith("reports/archive/"):
            paths.append(value)
    return sorted(dict.fromkeys(paths))


def _write_refresh_summary(scratch_root: Path, payload: dict[str, Any]) -> tuple[str, str]:
    relative_dir = Path("reports/generated/archive_refresh")
    json_rel = (relative_dir / "refresh_summary.json").as_posix()
    md_rel = (relative_dir / "refresh_summary.md").as_posix()
    json_path = scratch_root / json_rel
    md_path = scratch_root / md_rel
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2))
    md_path.write_text(
        "\n".join(
            [
                "# Archive Refresh Summary",
                "",
                f"- Source root: `{payload['source_root']}`",
                f"- Config root: `{payload['config_root']}`",
                f"- Scratch root: `{payload['scratch_root']}`",
                f"- Targets: `{', '.join(payload['targets'])}`",
                f"- Copied canonical inputs: `{payload['materialized_inputs']['copied_count']}`",
                f"- Validated canonical artifacts: `{payload['validation']['validated_artifact_count']}`",
                f"- Promote requested: `{payload['promote']}`",
                f"- Force overwrite: `{payload['force']}`",
                "",
                "## Generated Targets",
            ]
            + [
                f"- `{target}`: `{', '.join(details['archive_outputs']) if details['archive_outputs'] else 'no tracked archive outputs'}`"
                for target, details in payload["generated_targets"].items()
            ]
            + [
                "",
                "## Promoted Paths",
            ]
            + [f"- `{path}`" for path in payload["promoted_paths"]]
        )
    )
    return json_rel, md_rel


def _promote_archive_outputs(source_root: Path, scratch_root: Path, relative_paths: list[str], *, force: bool) -> list[str]:
    collisions = [path for path in relative_paths if (source_root / path).exists()]
    if collisions and not force:
        collision_list = ", ".join(collisions)
        raise RuntimeError(
            "Refusing to overwrite tracked archive outputs without `force=True`. "
            f"Colliding paths: {collision_list}"
        )
    for relative_path in relative_paths:
        source_path = scratch_root / relative_path
        destination_path = source_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if destination_path.exists():
            destination_path.unlink()
        shutil.copy2(source_path, destination_path)
    return relative_paths


def refresh_archive_outputs(
    *,
    source_root: str | Path | None = None,
    config_root: str | Path | None = None,
    scratch_root: str | Path | None = None,
    targets: Iterable[str] | None = None,
    promote: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Refresh tracked archive outputs from a validated scratch evidence root."""

    source = artifact_root(source_root) if source_root is not None else repository_root()
    config = artifact_root(config_root) if config_root is not None else repository_root()
    scratch = Path(scratch_root).resolve() if scratch_root is not None else create_scratch_root("archive_refresh")
    if scratch == source:
        raise RuntimeError("scratch_root must not be the tracked repository root; use an ignored scratch directory instead")

    selected_targets = archive_targets(targets)
    execution_context = refresh_driver_context(scratch)
    materialized_inputs = materialize_archive_inputs(source, scratch, config_root=config, targets=selected_targets)
    validation = validate_archive_evidence(scratch, targets=selected_targets)

    policy_path = scratch / "validation" / "acceptance_profiles.yaml"
    registry_path = scratch / "benchmarks" / "registry.yaml"
    generated_targets: dict[str, dict[str, Any]] = {}
    tracked_paths: list[str] = []
    for target in selected_targets:
        if target == "cross_domain":
            manifest = generate_cross_domain_application_package(
                root=scratch,
                policy_path=policy_path,
                registry_path=registry_path,
                context=execution_context,
            )
        elif target == "paper_e":
            manifest = generate_paper_e_package(root=scratch, context=execution_context)
        else:
            raise KeyError(f"unsupported archive target: {target}")
        archive_outputs = _archive_output_paths(manifest)
        tracked_paths.extend(archive_outputs)
        generated_targets[target] = {
            "manifest": manifest,
            "archive_outputs": archive_outputs,
        }

    tracked_paths = sorted(dict.fromkeys(tracked_paths))
    summary_paths = [
        "reports/generated/archive_refresh/refresh_summary.json",
        "reports/generated/archive_refresh/refresh_summary.md",
    ]
    summary: dict[str, Any] = {
        "source_root": str(source),
        "config_root": str(config),
        "scratch_root": str(scratch),
        "targets": list(selected_targets),
        "materialized_inputs": materialized_inputs,
        "validation": validation,
        "generated_targets": generated_targets,
        "promote": promote,
        "force": force,
        "promoted_paths": list(tracked_paths + summary_paths) if promote else [],
    }
    summary_json, summary_markdown = _write_refresh_summary(scratch, summary)
    if promote:
        _promote_archive_outputs(source, scratch, tracked_paths + [summary_json, summary_markdown], force=force)
    summary["summary_json"] = summary_json
    summary["summary_markdown"] = summary_markdown
    return summary


def main() -> None:
    """CLI for validated archive refreshes."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", default=None)
    parser.add_argument("--config-root", default=None)
    parser.add_argument("--scratch-root", default=None)
    parser.add_argument(
        "--target",
        action="append",
        choices=sorted(ARCHIVE_TARGET_REQUIREMENTS),
        dest="targets",
        help="Archive target(s) to refresh. Defaults to all targets.",
    )
    parser.add_argument("--promote", action="store_true", help="Promote validated archive outputs back into the tracked repository")
    parser.add_argument("--force", action="store_true", help="Allow overwriting existing tracked archive outputs during promotion")
    args = parser.parse_args()
    print(
        json.dumps(
            refresh_archive_outputs(
                source_root=args.source_root,
                config_root=args.config_root,
                scratch_root=args.scratch_root,
                targets=args.targets,
                promote=args.promote,
                force=args.force,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
