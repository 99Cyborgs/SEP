"""Shared validation I/O for evidence records and gate artifacts.

This module normalizes repository-relative paths and gate report serialization.
It does not evaluate any gate logic itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from subsystem_emergence.evidence import load_evidence_records

from .types import GateResult
from subsystem_emergence.io.paths import repo_relative_path, validation_gates_root


def load_records(path: str | Path) -> list[dict]:
    """Load canonical evidence records from either a repo root or an evidence root."""

    # Callers pass both repository roots and `<repo>/results/evidence`; normalize
    # both forms to the repository root expected by `load_evidence_records`.
    return load_evidence_records(Path(path).resolve().parents[1] if Path(path).name == "evidence" else path)


def load_gate_criteria(path: str | Path) -> dict:
    """Load machine-readable gate criteria."""

    return json.loads(Path(path).read_text())


def filter_records(
    records: Iterable[dict],
    *,
    benchmark_ids: set[str] | None = None,
    branch: str | None = None,
) -> list[dict]:
    """Filter canonical evidence records by benchmark id and branch."""

    filtered: list[dict] = []
    for record in records:
        if benchmark_ids is not None and record.get("benchmark_id") not in benchmark_ids:
            continue
        if branch is not None and record.get("branch") != branch:
            continue
        filtered.append(record)
    return filtered


def write_gate_artifacts(root: Path, result: GateResult) -> tuple[Path, Path]:
    """Write JSON and Markdown artifacts for a gate result.

    The function mutates ``result`` with repository-relative artifact paths so
    downstream ledgers can serialize the same object without re-resolving paths.
    """

    output_dir = validation_gates_root(root) / result.gate
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "gate_report.json"
    md_path = output_dir / "gate_report.md"
    result.report_json = repo_relative_path(json_path, root)
    result.report_markdown = repo_relative_path(md_path, root)
    json_path.write_text(json.dumps(result.to_dict(), indent=2))
    md_path.write_text(
        "\n".join(
            [
                f"# {result.gate} Report",
                "",
                f"- Passed: `{result.passed}`",
                f"- Summary: {result.summary}",
                f"- Failure labels: {', '.join(result.failure_labels) if result.failure_labels else 'none'}",
                "",
                "## Criteria",
                "```json",
                json.dumps(result.criteria, indent=2),
                "```",
                "",
                "## Metrics",
                "```json",
                json.dumps(result.metrics, indent=2),
                "```",
            ]
        )
    )
    return json_path, md_path


def load_ledgers(path: str | Path) -> list[dict]:
    """Deprecated alias for :func:`load_records`."""

    return load_records(path)


def filter_ledgers(
    records: Iterable[dict],
    *,
    benchmark_ids: set[str] | None = None,
    branch: str | None = None,
) -> list[dict]:
    """Deprecated alias for :func:`filter_records`."""

    return filter_records(records, benchmark_ids=benchmark_ids, branch=branch)
