"""Legacy ledger compatibility writers.

The canonical SEP persistence model is the evidence bundle under ``results/evidence``.
This module remains only to preserve opt-in compatibility snapshots under
``results/ledgers`` for historical archive consumers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from .paths import (
    artifact_root,
    current_code_hash,
    legacy_ledgers_root,
    repo_relative_path,
    repository_root,
)

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

def ledger_paths(root: Path, benchmark_id: str, parameter_id: str, seed: int) -> tuple[Path, Path]:
    """Return compatibility-only per-run JSON and Markdown ledger paths."""

    ledger_dir = legacy_ledgers_root(root) / benchmark_id
    stem = f"{parameter_id}_seed{seed}"
    return ledger_dir / f"{stem}.json", ledger_dir / f"{stem}.md"


def write_legacy_ledger(root: str | Path, record: dict) -> tuple[Path, Path]:
    """Write opt-in compatibility-only per-run ledgers plus an aggregate JSONL snapshot."""

    repo_root = artifact_root(root)
    json_path, md_path = ledger_paths(
        repo_root,
        str(record["benchmark_id"]),
        str(record["parameter_id"]),
        int(record["seed"]),
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _json_ready(record)
    json_path.write_text(json.dumps(normalized, indent=2))
    md_path.write_text(
        "\n".join(
            [
                f"# {record['benchmark_id']} Compatibility Ledger",
                "",
                "This file is a legacy compatibility snapshot.",
                "Canonical persistence lives under `results/evidence/` and `results/indexes/`.",
                "",
                f"- Parameter set: `{record['parameter_id']}`",
                f"- Seed: `{record['seed']}`",
                f"- Branch: `{record['branch']}`",
                f"- Tier: `{record['theorem_tier']}`",
                f"- Decision status: `{record.get('acceptance_decision', {}).get('decision_status', 'unknown')}`",
                "",
                "## Primary Observables",
                f"- spectral_gap: `{normalized['observables'].get('spectral_gap')}`",
                f"- singular_gap: `{normalized['observables'].get('singular_gap')}`",
                f"- projector_deformation: `{normalized['observables'].get('projector_deformation')}`",
                f"- coherent_projector_deformation: `{normalized['observables'].get('coherent_projector_deformation')}`",
                f"- block_residual_norm: `{normalized['observables'].get('block_residual_norm')}`",
                f"- autonomy_horizon: `{normalized['observables'].get('autonomy_horizon')}`",
                "",
                "## Law Selection",
                f"`{json.dumps(normalized.get('law_selection_summary', {}), indent=2)}`",
            ]
        )
    )
    jsonl_path = legacy_ledgers_root(repo_root) / "ledger.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(normalized) + "\n")
    return json_path, md_path


def load_legacy_ledgers(root: str | Path) -> list[dict]:
    """Load all compatibility ledgers from a repository root."""

    repo_root = artifact_root(root)
    ledgers: list[dict] = []
    for path in sorted(legacy_ledgers_root(repo_root).rglob("*.json")):
        if path.name.endswith("_report.json"):
            continue
        ledgers.append(json.loads(path.read_text()))
    return ledgers


def write_ledger(root: str | Path, record: dict) -> tuple[Path, Path]:
    """Deprecated alias for :func:`write_legacy_ledger`."""

    return write_legacy_ledger(root, record)


def load_ledgers(root: str | Path) -> list[dict]:
    """Deprecated alias for :func:`load_legacy_ledgers`."""

    return load_legacy_ledgers(root)
