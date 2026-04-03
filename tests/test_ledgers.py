from __future__ import annotations

from subsystem_emergence.benchmarking import run_mobility_application_evaluation, run_reference_benchmark
from subsystem_emergence.io.schema import validate_record


def test_reference_run_writes_canonical_manifest_without_compatibility_ledgers_by_default(tmp_path) -> None:
    record = run_reference_benchmark("BP_Linear_Two_Block", seed=1, root=tmp_path)
    compatibility = record["metadata"]["compatibility_artifacts"]
    manifest_path = tmp_path / record["metadata"]["artifact_paths"]["run_manifest"]
    assert record["benchmark_id"] == "BP_Linear_Two_Block"
    assert manifest_path.exists()
    assert record["metadata"]["compatibility_mode"] == "disabled"
    assert compatibility == {}
    assert not (tmp_path / "results" / "ledgers").exists()


def test_reference_run_emits_compatibility_ledgers_only_when_requested(tmp_path) -> None:
    record = run_reference_benchmark(
        "BP_Linear_Two_Block",
        seed=1,
        root=tmp_path,
        emit_compatibility_ledgers=True,
    )
    compatibility = record["metadata"]["compatibility_artifacts"]
    assert record["metadata"]["compatibility_mode"] == "legacy_ledgers_opt_in"
    assert (tmp_path / compatibility["legacy_ledger_json"]).exists()
    assert (tmp_path / compatibility["legacy_ledger_markdown"]).exists()


def test_transport_reference_run_writes_transport_diagnostics(tmp_path) -> None:
    record = run_reference_benchmark("BP_Windowed_Transport_Flow", seed=0, root=tmp_path)
    transport = record["observables"]["transportability_metrics"]
    assert not validate_record(record)
    assert transport["coherent_vs_frozen_horizon_gain"] >= 0.0
    assert "carrier_tracking" in transport
    assert "coherent_window_leakage" in transport
    assert "window_sensitivity" in transport
    assert transport["window_sensitivity"]["regrouped_window_count"] == 4


def test_t3_window_sensitivity_ledgers_capture_positive_vs_mixed_geometry(tmp_path) -> None:
    mixed = run_reference_benchmark("BP_T3_Window_Sensitivity_Pair", seed=0, parameter_id="reference", root=tmp_path)
    positive = run_reference_benchmark(
        "BP_T3_Window_Sensitivity_Pair", seed=0, parameter_id="matched_positive", root=tmp_path
    )
    assert not validate_record(mixed)
    assert not validate_record(positive)
    mixed_transport = mixed["observables"]["transportability_metrics"]
    positive_transport = positive["observables"]["transportability_metrics"]
    contrast = mixed_transport["positive_negative_transport_pair"]
    assert mixed_transport["coherent_vs_frozen_horizon_gain"] <= positive_transport["coherent_vs_frozen_horizon_gain"]
    assert mixed_transport["carrier_tracking"]["mean_deformation"] > positive_transport["carrier_tracking"]["mean_deformation"]
    assert mixed_transport["window_sensitivity"]["regrouped_carrier_mean_deformation"] > positive_transport["window_sensitivity"]["regrouped_carrier_mean_deformation"]
    assert contrast["paired_horizon_gain"] > contrast["current_horizon_gain"]
    assert contrast["current_carrier_deformation"] > contrast["paired_carrier_deformation"]


def test_nonlinear_reference_run_writes_local_tracking_diagnostics(tmp_path) -> None:
    record = run_reference_benchmark("BP_Weakly_Nonlinear_Slow_Manifold", seed=0, root=tmp_path)
    transport = record["observables"]["transportability_metrics"]
    tracking = transport["projector_tracking"]
    local = record["observables"]["local_validity_metrics"]
    assert not validate_record(record)
    assert record["law_selection_summary"]["best_law"] == "L2"
    assert record["observables"]["projector_deformation"] <= 0.35
    assert tracking["adjacent_mean_deformation"] == record["observables"]["projector_deformation"]
    assert tracking["anchor_mean_deformation"] >= tracking["adjacent_mean_deformation"]
    assert local["local_validity_margin"] > 0.0
    assert local["fast_slaving_defect"] < 0.1


def test_t4_local_validity_pair_captures_breakdown_geometry(tmp_path) -> None:
    breakdown = run_reference_benchmark("BP_T4_Local_Validity_Pair", seed=0, parameter_id="reference", root=tmp_path)
    matched = run_reference_benchmark("BP_T4_Local_Validity_Pair", seed=0, parameter_id="matched_local", root=tmp_path)
    assert not validate_record(breakdown)
    assert not validate_record(matched)
    breakdown_local = breakdown["observables"]["local_validity_metrics"]
    matched_local = matched["observables"]["local_validity_metrics"]
    contrast = breakdown["observables"]["transportability_metrics"]["local_validity_pair"]
    assert breakdown_local["local_validity_margin"] < matched_local["local_validity_margin"]
    assert breakdown_local["fast_slaving_defect"] > matched_local["fast_slaving_defect"]
    assert breakdown_local["anchor_projector_deformation"] > matched_local["anchor_projector_deformation"]
    assert matched_local["l2_minus_l1_rmse"] > breakdown_local["l2_minus_l1_rmse"]
    assert contrast["paired_l2_minus_l1_rmse"] > contrast["current_l2_minus_l1_rmse"]


def test_nonnormal_reference_run_writes_true_refinement_metric(tmp_path) -> None:
    record = run_reference_benchmark("BP_Non_Normal_Shear", seed=0, root=tmp_path)
    refinement = record["observables"]["numerical_refinement_metrics"]
    assert not validate_record(record)
    assert record["observables"]["transient_amplification_score"] >= 1.5
    assert record["observables"]["pseudospectral_proxy"] >= 100.0
    assert refinement["refinement_axis"] == "time_grid_density"
    assert refinement["max_relative_span"] <= 0.3
    assert refinement["spectral_gap_relative_span"] <= 0.3
    assert refinement["block_residual_relative_span"] <= 0.3
    assert refinement["transient_relative_span"] <= 0.3


def test_same_spectrum_counterexample_ledgers_capture_failure_geometry(tmp_path) -> None:
    nonnormal = run_reference_benchmark("BP_T2_Same_Spectrum_Pair", seed=0, parameter_id="reference", root=tmp_path)
    normal = run_reference_benchmark("BP_T2_Same_Spectrum_Pair", seed=0, parameter_id="matched_normal", root=tmp_path)
    assert not validate_record(nonnormal)
    assert not validate_record(normal)
    contrast = nonnormal["observables"]["transportability_metrics"]["same_spectrum_counterexample"]
    assert abs(contrast["gap_difference"]) <= 0.01
    assert nonnormal["observables"]["transient_amplification_score"] > normal["observables"]["transient_amplification_score"] * 5.0
    assert nonnormal["observables"]["pseudospectral_proxy"] > normal["observables"]["pseudospectral_proxy"] * 10.0
    nonnormal_l3_gain = nonnormal["law_fits"]["L1"]["test_rmse"] - nonnormal["law_fits"]["L3"]["test_rmse"]
    normal_l3_gain = normal["law_fits"]["L1"]["test_rmse"] - normal["law_fits"]["L3"]["test_rmse"]
    assert nonnormal_l3_gain > normal_l3_gain
    assert contrast["current_l3_minus_l1_rmse"] > contrast["paired_l3_minus_l1_rmse"]


def test_delay_reference_run_writes_delay_semigroup_metrics(tmp_path) -> None:
    record = run_reference_benchmark("BP_Delay_Coupled_Pair", seed=0, root=tmp_path)
    refinement = record["observables"]["numerical_refinement_metrics"]
    delay = record["observables"]["delay_semigroup_metrics"]
    assert not validate_record(record)
    assert delay["autonomy_horizon_span"] == refinement["autonomy_horizon_relative_span"]
    assert delay["sampled_surrogate_span"] == refinement["surrogate_relative_span"]
    assert delay["adjacent_terminal_projector_deformation_max"] >= 0.0
    assert delay["bounded_correspondence_summary"]["constant_history_projector_deformation"] >= 0.0
    assert len(delay["levels"]) == len(delay["history_operator_dimensions"])


def test_application_reference_run_writes_real_fixture_provenance(tmp_path) -> None:
    record = run_reference_benchmark("BP_Mobility_Chicago_Corridors", seed=0, root=tmp_path)
    transport = record["observables"]["transportability_metrics"]
    assert not validate_record(record)
    assert record["branch"] == "application"
    assert record["parameter_id"] == "reference"
    assert transport["source_archive"] == "202401-divvy-tripdata.zip"
    assert len(record["parameters"]["station_names"]) == 4
    assert record["observables"]["singular_gap"] >= 0.45
    assert record["observables"]["coherent_projector_deformation"] <= 0.35


def test_application_negative_run_preserves_failure_labels(tmp_path) -> None:
    record = run_reference_benchmark("BP_Mobility_Chicago_Corridors", seed=0, parameter_id="negative_weekend", root=tmp_path)
    refinement = record["observables"]["numerical_refinement_metrics"]
    assert not validate_record(record)
    assert record["parameter_id"] == "negative_weekend"
    assert "carrier_failure" in record["failure_labels"]
    assert "numerical_artifact_failure" in record["failure_labels"]
    assert refinement["max_relative_span"] > 0.3


def test_external_negative_application_run_preserves_geometry_failure_labels(tmp_path) -> None:
    record = run_reference_benchmark("BP_Mobility_Downtown_Routing_Instability", seed=0, root=tmp_path)
    assert not validate_record(record)
    assert record["branch"] == "application"
    assert record["parameters"]["total_trips"] >= 300
    assert record["observables"]["coherent_projector_deformation"] >= 0.9
    assert "carrier_failure" in record["failure_labels"]
    assert "coupling_failure" in record["failure_labels"]


def test_external_mixed_application_run_preserves_mixed_posture(tmp_path) -> None:
    record = run_reference_benchmark("BP_Mobility_NYC_East_Corridor", seed=0, root=tmp_path)
    refinement = record["observables"]["numerical_refinement_metrics"]
    assert not validate_record(record)
    assert record["branch"] == "application"
    assert record["parameters"]["total_trips"] >= 1000
    assert record["observables"]["singular_gap"] >= 0.3
    assert record["observables"]["coherent_projector_deformation"] >= 0.45
    assert refinement["max_relative_span"] <= 0.1
    assert "carrier_failure" in record["failure_labels"]
    assert "coupling_failure" in record["failure_labels"]


def test_clickstream_application_reference_run_writes_cross_domain_evidence(tmp_path) -> None:
    record = run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0, root=tmp_path)
    transport = record["observables"]["transportability_metrics"]
    assert not validate_record(record)
    assert record["branch"] == "application"
    assert record["parameters"]["total_sessions"] >= 900
    assert transport["source_archive"] == "docs_navigation_funnel_q1_2026.json"
    assert record["observables"]["singular_gap"] >= 0.39
    assert record["observables"]["coherent_projector_deformation"] <= 0.08


def test_clickstream_application_negative_run_preserves_failure_labels(tmp_path) -> None:
    record = run_reference_benchmark("BP_Clickstream_Docs_Funnel", seed=0, parameter_id="negative_detour", root=tmp_path)
    assert not validate_record(record)
    assert record["parameter_id"] == "negative_detour"
    assert "carrier_failure" in record["failure_labels"]
    assert "coupling_failure" in record["failure_labels"]


def test_support_application_reference_run_writes_cross_domain_evidence(tmp_path) -> None:
    record = run_reference_benchmark("BP_Support_Portal_Funnel", seed=0, root=tmp_path)
    transport = record["observables"]["transportability_metrics"]
    assert not validate_record(record)
    assert record["branch"] == "application"
    assert record["parameters"]["total_sessions"] >= 900
    assert transport["source_archive"] == "support_navigation_funnel_q1_2026.json"
    assert record["observables"]["singular_gap"] >= 0.35
    assert record["observables"]["coherent_projector_deformation"] <= 0.15


def test_support_application_negative_run_preserves_failure_labels(tmp_path) -> None:
    record = run_reference_benchmark("BP_Support_Portal_Funnel", seed=0, parameter_id="negative_detour", root=tmp_path)
    assert not validate_record(record)
    assert record["parameter_id"] == "negative_detour"
    assert "carrier_failure" in record["failure_labels"]
    assert "gap_failure" in record["failure_labels"]


def test_workflow_application_negative_run_preserves_package_rejection_without_taxonomy_coupling_failure(tmp_path) -> None:
    record = run_reference_benchmark("BP_Workflow_Queue_Funnel", seed=0, parameter_id="negative_detour", root=tmp_path)
    assert not validate_record(record)
    assert record["parameter_id"] == "negative_detour"
    assert "carrier_failure" in record["failure_labels"]
    assert "coupling_failure" not in record["failure_labels"]


def test_stochastic_reference_run_writes_uncertainty_metrics(tmp_path) -> None:
    record = run_reference_benchmark("BP_Noisy_Metastable_Network", seed=0, root=tmp_path)
    uncertainty = record["observables"]["stochastic_uncertainty_metrics"]
    assert not validate_record(record)
    assert uncertainty["bootstrap_width"] <= 0.1
    assert uncertainty["confidence_bounded_horizon"] >= 5.0


def test_t5_stochastic_stress_pair_captures_uncertainty_failure_geometry(tmp_path) -> None:
    stress = run_reference_benchmark("BP_T5_Stochastic_Stress_Pair", seed=0, parameter_id="reference", root=tmp_path)
    matched = run_reference_benchmark(
        "BP_T5_Stochastic_Stress_Pair", seed=0, parameter_id="matched_metastable", root=tmp_path
    )
    assert not validate_record(stress)
    assert not validate_record(matched)
    stress_uncertainty = stress["observables"]["stochastic_uncertainty_metrics"]
    matched_uncertainty = matched["observables"]["stochastic_uncertainty_metrics"]
    contrast = stress["observables"]["transportability_metrics"]["stochastic_uncertainty_pair"]
    assert stress_uncertainty["bootstrap_width"] > matched_uncertainty["bootstrap_width"]
    assert stress_uncertainty["confidence_bounded_horizon"] < matched_uncertainty["confidence_bounded_horizon"]
    assert stress_uncertainty["estimation_error_proxy"] > matched_uncertainty["estimation_error_proxy"]
    assert contrast["current_bootstrap_width"] > contrast["paired_bootstrap_width"]


def test_application_evaluation_writes_summary_and_classifies_profiles(tmp_path) -> None:
    summary = run_mobility_application_evaluation(seed=0, root=tmp_path)
    summary_path = tmp_path / "results" / "indexes" / "application_validation" / "BP_Mobility_Chicago_Corridors_validation_matrix.json"
    assert summary_path.exists()
    assert summary["aggregate_validation_summary"]["weekday_all_cases_successful"] is True
    assert summary["aggregate_validation_summary"]["negative_case_expected_failure_confirmed"] is True
    weekday_reference = next(case for case in summary["cases"] if case["case_id"] == "reference")
    weekend_negative = next(case for case in summary["cases"] if case["case_id"] == "negative_weekend")
    assert weekday_reference["decision_status"] == "accepted"
    assert weekday_reference["acceptance_decision"]["advisory_failures_present"] == ["coupling_failure"]
    assert weekend_negative["decision_status"] == "expected_failure_confirmed"
    assert weekend_negative["acceptance_decision"]["success"] is True
    assert "run_manifest" in weekday_reference["artifact_paths"]
    assert "numerical_artifact_failure" in weekend_negative["failure_labels"]
