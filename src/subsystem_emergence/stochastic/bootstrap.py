"""Bootstrap utilities for stochastic confidence bounds."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def bootstrap_statistic(
    samples: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    *,
    replicates: int = 200,
    seed: int = 0,
) -> np.ndarray:
    """Bootstrap a scalar statistic."""

    rng = np.random.default_rng(seed)
    samples_array = np.asarray(samples, dtype=float)
    draws = []
    for _ in range(replicates):
        indices = rng.integers(0, samples_array.shape[0], size=samples_array.shape[0])
        draws.append(statistic(samples_array[indices]))
    return np.asarray(draws, dtype=float)


def bootstrap_ci(
    samples: np.ndarray,
    *,
    confidence: float = 0.95,
    replicates: int = 200,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for the sample mean."""

    draws = bootstrap_statistic(samples, lambda value: float(np.mean(value)), replicates=replicates, seed=seed)
    alpha = 0.5 * (1.0 - confidence)
    lower, upper = np.quantile(draws, [alpha, 1.0 - alpha])
    return float(lower), float(upper)
