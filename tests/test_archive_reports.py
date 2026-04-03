from __future__ import annotations

import json

from subsystem_emergence.benchmarking import run_mobility_application_evaluation, run_reference_benchmark
from subsystem_emergence.reports.archive.refresh import refresh_archive_outputs


def test_cross_domain_archive_refresh_reads_canonical_evidence_without_ledgers(tmp_path) -> None:
    for benchmark_id, case_id in (
        ("BP_Clickstream_Docs_Funnel", "reference"),
        ("BP_Clickstream_Docs_Funnel", "negative_detour"),
        ("BP_Support_Portal_Funnel", "reference"),
        ("BP_Support_Portal_Funnel", "negative_detour"),
        ("BP_Workflow_Queue_Funnel", "reference"),
        ("BP_Workflow_Queue_Funnel", "negative_detour"),
    ):
        run_reference_benchmark(benchmark_id, parameter_id=case_id, seed=0, root=tmp_path)

    refresh = refresh_archive_outputs(
        source_root=tmp_path,
        scratch_root=tmp_path / "scratch_cross_domain",
        targets=["cross_domain"],
    )
    manifest = refresh["generated_targets"]["cross_domain"]["manifest"]
    summary = json.loads((tmp_path / "scratch_cross_domain" / manifest["summary_json"]).read_text())

    assert not (tmp_path / "results" / "ledgers").exists()
    assert all(case["run_manifest"].startswith("results/evidence/") for case in summary["cases"])
    assert (tmp_path / "scratch_cross_domain" / manifest["summary_json"]).exists()
    assert (tmp_path / "scratch_cross_domain" / manifest["summary_markdown"]).exists()


def test_paper_e_archive_refresh_reads_canonical_evidence_without_ledgers(tmp_path) -> None:
    run_mobility_application_evaluation(seed=0, root=tmp_path)
    run_reference_benchmark("BP_Mobility_Downtown_Routing_Instability", seed=0, root=tmp_path)
    run_reference_benchmark("BP_Mobility_NYC_East_Corridor", seed=0, root=tmp_path)

    refresh = refresh_archive_outputs(
        source_root=tmp_path,
        scratch_root=tmp_path / "scratch_paper_e",
        targets=["paper_e"],
    )
    manifest = refresh["generated_targets"]["paper_e"]["manifest"]

    assert not (tmp_path / "results" / "ledgers").exists()
    assert manifest["summary_json"].startswith("results/indexes/application_validation/")
    assert manifest["evidence_inventory"]["accepted_weekday_case"].startswith("results/evidence/")
    assert manifest["evidence_inventory"]["external_negative_case"].startswith("results/evidence/")
    assert (tmp_path / "scratch_paper_e" / manifest["outputs"]["weekday_leakage_png"]).exists()
    assert (tmp_path / "scratch_paper_e" / manifest["outputs"]["robustness_summary_markdown"]).exists()
