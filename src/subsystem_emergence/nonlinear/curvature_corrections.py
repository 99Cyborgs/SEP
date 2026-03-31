"""Curvature-aware law corrections."""

from __future__ import annotations

import numpy as np


def quadratic_manifold_fit(slow_states: np.ndarray, fast_states: np.ndarray) -> np.ndarray:
    """Fit a quadratic map from slow to fast coordinates."""

    x = np.asarray(slow_states, dtype=float)
    y = np.asarray(fast_states, dtype=float)
    if x.ndim != 2:
        raise ValueError("slow_states must be two-dimensional")
    features = [np.ones(x.shape[0])]
    for column in range(x.shape[1]):
        features.append(x[:, column])
    for i in range(x.shape[1]):
        for j in range(i, x.shape[1]):
            features.append(x[:, i] * x[:, j])
    design = np.column_stack(features)
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    return coefficients


def curvature_indicator(slow_states: np.ndarray, fast_states: np.ndarray) -> float:
    """Norm of quadratic curvature terms in a fitted slow-manifold map."""

    coefficients = quadratic_manifold_fit(slow_states, fast_states)
    quadratic = coefficients[1 + slow_states.shape[1] :]
    return float(np.linalg.norm(quadratic))
