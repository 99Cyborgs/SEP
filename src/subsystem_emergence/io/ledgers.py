"""Result ledger writers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np


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


def repo_relative_path(path: str | Path, root: str | Path | None = None) -> str:
    """Return a portable repository-relative POSIX path."""

    repo_root = repository_root(Path(root) if root is not None else None)
    return Path(path).resolve().relative_to(repo_root).as_posix()


def repository_root(start: Path | None = None) -> Path:
    """Locate the repository root by walking upward to pyproject.toml."""

    candidate = Path(start or __file__).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for path in [candidate] + list(candidate.parents):
        if (path / "pyproject.toml").exists():
            return path
    raise FileNotFoundError("could not locate repository root")


def current_code_hash(root: Path | None = None) -> str | None:
    """Return the git hash when available."""

    repo_root = repository_root(root)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            check=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def ledger_paths(root: Path, benchmark_id: str, parameter_id: str, seed: int) -> tuple[Path, Path]:
    """Return per-run JSON and Markdown ledger paths."""

    ledger_dir = root / "results" / "ledgers" / benchmark_id
    stem = f"{parameter_id}_seed{seed}"
    return ledger_dir / f"{stem}.json", ledger_dir / f"{stem}.md"


def write_ledger(root: str | Path, record: dict) -> tuple[Path, Path]:
    """Write per-run JSON and Markdown ledgers plus an aggregate JSONL ledger."""

    repo_root = repository_root(Path(root))
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
                f"# {record['benchmark_id']} Reference Run",
                "",
                f"- Parameter set: `{record['parameter_id']}`",
                f"- Seed: `{record['seed']}`",
                f"- Branch: `{record['branch']}`",
                f"- Tier: `{record['theorem_tier']}`",
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
    jsonl_path = repo_root / "results" / "ledgers" / "ledger.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(normalized) + "\n")
    return json_path, md_path


def load_ledgers(root: str | Path) -> list[dict]:
    """Load all run ledgers from a repository root."""

    repo_root = repository_root(Path(root))
    ledgers: list[dict] = []
    for path in sorted((repo_root / "results" / "ledgers").rglob("*.json")):
        if path.name.endswith("_report.json"):
            continue
        ledgers.append(json.loads(path.read_text()))
    return ledgers
