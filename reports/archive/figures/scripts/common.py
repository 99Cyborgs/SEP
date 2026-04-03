"""Shared helpers for archived figure scripts."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

from subsystem_emergence.evidence import load_evidence_records
from subsystem_emergence.reports.archive.runtime import ArchiveBypassError


def records() -> list[dict]:
    return load_evidence_records(ROOT)


def _raise_direct_archive_write_blocked(target: str | Path) -> NoReturn:
    resolved_target = (ROOT / target).resolve() if not Path(target).is_absolute() else Path(target).resolve()
    raise ArchiveBypassError(
        f"Legacy archive figure scripts may not write `{resolved_target}` directly. "
        "Use `python -m subsystem_emergence.reports.archive.refresh` to materialize archive outputs."
    )


def ensure_output(relative_path: str) -> Path:
    _raise_direct_archive_write_blocked(relative_path)


def save_figure(path: Path) -> None:
    _raise_direct_archive_write_blocked(path)


def dump_recipe(output_relative_path: str, payload: dict) -> None:
    del payload
    _raise_direct_archive_write_blocked(output_relative_path)

