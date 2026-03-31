from __future__ import annotations

from pathlib import Path

from subsystem_emergence.application.cross_domain import generate_cross_domain_application_package
from subsystem_emergence.benchmarking import run_reference_benchmark


def test_cross_domain_package_generation_writes_expected_outputs() -> None:
    run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0)
    run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0, parameter_id="negative_detour")
    run_reference_benchmark("BP_Support_Portal_Funnel", seed=0)
    run_reference_benchmark("BP_Support_Portal_Funnel", seed=0, parameter_id="negative_detour")
    run_reference_benchmark("BP_Workflow_Queue_Funnel", seed=0)
    run_reference_benchmark("BP_Workflow_Queue_Funnel", seed=0, parameter_id="negative_detour")
    manifest = generate_cross_domain_application_package()
    root = Path(__file__).resolve().parents[1]
    for relative_path in manifest["outputs"].values():
        assert (root / relative_path).exists()
    assert (root / manifest["manifest_json"]).exists()
    assert (root / manifest["summary_json"]).exists()
    assert manifest["evidence_inventory"]["accepted_case_count"] == 3
    assert manifest["evidence_inventory"]["rejected_case_count"] == 3
    assert "\\" not in manifest["summary_json"]
    assert "\\" not in manifest["manifest_json"]


def test_cross_domain_summary_mentions_all_benchmarks() -> None:
    run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0)
    run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0, parameter_id="negative_detour")
    run_reference_benchmark("BP_Support_Portal_Funnel", seed=0)
    run_reference_benchmark("BP_Support_Portal_Funnel", seed=0, parameter_id="negative_detour")
    run_reference_benchmark("BP_Workflow_Queue_Funnel", seed=0)
    run_reference_benchmark("BP_Workflow_Queue_Funnel", seed=0, parameter_id="negative_detour")
    manifest = generate_cross_domain_application_package()
    root = Path(__file__).resolve().parents[1]
    summary = (root / manifest["summary_markdown"]).read_text()
    assert "BP_Clickstream_Docs_Funnel" in summary
    assert "BP_Support_Portal_Funnel" in summary
    assert "BP_Workflow_Queue_Funnel" in summary
    assert "reasons=`none`" in summary
    assert "singular_gap_below_package_floor" in summary
