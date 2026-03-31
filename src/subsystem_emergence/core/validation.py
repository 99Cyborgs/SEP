"""Shared validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .types import GateResult
from subsystem_emergence.io.ledgers import repo_relative_path


def load_ledgers(path: str | Path) -> list[dict]:
    """Load all per-run JSON ledgers below a directory tree."""

    root = Path(path)
    records: list[dict] = []
    for item in sorted(root.rglob("*.json")):
        if item.name == "ledger.jsonl":
            continue
        records.append(json.loads(item.read_text()))
    return records


def load_gate_criteria(path: str | Path) -> dict:
    """Load machine-readable gate criteria."""

    return json.loads(Path(path).read_text())


def filter_ledgers(
    records: Iterable[dict],
    *,
    benchmark_ids: set[str] | None = None,
    branch: str | None = None,
) -> list[dict]:
    """Filter ledgers by benchmark id and branch."""

    filtered: list[dict] = []
    for record in records:
        if benchmark_ids is not None and record.get("benchmark_id") not in benchmark_ids:
            continue
        if branch is not None and record.get("branch") != branch:
            continue
        filtered.append(record)
    return filtered


def write_gate_artifacts(root: Path, result: GateResult) -> tuple[Path, Path]:
    """Write JSON and Markdown artifacts for a gate result."""

    output_dir = root / "results" / "gate_reports" / result.gate
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{result.gate.lower()}_report.json"
    md_path = output_dir / f"{result.gate.lower()}_report.md"
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
