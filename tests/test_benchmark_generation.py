from __future__ import annotations

from subsystem_emergence.application.mobility import mobility_evaluation_cases
from subsystem_emergence.application.clickstream import clickstream_parameter_set
from subsystem_emergence.application.support import support_parameter_set
from subsystem_emergence.application.workflow import workflow_parameter_set
from subsystem_emergence.benchmarking import list_benchmarks, sample_parameters


def test_sample_parameters_for_linear_benchmark() -> None:
    parameters = sample_parameters("BP_Linear_Two_Block")
    assert "times" in parameters
    assert parameters["slow_count"] == 4


def test_application_benchmark_is_listed_and_parameterized() -> None:
    benchmark_ids = {item["benchmark_id"] for item in list_benchmarks()}
    parameters = sample_parameters("BP_Mobility_Chicago_Corridors", parameter_id="negative_weekend")
    assert "BP_Mobility_Chicago_Corridors" in benchmark_ids
    assert "BP_Mobility_Downtown_Routing_Instability" in benchmark_ids
    assert "BP_Mobility_NYC_East_Corridor" in benchmark_ids
    assert "BP_Clickstream_Docs_Funnel" in benchmark_ids
    assert "BP_Support_Portal_Funnel" in benchmark_ids
    assert "BP_Workflow_Queue_Funnel" in benchmark_ids
    assert "BP_T2_Same_Spectrum_Pair" in benchmark_ids
    assert "BP_T3_Window_Sensitivity_Pair" in benchmark_ids
    assert "BP_T4_Local_Validity_Pair" in benchmark_ids
    assert "BP_T5_Stochastic_Stress_Pair" in benchmark_ids
    assert parameters["case_label"] == "weekend_night"
    assert len(parameters["station_names"]) == 4


def test_external_negative_application_benchmark_is_parameterized() -> None:
    parameters = sample_parameters("BP_Mobility_Downtown_Routing_Instability", parameter_id="reference")
    assert parameters["case_label"] == "downtown_commute_routing_instability"
    assert parameters["total_trips"] >= 300
    assert len(parameters["station_names"]) == 4


def test_external_mixed_application_benchmark_is_parameterized() -> None:
    parameters = sample_parameters("BP_Mobility_NYC_East_Corridor", parameter_id="reference")
    assert parameters["case_label"] == "nyc_east_side_mixed"
    assert parameters["total_trips"] >= 1000
    assert len(parameters["station_names"]) == 4


def test_application_evaluation_cases_cover_positive_and_negative_profiles() -> None:
    cases = mobility_evaluation_cases()
    case_ids = {case["case_id"] for case in cases}
    profiles = {case["profile"] for case in cases}
    assert "weekday_reference" in case_ids
    assert "weekend_negative" in case_ids
    assert profiles == {"accepted", "failure"}


def test_clickstream_application_benchmark_is_parameterized() -> None:
    parameters = sample_parameters("BP_Clickstream_Docs_Funnel", parameter_id="reference")
    negative = clickstream_parameter_set("negative_detour")
    assert parameters["case_label"] == "stable_docs_funnel"
    assert parameters["total_sessions"] >= 900
    assert len(parameters["page_names"]) == 4
    assert negative["case_label"] == "docs_detour_negative"


def test_support_application_benchmark_is_parameterized() -> None:
    parameters = sample_parameters("BP_Support_Portal_Funnel", parameter_id="reference")
    negative = support_parameter_set("negative_detour")
    assert parameters["case_label"] == "stable_support_funnel"
    assert parameters["total_sessions"] >= 900
    assert len(parameters["page_names"]) == 4
    assert negative["case_label"] == "support_detour_negative"


def test_workflow_application_benchmark_is_parameterized() -> None:
    parameters = sample_parameters("BP_Workflow_Queue_Funnel", parameter_id="reference")
    negative = workflow_parameter_set("negative_detour")
    assert parameters["case_label"] == "stable_workflow_queue"
    assert parameters["total_cases"] >= 1000
    assert len(parameters["stage_names"]) == 4
    assert negative["case_label"] == "workflow_rework_negative"


def test_t2_same_spectrum_benchmark_exposes_both_branches() -> None:
    nonnormal = sample_parameters("BP_T2_Same_Spectrum_Pair", parameter_id="reference")
    normal = sample_parameters("BP_T2_Same_Spectrum_Pair", parameter_id="matched_normal")
    assert nonnormal["parameter_id"] == "matched_nonnormal"
    assert normal["parameter_id"] == "matched_normal"
    assert nonnormal["paired_parameter_id"] == "matched_normal"
    assert normal["paired_parameter_id"] == "matched_nonnormal"


def test_t3_window_sensitivity_benchmark_exposes_both_branches() -> None:
    mixed = sample_parameters("BP_T3_Window_Sensitivity_Pair", parameter_id="reference")
    positive = sample_parameters("BP_T3_Window_Sensitivity_Pair", parameter_id="matched_positive")
    assert mixed["case_label"] == "fast_drift_mixed"
    assert positive["case_label"] == "moderate_drift_positive"
    assert mixed["paired_parameter_id"] == "matched_positive"
    assert positive["paired_parameter_id"] == "reference"
    assert mixed["window_groups"] == [[0], [1, 2], [3], [4, 5]]


def test_t4_local_validity_benchmark_exposes_both_branches() -> None:
    breakdown = sample_parameters("BP_T4_Local_Validity_Pair", parameter_id="reference")
    matched = sample_parameters("BP_T4_Local_Validity_Pair", parameter_id="matched_local")
    assert breakdown["parameter_id"] == "amplitude_breakdown"
    assert matched["parameter_id"] == "matched_local"
    assert breakdown["paired_parameter_id"] == "matched_local"
    assert matched["paired_parameter_id"] == "amplitude_breakdown"


def test_t5_stochastic_stress_benchmark_exposes_both_branches() -> None:
    stress = sample_parameters("BP_T5_Stochastic_Stress_Pair", parameter_id="reference")
    matched = sample_parameters("BP_T5_Stochastic_Stress_Pair", parameter_id="matched_metastable")
    assert stress["parameter_id"] == "sample_stress"
    assert matched["parameter_id"] == "matched_metastable"
    assert stress["paired_parameter_id"] == "matched_metastable"
    assert matched["paired_parameter_id"] == "sample_stress"
