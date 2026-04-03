from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from subsystem_emergence.benchmarking import run_reference_benchmark
from subsystem_emergence.io.paths import UnsafeTrackedRootError, repository_root
from subsystem_emergence.reports.archive.cross_domain import generate_cross_domain_application_package
from subsystem_emergence.reports.archive.paper_e import generate_paper_e_package
from subsystem_emergence.reports.archive import refresh as archive_refresh
from subsystem_emergence.reports.archive.refresh import refresh_archive_outputs
from subsystem_emergence.reports.archive.runtime import ArchiveBypassError, ArchiveGenerationContext, refresh_driver_context
from subsystem_emergence.reports.archive.validation import ArchiveEvidenceError


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _prepare_cross_domain_evidence(root: Path) -> None:
    for benchmark_id, case_id in (
        ("BP_Clickstream_Docs_Funnel", "reference"),
        ("BP_Clickstream_Docs_Funnel", "negative_detour"),
        ("BP_Support_Portal_Funnel", "reference"),
        ("BP_Support_Portal_Funnel", "negative_detour"),
        ("BP_Workflow_Queue_Funnel", "reference"),
        ("BP_Workflow_Queue_Funnel", "negative_detour"),
    ):
        run_reference_benchmark(benchmark_id, parameter_id=case_id, seed=0, root=root)


def test_explicit_repository_root_is_rejected_for_benchmark_runs() -> None:
    with pytest.raises(UnsafeTrackedRootError, match="tracked repository root"):
        run_reference_benchmark("BP_Linear_Two_Block", seed=0, root=repository_root())


def test_run_without_root_uses_auto_scratch_root() -> None:
    record = run_reference_benchmark("BP_Linear_Two_Block", seed=3)
    artifact_root = Path(record["metadata"]["artifact_root"])
    try:
        assert artifact_root != repository_root()
        assert (artifact_root / record["metadata"]["artifact_paths"]["run_manifest"]).exists()
    finally:
        if artifact_root.exists():
            shutil.rmtree(artifact_root)


def test_archive_refresh_fails_when_required_canonical_evidence_is_missing(tmp_path) -> None:
    run_reference_benchmark("BP_Clickstream_Docs_Funnel", parameter_id="reference", seed=0, root=tmp_path)

    with pytest.raises(ArchiveEvidenceError, match="BP_Support_Portal_Funnel"):
        refresh_archive_outputs(
            source_root=tmp_path,
            scratch_root=tmp_path / "scratch_incomplete",
            targets=["cross_domain"],
        )


def test_cross_domain_archive_refresh_is_deterministic(tmp_path) -> None:
    _prepare_cross_domain_evidence(tmp_path)

    first = refresh_archive_outputs(
        source_root=tmp_path,
        scratch_root=tmp_path / "scratch_one",
        targets=["cross_domain"],
    )
    second = refresh_archive_outputs(
        source_root=tmp_path,
        scratch_root=tmp_path / "scratch_two",
        targets=["cross_domain"],
    )

    first_outputs = first["generated_targets"]["cross_domain"]["archive_outputs"]
    second_outputs = second["generated_targets"]["cross_domain"]["archive_outputs"]
    assert first_outputs == second_outputs
    for relative_path in first_outputs:
        assert _sha256(tmp_path / "scratch_one" / relative_path) == _sha256(tmp_path / "scratch_two" / relative_path)


def test_archive_promotion_requires_force_to_overwrite_tracked_outputs(tmp_path) -> None:
    _prepare_cross_domain_evidence(tmp_path)
    collision_path = tmp_path / "reports/archive/generated/application/cross_domain_navigation/cross_domain_navigation_summary.json"
    collision_path.parent.mkdir(parents=True, exist_ok=True)
    collision_path.write_text("stale archive output")

    with pytest.raises(RuntimeError, match="force=True"):
        refresh_archive_outputs(
            source_root=tmp_path,
            scratch_root=tmp_path / "scratch_collision",
            targets=["cross_domain"],
            promote=True,
        )

    refresh_archive_outputs(
        source_root=tmp_path,
        scratch_root=tmp_path / "scratch_force",
        targets=["cross_domain"],
        promote=True,
        force=True,
    )
    assert "stale archive output" not in collision_path.read_text()


@pytest.mark.parametrize(
    "generator",
    (
        generate_cross_domain_application_package,
        generate_paper_e_package,
    ),
)
def test_direct_archive_generation_requires_refresh_context(tmp_path, generator) -> None:
    with pytest.raises(ArchiveBypassError, match="scratch_root context"):
        generator(root=tmp_path)


@pytest.mark.parametrize(
    "generator",
    (
        generate_cross_domain_application_package,
        generate_paper_e_package,
    ),
)
def test_direct_archive_generation_rejects_non_refresh_driver_context(tmp_path, generator) -> None:
    context = ArchiveGenerationContext(scratch_root=tmp_path, is_refresh_driver=False)

    with pytest.raises(ArchiveBypassError, match="context.is_refresh_driver must be True"):
        generator(root=tmp_path, context=context)


@pytest.mark.parametrize(
    "generator",
    (
        generate_cross_domain_application_package,
        generate_paper_e_package,
    ),
)
def test_direct_archive_generation_rejects_refresh_context_outside_driver(tmp_path, generator) -> None:
    context = refresh_driver_context(tmp_path)

    with pytest.raises(ArchiveBypassError, match="must be invoked through refresh.py"):
        generator(root=tmp_path, context=context)


@pytest.mark.parametrize(
    ("case", "match"),
    (
        ("missing_scratch_root", "scratch_root context"),
        ("missing_token", "execution token missing or invalid"),
        ("invalid_token", "execution token missing or invalid"),
    ),
)
@pytest.mark.parametrize(
    "generator",
    (
        generate_cross_domain_application_package,
        generate_paper_e_package,
    ),
)
def test_direct_archive_generation_rejects_invalid_refresh_tokens_and_roots(tmp_path, generator, case, match) -> None:
    if case == "missing_scratch_root":
        invalid_context = ArchiveGenerationContext(scratch_root=None, is_refresh_driver=True)
    elif case == "missing_token":
        invalid_context = ArchiveGenerationContext(scratch_root=tmp_path, is_refresh_driver=True)
    elif case == "invalid_token":
        invalid_context = ArchiveGenerationContext(scratch_root=tmp_path, is_refresh_driver=True, _driver_token=object())
    else:
        raise AssertionError(f"unsupported invalid context case: {case}")

    with pytest.raises(ArchiveBypassError, match=match):
        generator(root=tmp_path, context=invalid_context)


def test_refresh_archive_generation_rejects_mismatched_context_root(monkeypatch, tmp_path) -> None:
    _prepare_cross_domain_evidence(tmp_path)

    monkeypatch.setattr(
        archive_refresh,
        "refresh_driver_context",
        lambda scratch_root: refresh_driver_context(Path(scratch_root) / "mismatch"),
    )

    with pytest.raises(ArchiveBypassError, match="to match requested root"):
        refresh_archive_outputs(
            source_root=tmp_path,
            scratch_root=tmp_path / "scratch_mismatch",
            targets=["cross_domain"],
        )
