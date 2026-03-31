"""Monte Carlo drivers for stochastic benchmarks."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def run_mc(
    transition_matrix: np.ndarray,
    *,
    start_distribution: Sequence[float],
    steps: int,
    trajectories: int,
    seed: int = 0,
) -> np.ndarray:
    """Sample discrete-state trajectories from a transition matrix."""

    rng = np.random.default_rng(seed)
    matrix = np.asarray(transition_matrix, dtype=float)
    start = np.asarray(start_distribution, dtype=float)
    states = np.zeros((trajectories, steps + 1), dtype=int)
    states[:, 0] = rng.choice(matrix.shape[0], size=trajectories, p=start)
    for step in range(steps):
        for trajectory in range(trajectories):
            current = states[trajectory, step]
            states[trajectory, step + 1] = rng.choice(matrix.shape[0], p=matrix[current])
    return states


def ensemble_leakage_trajectory(
    trajectories: np.ndarray, source_states: set[int]
) -> np.ndarray:
    """Empirical leakage out of the source state set."""

    leakage = []
    for step in range(trajectories.shape[1]):
        inside = np.isin(trajectories[:, step], list(source_states))
        leakage.append(1.0 - float(np.mean(inside)))
    return np.asarray(leakage, dtype=float)
