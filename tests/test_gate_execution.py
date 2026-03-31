from __future__ import annotations

from subsystem_emergence.benchmarking import run_mobility_application_evaluation, run_reference_benchmark
from validation.gate_G1 import evaluate as evaluate_g1
from validation.gate_G2 import evaluate as evaluate_g2
from validation.gate_G3 import evaluate as evaluate_g3
from validation.gate_G4 import evaluate as evaluate_g4
from validation.gate_G5 import evaluate as evaluate_g5
from validation.gate_G6 import evaluate as evaluate_g6


def test_gate_g1_executes_after_linear_run() -> None:
    run_reference_benchmark("BP_Linear_Two_Block", seed=2)
    result = evaluate_g1()
    assert result["gate"] == "G1"
    assert "metrics" in result


def test_gate_g3_executes_after_transport_run() -> None:
    run_reference_benchmark("BP_Windowed_Transport_Flow", seed=0)
    run_reference_benchmark("BP_T3_Window_Sensitivity_Pair", seed=0, parameter_id="reference")
    result = evaluate_g3()
    assert result["gate"] == "G3"
    assert result["passed"] is True
    assert result["metrics"]["horizon_gain"] >= 0.0
    assert result["metrics"]["window_sensitivity_regrouped_horizon_gain"] >= 0.0
    assert result["metrics"]["mixed_transport_pair_count"] >= 1


def test_gate_g4_executes_after_nonlinear_run() -> None:
    run_reference_benchmark("BP_Weakly_Nonlinear_Slow_Manifold", seed=0)
    run_reference_benchmark("BP_T4_Local_Validity_Pair", seed=0, parameter_id="reference")
    result = evaluate_g4()
    assert result["gate"] == "G4"
    assert result["passed"] is True
    assert result["metrics"]["projector_deformation"] <= 0.35
    assert result["metrics"]["nonlinear_pair_count"] >= 1
    assert result["metrics"]["nonlinear_pair_margin_delta"] > 0.0


def test_gate_g5_reports_stochastic_stress_metrics() -> None:
    run_reference_benchmark("BP_Noisy_Metastable_Network", seed=0)
    run_reference_benchmark("BP_T5_Stochastic_Stress_Pair", seed=0, parameter_id="reference")
    result = evaluate_g5()
    assert result["gate"] == "G5"
    assert result["passed"] is True
    assert result["metrics"]["stochastic_pair_count"] >= 1
    assert result["metrics"]["stochastic_pair_width_delta"] > 0.0


def test_gate_g6_executes_after_required_reference_runs() -> None:
    for benchmark_id in (
        "BP_Linear_Two_Block",
        "BP_Nearly_Decomposable_Chain",
        "BP_Non_Normal_Shear",
        "BP_Windowed_Transport_Flow",
        "BP_Weakly_Nonlinear_Slow_Manifold",
        "BP_Noisy_Metastable_Network",
    ):
        run_reference_benchmark(benchmark_id, seed=0)
    run_mobility_application_evaluation(seed=0)
    run_reference_benchmark("BP_Mobility_Downtown_Routing_Instability", seed=0)
    run_reference_benchmark("BP_Mobility_NYC_East_Corridor", seed=0)
    run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0)
    run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0, parameter_id="negative_detour")
    run_reference_benchmark("BP_Support_Portal_Funnel", seed=0)
    run_reference_benchmark("BP_Support_Portal_Funnel", seed=0, parameter_id="negative_detour")
    run_reference_benchmark("BP_Workflow_Queue_Funnel", seed=0)
    run_reference_benchmark("BP_Workflow_Queue_Funnel", seed=0, parameter_id="negative_detour")
    result = evaluate_g6()
    assert result["gate"] == "G6"
    assert result["passed"] is True
    assert result["metrics"]["primary_records_present"] is True
    assert result["metrics"]["refinement_ok"] is True
    assert result["metrics"]["application_enforced"] is True
    assert result["metrics"]["application_enforcement_ok"] is True
    assert result["metrics"]["accepted_application_case_count"] >= 8
    assert result["metrics"]["rejected_application_case_count"] >= 6
    assert result["metrics"]["missing_application_case_count"] == 0
    assert result["metrics"]["mismatched_application_case_count"] == 0


def test_gate_g2_reports_delay_refinement_metrics() -> None:
    for benchmark_id in ("BP_Non_Normal_Shear", "BP_Random_Gap_Ensemble", "BP_Delay_Coupled_Pair"):
        run_reference_benchmark(benchmark_id, seed=0)
    run_reference_benchmark("BP_T2_Same_Spectrum_Pair", seed=0, parameter_id="reference")
    result = evaluate_g2()
    assert result["gate"] == "G2"
    assert result["metrics"]["delay_record_count"] >= 1
    assert result["metrics"]["delay_refinement_ok"] is True
    assert result["metrics"]["delay_horizon_span_max"] >= 0.0
    assert result["metrics"]["delay_adjacent_stability_max"] >= 0.0
    assert result["metrics"]["delay_correspondence_deformation_max"] >= 0.0
    assert result["metrics"]["pseudospectral_proxy_max"] >= result["metrics"]["pseudospectral_proxy_mean"]
    assert result["metrics"]["same_spectrum_counterexample_count"] >= 1
