"""Canonical repository and artifact path helpers."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


RESULTS_DIRNAME = "results"
EVIDENCE_DIRNAME = "evidence"
INDEXES_DIRNAME = "indexes"
VALIDATION_GATES_DIRNAME = "validation_gates"
LEGACY_LEDGERS_DIRNAME = "ledgers"
TMP_DIRNAME = "tmp"


class UnsafeTrackedRootError(RuntimeError):
    """Raised when a mutating workflow targets the tracked repository root."""


def repository_root(start: Path | None = None) -> Path:
    """Locate the repository root by walking upward to pyproject.toml."""

    candidate = Path(start or __file__).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for path in [candidate] + list(candidate.parents):
        if (path / "pyproject.toml").exists():
            return path
    raise FileNotFoundError("could not locate repository root")


def artifact_root(root: str | Path | None = None) -> Path:
    """Resolve the artifact/output root for generated evidence."""

    if root is not None:
        return Path(root).resolve()
    return repository_root()


def create_scratch_root(label: str, *, base_dir: str | Path | None = None) -> Path:
    """Create an ignored scratch root for safe mutating workflows."""

    parent = Path(base_dir).resolve() if base_dir is not None else repository_root() / TMP_DIRNAME / label
    parent.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=f"{label}_", dir=parent)).resolve()


def resolve_mutation_root(
    root: str | Path | None,
    *,
    purpose: str,
    scratch_label: str,
    allow_repository_root: bool = False,
    require_explicit_root: bool = False,
    recommended_action: str | None = None,
) -> Path:
    """Resolve a write root while preventing tracked repository-root mutation."""

    repo_root = repository_root()
    if root is None:
        resolved = repo_root if require_explicit_root else create_scratch_root(scratch_label)
    else:
        resolved = Path(root).resolve()
    if resolved == repo_root and not allow_repository_root:
        message = (
            f"Refusing to write {purpose} into the tracked repository root at `{repo_root}`. "
            "Use an ignored scratch root instead."
        )
        if recommended_action:
            message += f" {recommended_action}"
        message += " Set `dangerously_allow_repo_root=True` only for intentional tracked-output updates."
        raise UnsafeTrackedRootError(message)
    return resolved


def repo_relative_path(path: str | Path, root: str | Path | None = None) -> str:
    """Return a portable repository-relative POSIX path."""

    repo_root = artifact_root(root)
    return Path(path).resolve().relative_to(repo_root).as_posix()


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


def results_root(root: str | Path | None = None) -> Path:
    """Return the root directory for all generated repository results."""

    return artifact_root(root) / RESULTS_DIRNAME


def evidence_root(root: str | Path | None = None) -> Path:
    """Return the canonical evidence-bundle root."""

    return results_root(root) / EVIDENCE_DIRNAME


def indexes_root(root: str | Path | None = None) -> Path:
    """Return the canonical derived-index root."""

    return results_root(root) / INDEXES_DIRNAME


def validation_gates_root(root: str | Path | None = None) -> Path:
    """Return the canonical validation-gate report root."""

    return results_root(root) / VALIDATION_GATES_DIRNAME


def legacy_ledgers_root(root: str | Path | None = None) -> Path:
    """Return the compatibility-only legacy ledger root."""

    return results_root(root) / LEGACY_LEDGERS_DIRNAME


def application_validation_root(root: str | Path | None = None) -> Path:
    """Return the canonical application validation summary directory."""

    return indexes_root(root) / "application_validation"
