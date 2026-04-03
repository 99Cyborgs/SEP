"""Shared gate helpers."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from subsystem_emergence.core.types import GateResult
from subsystem_emergence.core.validation import filter_records, load_gate_criteria, load_records, write_gate_artifacts
from subsystem_emergence.io.paths import artifact_root, evidence_root, repository_root


def gate_context(gate: str, root: Path | None = None) -> tuple[Path, dict, list[dict]]:
    """Load repo root, gate criteria, and filtered records."""

    source_root = repository_root(Path(__file__).resolve())
    repo_root = artifact_root(root) if root is not None else source_root
    criteria = load_gate_criteria(source_root / "validation" / "criteria" / f"{gate}.json")
    records = filter_records(
        load_records(evidence_root(repo_root)),
        benchmark_ids=set(criteria["benchmark_ids"]),
    )
    return repo_root, criteria, records


def finalize_gate(
    root: Path,
    gate: str,
    criteria: dict,
    records: list[dict],
    passed: bool,
    metrics: dict,
    summary: str,
) -> dict:
    """Write gate artifacts and return a serialized result."""

    failure_labels = sorted(
        {
            label
            for record in records
            for label in record.get("failure_labels", [])
        }
    )
    result = GateResult(
        gate=gate,
        passed=passed,
        criteria=criteria,
        summary=summary,
        metrics=metrics,
        failure_labels=failure_labels,
    )
    write_gate_artifacts(root, result)
    return result.to_dict()


def main_dump(result: dict) -> None:
    """Print a JSON gate report."""

    print(json.dumps(result, indent=2))
