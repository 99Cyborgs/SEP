"""Autonomy-horizon utilities for sampled trajectories and affine predictions.

These helpers work on sampled leakage traces only. They intentionally avoid
interpolation so reported horizons remain tied to observed evidence points.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np


def autonomy_horizon(times: Sequence[float], leakage: Sequence[float], eta: float) -> float:
    """Return the largest sampled time whose leakage stays within the gate threshold."""

    times_array = np.asarray(times, dtype=float)
    leakage_array = np.asarray(leakage, dtype=float)
    if times_array.shape != leakage_array.shape:
        raise ValueError("times and leakage must have the same shape")
    admissible = times_array[leakage_array <= eta]
    return float(admissible[-1]) if admissible.size else 0.0


def predicted_autonomy_horizon(epsilon_s: float, rho: float, eta: float) -> float:
    """Return the affine-law horizon prediction under the L1 leakage surrogate.

    ``inf`` denotes zero coupling drift with admissible initial deformation;
    ``0.0`` denotes a threshold already violated at the start.
    """

    if eta <= epsilon_s:
        return 0.0
    if rho <= 0.0:
        return float("inf")
    return float((eta - epsilon_s) / rho)


def finite_window_autonomy_horizon(
    windows: Sequence[int], leakage: Sequence[float], eta: float
) -> int:
    """Return the last admissible sampled window index."""

    if len(windows) != len(leakage):
        raise ValueError("windows and leakage must have the same length")
    admissible = [window for window, value in zip(windows, leakage) if value <= eta]
    return int(admissible[-1]) if admissible else 0


def horizon_ratio(observed: float, predicted: float) -> float:
    """Return observed / predicted with explicit conventions for degenerate cases."""

    if np.isinf(predicted):
        return 1.0 if np.isinf(observed) else 0.0
    if predicted <= 0.0:
        return 1.0 if observed <= 0.0 else 0.0
    return float(observed / predicted)
