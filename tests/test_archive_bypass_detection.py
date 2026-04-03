from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from subsystem_emergence.reports.archive import runtime as archive_runtime
from subsystem_emergence.reports.archive.runtime import (
    ArchiveBypassError,
    assert_archive_write_allowed,
    refresh_driver_context,
)
from tests.test_archive_write_invariant import collect_unauthorized_archive_writes


def _load_legacy_archive_common():
    common_path = Path(__file__).resolve().parents[1] / "reports" / "archive" / "figures" / "scripts" / "common.py"
    spec = importlib.util.spec_from_file_location("legacy_archive_common", common_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"failed to load {common_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_static_invariant_detects_synthetic_archive_writer(tmp_path) -> None:
    fake_writer = tmp_path / "fake_writer.py"
    fake_writer.write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "",
                "def write_archive_payload(root):",
                "    path = Path(root) / 'reports' / 'archive' / 'synthetic' / 'payload.json'",
                "    path.parent.mkdir(parents=True, exist_ok=True)",
                "    path.write_text('{}')",
            ]
        )
    )

    violations = collect_unauthorized_archive_writes(tmp_path)

    assert len(violations) == 2
    assert {violation.kind for violation in violations} == {"mkdir", "write_text"}
    assert all(violation.source_path == fake_writer for violation in violations)


def test_static_invariant_detects_helper_mediated_archive_writer(tmp_path) -> None:
    helper_module = tmp_path / "archive_helpers.py"
    helper_module.write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "",
                "def write_archive_payload(target_path):",
                "    path = Path(target_path)",
                "    path.parent.mkdir(parents=True, exist_ok=True)",
                "    path.write_text('{}')",
            ]
        )
    )
    caller_module = tmp_path / "caller.py"
    caller_module.write_text(
        "\n".join(
            [
                "from archive_helpers import write_archive_payload",
                "",
                "def run():",
                "    write_archive_payload('reports/archive/synthetic/helper_payload.json')",
            ]
        )
    )

    violations = collect_unauthorized_archive_writes(tmp_path)

    helper_bypass = [
        violation
        for violation in violations
        if violation.source_path == caller_module and violation.kind == "write_archive_payload"
    ]
    assert helper_bypass
    assert helper_bypass[0].detail == "reports/archive/synthetic/helper_payload.json"


def test_runtime_guard_rejects_synthetic_archive_write_without_refresh_context(tmp_path) -> None:
    target_path = tmp_path / "reports" / "archive" / "synthetic" / "payload.json"

    def fake_writer() -> None:
        assert_archive_write_allowed(None, target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text("{}")

    with pytest.raises(ArchiveBypassError, match="scratch_root context"):
        fake_writer()


def test_legacy_archive_helpers_reject_direct_archive_outputs() -> None:
    legacy_common = _load_legacy_archive_common()

    with pytest.raises(ArchiveBypassError, match="Legacy archive figure scripts may not write"):
        legacy_common.ensure_output("reports/archive/figures/legacy_blocked.png")


def test_runtime_guard_rejects_archive_targets_outside_refresh_scratch(monkeypatch, tmp_path) -> None:
    scratch_root = tmp_path / "scratch_root"
    target_path = tmp_path / "elsewhere" / "reports" / "archive" / "synthetic" / "payload.json"
    context = refresh_driver_context(scratch_root)

    monkeypatch.setattr(archive_runtime, "_called_from_refresh_driver", lambda: True)

    with pytest.raises(ArchiveBypassError, match="must stay under refresh scratch archive root"):
        assert_archive_write_allowed(context, target_path)
