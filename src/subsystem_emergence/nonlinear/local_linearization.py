"""Local linearization utilities for weakly nonlinear systems."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from scipy.integrate import solve_ivp


def local_jacobian(
    function: Callable[[float, np.ndarray], np.ndarray],
    state: np.ndarray,
    time: float,
    step: float = 1.0e-6,
) -> np.ndarray:
    """Finite-difference Jacobian of a vector field."""

    state_array = np.asarray(state, dtype=float)
    base = np.asarray(function(time, state_array), dtype=float)
    jacobian = np.zeros((state_array.size, state_array.size), dtype=float)
    for index in range(state_array.size):
        delta = np.zeros_like(state_array)
        delta[index] = step
        shifted = np.asarray(function(time, state_array + delta), dtype=float)
        jacobian[:, index] = (shifted - base) / step
    return jacobian


def integrate_trajectory(
    function: Callable[[float, np.ndarray], np.ndarray],
    initial_state: Sequence[float],
    times: Sequence[float],
) -> np.ndarray:
    """Integrate a nonlinear benchmark trajectory."""

    time_array = np.asarray(times, dtype=float)
    solution = solve_ivp(
        function,
        (float(time_array[0]), float(time_array[-1])),
        np.asarray(initial_state, dtype=float),
        t_eval=time_array,
        rtol=1.0e-8,
        atol=1.0e-8,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return solution.y.T


def jacobian_sequence(
    function: Callable[[float, np.ndarray], np.ndarray],
    states: np.ndarray,
    times: Sequence[float],
) -> list[np.ndarray]:
    """Local Jacobians along a trajectory."""

    return [
        local_jacobian(function, state, float(time))
        for state, time in zip(np.asarray(states), np.asarray(times), strict=True)
    ]
