"""Stochastic propagator estimation."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from subsystem_emergence.core.horizons import autonomy_horizon, predicted_autonomy_horizon
from subsystem_emergence.core.leakage import ensemble_summary
from subsystem_emergence.linear.spectral import analyze_linear_generator


def estimate_propagator(trajectories: np.ndarray, state_count: int) -> np.ndarray:
    """Estimate a transition matrix from sampled trajectories."""

    counts = np.zeros((state_count, state_count), dtype=float)
    for row in trajectories:
        for source, target in zip(row[:-1], row[1:], strict=True):
            counts[source, target] += 1.0
    row_sums = counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0.0] = 1.0
    return counts / row_sums


def exact_leakage_trajectory(
    transition_matrix: np.ndarray,
    source_states: Sequence[int],
    steps: int,
) -> np.ndarray:
    """Exact leakage trajectory from a source state set."""

    matrix = np.asarray(transition_matrix, dtype=float)
    state_count = matrix.shape[0]
    initial = np.zeros(state_count, dtype=float)
    initial[list(source_states)] = 1.0 / len(source_states)
    leakage = []
    distribution = initial
    source_mask = np.zeros(state_count, dtype=float)
    source_mask[list(source_states)] = 1.0
    for _ in range(steps + 1):
        leakage.append(1.0 - float(np.dot(distribution, source_mask)))
        distribution = distribution @ matrix
    return np.asarray(leakage, dtype=float)


def analyze_stochastic_transition(
    transition_matrix: np.ndarray,
    *,
    source_states: Sequence[int],
    slow_count: int,
    steps: int,
    eta: float,
) -> dict[str, object]:
    """Analyze a stochastic benchmark through its propagator."""

    generator = transition_matrix - np.eye(transition_matrix.shape[0])
    linear_result = analyze_linear_generator(
        generator,
        slow_count=slow_count,
        block_sizes=[1] * slow_count,
        times=list(range(steps + 1)),
        eta=eta,
    )
    leakage = exact_leakage_trajectory(transition_matrix, source_states, steps)
    ensemble = ensemble_summary(leakage)
    linear_result.update(
        {
            "ensemble_averaged_leakage": ensemble["mean"],
            "leakage_variance": ensemble["variance"],
            "autonomy_horizon": autonomy_horizon(list(range(steps + 1)), leakage.tolist(), eta),
            "predicted_autonomy_horizon": predicted_autonomy_horizon(
                float(linear_result["projector_deformation"]),
                float(linear_result["block_residual_norm"]),
                eta,
            ),
            "leakage_trajectory": leakage.tolist(),
        }
    )
    return linear_result
