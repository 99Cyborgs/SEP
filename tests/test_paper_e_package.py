from __future__ import annotations

from pathlib import Path

from subsystem_emergence.application.paper_e import generate_paper_e_package
from subsystem_emergence.benchmarking import run_mobility_application_evaluation, run_reference_benchmark


def test_paper_e_package_generation_writes_expected_outputs() -> None:
    run_mobility_application_evaluation(seed=0)
    run_reference_benchmark("BP_Mobility_Downtown_Routing_Instability", seed=0)
    run_reference_benchmark("BP_Mobility_NYC_East_Corridor", seed=0)
    manifest = generate_paper_e_package()
    root = Path(__file__).resolve().parents[1]
    outputs = manifest["outputs"]
    for relative_path in outputs.values():
        assert (root / relative_path).exists()
    assert (root / manifest["manifest_json"]).exists()
    assert manifest["evidence_inventory"]["weekday_sweep_accepted"] is True
    assert manifest["evidence_inventory"]["negative_case_rejected"] is True
    assert manifest["evidence_inventory"]["external_negative_rejected"] is True
    assert (root / manifest["evidence_inventory"]["external_negative_case"]).exists()
    assert (root / manifest["evidence_inventory"]["external_mixed_case"]).exists()
    assert manifest["evidence_inventory"]["external_mixed_case_present"] is True
    assert "\\" not in manifest["summary_json"]
    assert "\\" not in manifest["manifest_json"]


def test_paper_e_table_includes_key_summary_fields() -> None:
    run_mobility_application_evaluation(seed=0)
    run_reference_benchmark("BP_Mobility_Downtown_Routing_Instability", seed=0)
    run_reference_benchmark("BP_Mobility_NYC_East_Corridor", seed=0)
    manifest = generate_paper_e_package()
    root = Path(__file__).resolve().parents[1]
    table = (root / manifest["outputs"]["robustness_summary_markdown"]).read_text()
    assert "Weekday sweep accepted" in table
    assert "Negative case rejected" in table
    assert "Weekday minimum singular gap" in table
    assert "Weekday maximum deformation" in table
    assert "Weekday maximum refinement span" in table
    assert "External downtown rejection labels" in table
    assert "NYC mixed failure labels" in table
