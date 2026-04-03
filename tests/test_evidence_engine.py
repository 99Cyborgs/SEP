from __future__ import annotations

import json

from subsystem_emergence.benchmarking import run_reference_benchmark


def test_reference_run_emits_canonical_evidence_bundle(tmp_path) -> None:
    record = run_reference_benchmark("BP_Linear_Two_Block", seed=0, root=tmp_path)
    artifact_paths = record["metadata"]["artifact_paths"]
    required_artifacts = {
        "environment_fingerprint",
        "solver_config",
        "seed_record",
        "benchmark_case_snapshot",
        "observables_summary",
        "residual_diagnostics",
        "gate_report",
        "acceptance_decision",
        "regression_check",
        "run_manifest",
    }
    assert required_artifacts.issubset(artifact_paths)
    for relative_path in artifact_paths.values():
        assert (tmp_path / relative_path).exists()
    decision = json.loads((tmp_path / artifact_paths["acceptance_decision"]).read_text())
    assert decision["decision_status"] == "accepted"
    assert decision["success"] is True


def test_negative_control_updates_failure_and_traceability_indexes(tmp_path) -> None:
    run_reference_benchmark("BP_T4_Local_Validity_Pair", seed=0, parameter_id="reference", root=tmp_path)
    run_reference_benchmark("BP_Delay_Coupled_Pair", seed=0, root=tmp_path)
    run_index = json.loads((tmp_path / "results" / "indexes" / "run_index.json").read_text())
    failure_index = json.loads((tmp_path / "results" / "indexes" / "failure_index.json").read_text())
    traceability = json.loads((tmp_path / "results" / "indexes" / "claim_traceability.json").read_text())
    delay_entry = next(entry for entry in run_index["runs"] if entry["benchmark_id"] == "BP_Delay_Coupled_Pair")
    assert any(entry["benchmark_id"] == "BP_T4_Local_Validity_Pair" for entry in failure_index["entries"])
    assert delay_entry["decision_status"] == "qualified"
    assert delay_entry["implementation_status"] == "surrogate"
    assert delay_entry["evidence_class"] == "surrogate_delay"
    t4_entry = next(entry for entry in traceability["claims"] if entry["claim"]["claim_id"] == "T4_weakly_nonlinear")
    case_entry = next(case for case in t4_entry["cases"] if case["benchmark_id"] == "BP_T4_Local_Validity_Pair" and case["case_id"] == "reference")
    assert case_entry["decision_status"] == "expected_failure_confirmed"
    assert case_entry["artifact_paths"]["acceptance_decision"].endswith("acceptance_decision.json")
