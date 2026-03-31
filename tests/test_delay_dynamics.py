from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from subsystem_emergence.benchmarking import run_reference_benchmark, sample_parameters
from subsystem_emergence.delay import analyze_delay_system, delay_refinement_diagnostics, solve_linear_delay
from validation.gate_G2 import evaluate as evaluate_g2


def test_delay_solver_matches_ode_limit_when_delayed_term_is_zero() -> None:
    a0 = np.array([[-0.4, 0.2], [0.0, -0.6]])
    a_delay = np.zeros((2, 2))
    times = np.linspace(0.0, 1.0, 11)
    history = lambda time: np.array([1.0 - 0.1 * time, -0.25], dtype=float)
    solution = solve_linear_delay(
        a0,
        a_delay,
        delay=0.2,
        times=times,
        history=history,
        step_size=0.01,
    )
    initial = history(0.0)
    expected = np.asarray([expm(float(time) * a0) @ initial for time in times], dtype=float)
    assert np.max(np.abs(solution["states"] - expected)) < 2.0e-4


def test_delay_solver_returns_finite_states_for_smooth_history() -> None:
    a0 = np.array([[-0.6, 0.8], [0.0, -0.9]])
    a_delay = np.array([[0.7, 0.0], [0.2, 0.6]])
    times = np.linspace(0.0, 1.6, 9)
    history = lambda time: np.array([np.cos(time), 0.5 * np.sin(time)], dtype=float)
    solution = solve_linear_delay(
        a0,
        a_delay,
        delay=0.4,
        times=times,
        history=history,
        step_size=0.0125,
    )
    assert np.isfinite(solution["states"]).all()
    assert solution["states"].shape == (len(times), 2)


def test_delay_analysis_reports_finite_nonnegative_observables() -> None:
    result = analyze_delay_system(
        np.array([[-0.9, 2.2], [0.0, -1.05]]),
        np.array([[1.3, 0.0], [0.25, 1.22]]),
        delay=0.4,
        times=np.linspace(0.0, 4.8, 13).tolist(),
        eta=0.69,
        slow_count=2,
        block_sizes=[1, 1],
        history_grid_size=6,
        step_size=0.0125,
    )
    assert result["history_operator"].shape == (12, 12)
    assert result["transient_amplification_score"] >= 0.0
    assert result["spectral_gap"] >= 0.0
    assert result["singular_gap"] >= 0.0
    assert all(value >= 0.0 for value in result["leakage_trajectory"])


def test_delay_benchmark_parameters_expose_true_delay_fields() -> None:
    parameters = sample_parameters("BP_Delay_Coupled_Pair")
    assert parameters["delay"] == 0.4
    assert parameters["history_kind"] == "nodal_piecewise_linear"
    assert "surrogate" not in parameters
    assert "delay_steps" not in parameters


def test_delay_reference_run_writes_true_delay_ledger() -> None:
    record = run_reference_benchmark("BP_Delay_Coupled_Pair", seed=0)
    assert record["law_selection_summary"]["best_law"] == "L3"
    assert record["observables"]["transient_amplification_score"] >= 1.5
    assert "surrogate_warning" not in record["observables"]["transportability_metrics"]
    assert record["observables"]["numerical_refinement_metrics"]["surrogate_relative_span"] <= 0.3
    assert not any("surrogate" in note.lower() for note in record["notes"])


def test_gate_g2_executes_after_delay_path_runs() -> None:
    for benchmark_id in ("BP_Non_Normal_Shear", "BP_Random_Gap_Ensemble", "BP_Delay_Coupled_Pair"):
        run_reference_benchmark(benchmark_id, seed=0)
    result = evaluate_g2()
    assert result["gate"] == "G2"
    assert result["passed"] is True
    assert result["metrics"]["delay_refinement_ok"] is True


def test_delay_refinement_diagnostics_report_stable_reference_ladder() -> None:
    diagnostics = delay_refinement_diagnostics(
        np.array([[-0.9, 2.2], [0.0, -1.05]]),
        np.array([[1.3, 0.0], [0.25, 1.22]]),
        delay=0.4,
        times=np.linspace(0.0, 4.8, 13).tolist(),
        eta=0.69,
        slow_count=2,
        block_sizes=[1, 1],
        history_grid_sizes=[6, 8, 10],
        step_sizes=[0.0125, 0.00625, 0.003125],
    )
    assert diagnostics["refinement_axis"] == "history_grid_and_step_ladder"
    assert diagnostics["autonomy_horizon_relative_span"] == 0.0
    assert diagnostics["transient_relative_span"] <= 0.05
    assert diagnostics["block_residual_relative_span"] <= 0.05
    assert diagnostics["surrogate_relative_span"] <= 0.3
    assert len(diagnostics["levels"]) == 3


def test_delay_refinement_diagnostics_expose_unstable_coarse_ladder() -> None:
    diagnostics = delay_refinement_diagnostics(
        np.array([[-0.9, 2.2], [0.0, -1.05]]),
        np.array([[1.3, 0.0], [0.25, 1.22]]),
        delay=0.4,
        times=np.linspace(0.0, 4.8, 13).tolist(),
        eta=0.69,
        slow_count=2,
        block_sizes=[1, 1],
        history_grid_sizes=[2, 4, 6],
        step_sizes=[0.2, 0.05, 0.0125],
    )
    assert diagnostics["surrogate_relative_span"] > 0.3
