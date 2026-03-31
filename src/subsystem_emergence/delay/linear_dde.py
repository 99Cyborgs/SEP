"""Minimal fixed-lag linear delay-differential analysis."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

from subsystem_emergence.core.horizons import autonomy_horizon, predicted_autonomy_horizon
from subsystem_emergence.core.identifiability import numerical_refinement_metric
from subsystem_emergence.core.projectors import orthonormal_basis, orth_projector, projector_deformation


HistoryFunction = Callable[[float], np.ndarray]


def _ordered_eigensystem(operator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eig(np.asarray(operator, dtype=complex))
    order = np.argsort(np.abs(eigenvalues))[::-1]
    return eigenvalues[order], eigenvectors[:, order]


def _history_grid(delay: float, history_grid_size: int) -> np.ndarray:
    if history_grid_size < 2:
        raise ValueError("history_grid_size must be at least 2")
    return np.linspace(-float(delay), 0.0, int(history_grid_size))


def _history_from_samples(
    sample_times: np.ndarray,
    sample_values: np.ndarray,
) -> HistoryFunction:
    values = np.asarray(sample_values, dtype=float)
    times = np.asarray(sample_times, dtype=float)
    if values.ndim != 2:
        raise ValueError("history samples must be a 2D array")

    def history(time: float) -> np.ndarray:
        query = float(time)
        if query <= times[0]:
            return values[0].copy()
        if query >= times[-1]:
            return values[-1].copy()
        return np.asarray(
            [np.interp(query, times, values[:, index]) for index in range(values.shape[1])],
            dtype=float,
        )

    return history


def _canonical_history(
    delay: float,
    history_grid_size: int,
    state_dimension: int,
    flat_index: int,
) -> HistoryFunction:
    grid = _history_grid(delay, history_grid_size)
    values = np.zeros((history_grid_size, state_dimension), dtype=float)
    values.reshape(-1)[flat_index] = 1.0
    return _history_from_samples(grid, values)


def _constant_history_basis(
    delay: float,
    history_grid_size: int,
    state_dimension: int,
) -> np.ndarray:
    grid = _history_grid(delay, history_grid_size)
    columns = []
    for coordinate in range(state_dimension):
        values = np.zeros((history_grid_size, state_dimension), dtype=float)
        values[:, coordinate] = 1.0 + 0.15 * (grid / max(delay, 1.0e-12))
        columns.append(values.reshape(-1))
    return orthonormal_basis(np.column_stack(columns), rank=state_dimension)


def _state_from_history(
    time: float,
    known_times: np.ndarray,
    known_states: np.ndarray,
    history: HistoryFunction,
) -> np.ndarray:
    query = float(time)
    if query <= 0.0:
        return np.asarray(history(query), dtype=float)
    if query <= known_times[0]:
        return known_states[0].copy()
    if query >= known_times[-1]:
        return known_states[-1].copy()
    return np.asarray(
        [np.interp(query, known_times, known_states[:, index]) for index in range(known_states.shape[1])],
        dtype=float,
    )


def solve_linear_delay(
    a0: np.ndarray,
    a_delay: np.ndarray,
    *,
    delay: float,
    times: Sequence[float],
    history: HistoryFunction,
    step_size: float,
) -> dict[str, np.ndarray]:
    """Integrate x'(t) = A0 x(t) + A_delay x(t - delay) on a fixed grid."""

    a0_array = np.asarray(a0, dtype=float)
    a_delay_array = np.asarray(a_delay, dtype=float)
    times_array = np.asarray(times, dtype=float)
    if times_array.ndim != 1 or times_array.size == 0:
        raise ValueError("times must be a non-empty one-dimensional sequence")
    if np.any(np.diff(times_array) < 0.0):
        raise ValueError("times must be sorted in ascending order")
    delay_value = float(delay)
    step = float(step_size)
    if delay_value <= 0.0:
        raise ValueError("delay must be positive")
    if step <= 0.0 or step > delay_value:
        raise ValueError("step_size must be positive and no larger than delay")

    state_dimension = a0_array.shape[0]
    horizon = float(times_array[-1])
    step_count = int(np.ceil(horizon / step))
    integration_times = np.linspace(0.0, step_count * step, step_count + 1)
    states = np.zeros((integration_times.size, state_dimension), dtype=float)
    states[0] = np.asarray(history(0.0), dtype=float)

    for index in range(integration_times.size - 1):
        time = float(integration_times[index])
        current = states[index]
        past_times = integration_times[: index + 1]
        past_states = states[: index + 1]

        def delayed(query: float) -> np.ndarray:
            return _state_from_history(query, past_times, past_states, history)

        def rhs(stage_time: float, stage_state: np.ndarray) -> np.ndarray:
            return a0_array @ stage_state + a_delay_array @ delayed(stage_time - delay_value)

        k1 = rhs(time, current)
        k2 = rhs(time + 0.5 * step, current + 0.5 * step * k1)
        k3 = rhs(time + 0.5 * step, current + 0.5 * step * k2)
        k4 = rhs(time + step, current + step * k3)
        states[index + 1] = current + (step / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    sampled_states = np.asarray(
        [_state_from_history(time, integration_times, states, history) for time in times_array],
        dtype=float,
    )
    return {
        "integration_times": integration_times,
        "integration_states": states,
        "times": times_array,
        "states": sampled_states,
    }


def _sample_history_snapshot(
    end_time: float,
    delay: float,
    history_grid_size: int,
    integration_times: np.ndarray,
    integration_states: np.ndarray,
    history: HistoryFunction,
) -> np.ndarray:
    snapshot_times = end_time + _history_grid(delay, history_grid_size)
    samples = [
        _state_from_history(time, integration_times, integration_states, history)
        for time in snapshot_times
    ]
    return np.asarray(samples, dtype=float).reshape(-1)


def _history_operator(
    a0: np.ndarray,
    a_delay: np.ndarray,
    *,
    delay: float,
    history_grid_size: int,
    step_size: float,
) -> np.ndarray:
    state_dimension = a0.shape[0]
    history_dimension = state_dimension * history_grid_size
    columns = []
    for basis_index in range(history_dimension):
        history = _canonical_history(delay, history_grid_size, state_dimension, basis_index)
        solution = solve_linear_delay(
            a0,
            a_delay,
            delay=delay,
            times=[delay],
            history=history,
            step_size=step_size,
        )
        columns.append(
            _sample_history_snapshot(
                delay,
                delay,
                history_grid_size,
                solution["integration_times"],
                solution["integration_states"],
                history,
            )
        )
    return np.column_stack(columns)


def _terminal_state_projector(history_basis: np.ndarray, state_dimension: int) -> np.ndarray:
    """Project the learned history basis back onto the physical state slice."""

    terminal_block = np.asarray(history_basis, dtype=complex)[-state_dimension:, :]
    return orth_projector(orthonormal_basis(terminal_block, rank=terminal_block.shape[1]))


def _operator_power_leakage(
    operator: np.ndarray,
    projector: np.ndarray,
    steps: Sequence[int],
) -> list[float]:
    identity = np.eye(operator.shape[0], dtype=complex)
    values: list[float] = []
    for step in steps:
        propagated = np.linalg.matrix_power(operator, int(step))
        values.append(float(np.linalg.norm((identity - projector) @ propagated @ projector, 2)))
    return values


def _block_slices(block_sizes: Sequence[int]) -> list[slice]:
    start = 0
    slices: list[slice] = []
    for size in block_sizes:
        stop = start + int(size)
        slices.append(slice(start, stop))
        start = stop
    return slices


def _reduced_block_leakage(
    reduced_operator: np.ndarray,
    block_sizes: Sequence[int],
    steps: Sequence[int],
) -> list[float]:
    slices = _block_slices(block_sizes)
    values: list[float] = []
    identity = np.eye(reduced_operator.shape[0], dtype=complex)
    for step in steps:
        propagated = np.linalg.matrix_power(reduced_operator, int(step))
        best = 0.0
        for block in slices:
            projector = np.zeros_like(reduced_operator, dtype=complex)
            size = block.stop - block.start
            projector[block, block] = np.eye(size, dtype=complex)
            best = max(
                best,
                float(np.linalg.norm((identity - projector) @ propagated @ projector, 2)),
            )
        values.append(best)
    return values


def _cross_subsystem_transfer_rate(reduced_operator: np.ndarray, block_sizes: Sequence[int]) -> float:
    residual = np.array(reduced_operator, dtype=complex, copy=True)
    for block in _block_slices(block_sizes):
        residual[block, block] = 0.0
    return float(np.linalg.norm(residual, 2))


def _reduced_model_forecast_error(
    operator: np.ndarray,
    basis: np.ndarray,
    reduced_operator: np.ndarray,
    steps: Sequence[int],
) -> float:
    projector = basis @ basis.conj().T
    errors = []
    for step in steps:
        propagated = np.linalg.matrix_power(operator, int(step))
        reduced = np.linalg.matrix_power(reduced_operator, int(step))
        full = projector @ propagated @ projector
        reduced_lifted = basis @ reduced @ basis.conj().T
        errors.append(np.linalg.norm(full - reduced_lifted, 2))
    return float(np.mean(errors))


def _transient_profile(operator: np.ndarray, steps: Sequence[int]) -> list[float]:
    eigenvalues = np.linalg.eigvals(operator)
    radius = max(float(np.max(np.abs(eigenvalues))), 1.0e-12)
    values = []
    for step in steps:
        propagated = np.linalg.matrix_power(operator, int(step))
        values.append(float(np.linalg.norm(propagated, 2) / (radius**int(step))))
    return values


def analyze_delay_system(
    a0: np.ndarray,
    a_delay: np.ndarray,
    *,
    delay: float,
    times: Sequence[float],
    eta: float,
    slow_count: int,
    block_sizes: Sequence[int],
    history_grid_size: int,
    step_size: float,
) -> dict[str, object]:
    """Analyze a fixed-lag linear delay system through sampled history evolution."""

    if slow_count != a0.shape[0]:
        raise ValueError("validation path expects slow_count to match the physical state dimension")
    time_array = np.asarray(times, dtype=float)
    discrete_steps = np.rint(time_array / float(delay)).astype(int)
    if np.any(np.abs(time_array - discrete_steps * float(delay)) > 1.0e-8):
        raise ValueError("delay validation path expects times to be integer multiples of delay")

    operator = _history_operator(
        np.asarray(a0, dtype=float),
        np.asarray(a_delay, dtype=float),
        delay=delay,
        history_grid_size=history_grid_size,
        step_size=step_size,
    )
    eigenvalues, eigenvectors = _ordered_eigensystem(operator)
    estimated_basis = orthonormal_basis(eigenvectors[:, :slow_count], rank=slow_count)
    reference_basis = _constant_history_basis(delay, history_grid_size, a0.shape[0])
    estimated_projector = orth_projector(estimated_basis)
    reference_projector = orth_projector(reference_basis)
    reduced_operator = estimated_basis.conj().T @ operator @ estimated_basis
    autonomous = _operator_power_leakage(operator, estimated_projector, discrete_steps.tolist())
    reduced_leakage = _reduced_block_leakage(reduced_operator, block_sizes, discrete_steps.tolist())
    total_leakage = [max(a, b) for a, b in zip(autonomous, reduced_leakage, strict=True)]
    deformation = projector_deformation(estimated_projector, reference_projector)
    rho = _cross_subsystem_transfer_rate(reduced_operator, block_sizes)
    transient_profile = _transient_profile(reduced_operator, discrete_steps.tolist())
    singular_values = np.linalg.svd(operator, compute_uv=False)
    spectral_gap = 0.0
    singular_gap = 0.0
    if eigenvalues.size > slow_count:
        spectral_gap = float(np.abs(eigenvalues[slow_count - 1]) - np.abs(eigenvalues[slow_count]))
    if singular_values.size > slow_count:
        singular_gap = float(singular_values[slow_count - 1] - singular_values[slow_count])

    return {
        "spectral_gap": spectral_gap,
        "singular_gap": singular_gap,
        "projector_deformation": deformation,
        "block_residual_norm": rho,
        "leakage_trajectory": total_leakage,
        "autonomy_horizon": autonomy_horizon(time_array.tolist(), total_leakage, eta),
        "predicted_autonomy_horizon": predicted_autonomy_horizon(deformation, rho, eta),
        "cross_subsystem_transfer_rate": rho,
        "reduced_model_forecast_error": _reduced_model_forecast_error(
            operator,
            estimated_basis,
            reduced_operator,
            discrete_steps.tolist(),
        ),
        "transient_amplification_score": float(max(transient_profile)),
        "eigenvector_condition_number": float(np.linalg.cond(eigenvectors)),
        "projector": estimated_projector,
        "history_basis": estimated_basis,
        "reduced_operator": reduced_operator,
        "history_operator": operator,
        "constant_history_projector_deformation": deformation,
        "terminal_state_projector": _terminal_state_projector(estimated_basis, a0.shape[0]),
        "fit_gamma": np.asarray(transient_profile, dtype=float),
    }


def delay_refinement_diagnostics(
    a0: np.ndarray,
    a_delay: np.ndarray,
    *,
    delay: float,
    times: Sequence[float],
    eta: float,
    slow_count: int,
    block_sizes: Sequence[int],
    history_grid_sizes: Sequence[int],
    step_sizes: Sequence[float],
) -> dict[str, object]:
    """Compare the sampled-history delay diagnostics across a refinement ladder."""

    if len(history_grid_sizes) != len(step_sizes):
        raise ValueError("history_grid_sizes and step_sizes must have the same length")
    if len(history_grid_sizes) < 2:
        raise ValueError("delay refinement diagnostics require at least two refinement levels")

    analyses = []
    levels = []
    state_dimension = int(np.asarray(a0, dtype=float).shape[0])
    for history_grid_size, step_size in zip(history_grid_sizes, step_sizes, strict=True):
        result = analyze_delay_system(
            a0,
            a_delay,
            delay=delay,
            times=times,
            eta=eta,
            slow_count=slow_count,
            block_sizes=block_sizes,
            history_grid_size=int(history_grid_size),
            step_size=float(step_size),
        )
        analyses.append(result)
        levels.append(
            {
                "history_grid_size": int(history_grid_size),
                "step_size": float(step_size),
                "history_operator_dimension": int(result["history_operator"].shape[0]),
                "autonomy_horizon": float(result["autonomy_horizon"]),
                "transient_amplification_score": float(result["transient_amplification_score"]),
                "block_residual_norm": float(result["block_residual_norm"]),
                "spectral_gap": float(result["spectral_gap"]),
                "singular_gap": float(result["singular_gap"]),
                "constant_history_projector_deformation": float(result["constant_history_projector_deformation"]),
            }
        )

    adjacent_terminal_projector_deformation = []
    adjacent_horizon_relative_change = []
    for left, right in zip(analyses[:-1], analyses[1:], strict=True):
        left_projector = np.asarray(left["terminal_state_projector"], dtype=complex)
        right_projector = np.asarray(right["terminal_state_projector"], dtype=complex)
        adjacent_terminal_projector_deformation.append(projector_deformation(left_projector, right_projector))
        left_horizon = float(left["autonomy_horizon"])
        right_horizon = float(right["autonomy_horizon"])
        adjacent_horizon_relative_change.append(abs(left_horizon - right_horizon) / max(abs(right_horizon), 1.0))

    metric_map = {
        "autonomy_horizon_relative_span": numerical_refinement_metric([float(item["autonomy_horizon"]) for item in analyses]),
        "transient_relative_span": numerical_refinement_metric([float(item["transient_amplification_score"]) for item in analyses]),
        "block_residual_relative_span": numerical_refinement_metric([float(item["block_residual_norm"]) for item in analyses]),
        "spectral_gap_relative_span": numerical_refinement_metric([float(item["spectral_gap"]) for item in analyses]),
        "singular_gap_relative_span": numerical_refinement_metric([float(item["singular_gap"]) for item in analyses]),
    }
    surrogate_relative_span = float(
        max(
            metric_map["spectral_gap_relative_span"]["max_relative_span"],
            metric_map["singular_gap_relative_span"]["max_relative_span"],
        )
    )
    max_relative_span = float(
        max(
            metric_map["autonomy_horizon_relative_span"]["max_relative_span"],
            metric_map["transient_relative_span"]["max_relative_span"],
            metric_map["block_residual_relative_span"]["max_relative_span"],
            surrogate_relative_span,
        )
    )
    mean_value = float(
        np.mean(
            [
                metric_map["autonomy_horizon_relative_span"]["mean"],
                metric_map["transient_relative_span"]["mean"],
                metric_map["block_residual_relative_span"]["mean"],
                metric_map["spectral_gap_relative_span"]["mean"],
                metric_map["singular_gap_relative_span"]["mean"],
            ]
        )
    )
    constant_history_projector_span = numerical_refinement_metric(
        [float(item["constant_history_projector_deformation"]) for item in analyses]
    )
    terminal_correspondence = [
        float(np.linalg.norm(np.asarray(item["terminal_state_projector"], dtype=complex), 2))
        for item in analyses
    ]
    return {
        "refinement_axis": "history_grid_and_step_ladder",
        "history_grid_sizes": [int(value) for value in history_grid_sizes],
        "step_sizes": [float(value) for value in step_sizes],
        "history_operator_dimensions": [int(level["history_operator_dimension"]) for level in levels],
        "levels": levels,
        "max_relative_span": max_relative_span,
        "mean": mean_value,
        "autonomy_horizon_relative_span": float(metric_map["autonomy_horizon_relative_span"]["max_relative_span"]),
        "transient_relative_span": float(metric_map["transient_relative_span"]["max_relative_span"]),
        "block_residual_relative_span": float(metric_map["block_residual_relative_span"]["max_relative_span"]),
        "spectral_gap_relative_span": float(metric_map["spectral_gap_relative_span"]["max_relative_span"]),
        "singular_gap_relative_span": float(metric_map["singular_gap_relative_span"]["max_relative_span"]),
        "surrogate_relative_span": surrogate_relative_span,
        "constant_history_projector_relative_span": float(constant_history_projector_span["max_relative_span"]),
        "adjacent_terminal_projector_deformation_max": float(max(adjacent_terminal_projector_deformation, default=0.0)),
        "adjacent_horizon_relative_change_max": float(max(adjacent_horizon_relative_change, default=0.0)),
        "terminal_state_dimension": state_dimension,
        "terminal_correspondence_norm_min": float(min(terminal_correspondence, default=0.0)),
        "terminal_correspondence_norm_max": float(max(terminal_correspondence, default=0.0)),
    }
