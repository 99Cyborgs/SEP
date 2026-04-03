"""Refresh-only runtime guardrails for archive output generation."""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from pathlib import Path


_REFRESH_DRIVER_MODULE = "subsystem_emergence.reports.archive.refresh"
_REFRESH_DRIVER_TOKEN = object()


class ArchiveBypassError(RuntimeError):
    """Raised when archive generation bypasses the refresh driver."""


@dataclass(frozen=True)
class ArchiveGenerationContext:
    """Execution context required for scratch-rooted archive generation."""

    scratch_root: Path | None
    is_refresh_driver: bool = False
    _driver_token: object | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        resolved = None if self.scratch_root is None else Path(self.scratch_root).resolve()
        object.__setattr__(self, "scratch_root", resolved)


def refresh_driver_context(scratch_root: str | Path) -> ArchiveGenerationContext:
    """Create the refresh-issued context accepted by archive generators."""

    return ArchiveGenerationContext(
        scratch_root=Path(scratch_root).resolve(),
        is_refresh_driver=True,
        _driver_token=_REFRESH_DRIVER_TOKEN,
    )


def require_refresh_driver_context(
    context: ArchiveGenerationContext | None,
    *,
    target: str,
) -> ArchiveGenerationContext:
    """Reject archive generation that does not originate from refresh.py."""

    if context is None or context.scratch_root is None:
        raise ArchiveBypassError(
            f"{target} archive generation requires a scratch_root context issued by refresh.py."
        )
    if not context.is_refresh_driver:
        raise ArchiveBypassError(
            f"{target} archive generation bypassed refresh.py: context.is_refresh_driver must be True."
        )
    if context._driver_token is not _REFRESH_DRIVER_TOKEN:
        raise ArchiveBypassError(
            f"{target} archive generation bypassed refresh.py: refresh-issued execution token missing or invalid."
        )
    if not _called_from_refresh_driver():
        raise ArchiveBypassError(f"{target} archive generation must be invoked through refresh.py.")
    return context


def assert_context_matches_root(
    context: ArchiveGenerationContext,
    *,
    root: str | Path,
    target: str,
) -> None:
    """Ensure the refresh context and requested root resolve to the same scratch tree."""

    resolved_root = Path(root).resolve()
    if context.scratch_root != resolved_root:
        raise ArchiveBypassError(
            f"{target} archive generation requires scratch_root `{context.scratch_root}` "
            f"to match requested root `{resolved_root}`."
        )


def assert_archive_write_allowed(
    context: ArchiveGenerationContext | None,
    target_path: str | Path,
) -> None:
    """Reject writes into reports/archive unless the path is refresh-authorized."""

    normalized_target = Path(target_path).resolve()
    if "reports/archive" not in normalized_target.as_posix():
        return

    execution_context = require_refresh_driver_context(context, target="archive write")
    assert_context_matches_root(
        execution_context,
        root=execution_context.scratch_root,
        target="archive write",
    )
    expected_archive_root = execution_context.scratch_root / "reports" / "archive"
    try:
        normalized_target.relative_to(expected_archive_root)
    except ValueError as exc:
        raise ArchiveBypassError(
            f"archive write target `{normalized_target}` must stay under refresh scratch archive root "
            f"`{expected_archive_root}`."
        ) from exc


def _called_from_refresh_driver() -> bool:
    frame = inspect.currentframe()
    try:
        while frame is not None:
            if frame.f_globals.get("__name__") == _REFRESH_DRIVER_MODULE:
                return True
            frame = frame.f_back
        return False
    finally:
        del frame
