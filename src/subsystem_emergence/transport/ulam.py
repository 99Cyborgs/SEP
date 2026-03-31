"""Ulam-style transfer-operator builders for transport benchmarks."""

from __future__ import annotations

import numpy as np


def _gaussian_kernel(grid_size: int, center: float, diffusion: float) -> np.ndarray:
    indices = np.arange(grid_size)
    distances = np.minimum(
        np.mod(indices - center, grid_size),
        np.mod(center - indices, grid_size),
    )
    weights = np.exp(-(distances**2) / max(diffusion, 1.0e-6))
    return weights / np.sum(weights)


def build_ulam_operator(
    grid_size: int,
    shift: float,
    *,
    diffusion: float,
    coherent_strength: float,
) -> np.ndarray:
    """Build a row-stochastic transport operator on a ring."""

    matrix = np.zeros((grid_size, grid_size), dtype=float)
    half = grid_size // 2
    for state in range(grid_size):
        center = state + shift
        kernel = _gaussian_kernel(grid_size, center, diffusion)
        if state < half:
            kernel[:half] *= coherent_strength
        else:
            kernel[half:] *= coherent_strength
        kernel /= np.sum(kernel)
        matrix[state] = kernel
    return matrix


def build_windowed_transport_flow(
    *,
    grid_size: int,
    window_count: int,
    base_shift: float,
    phase_increment: float,
    diffusion: float,
    coherent_strength: float,
) -> list[np.ndarray]:
    """Construct a concrete time-dependent transport benchmark."""

    operators = []
    for window in range(window_count):
        shift = base_shift + phase_increment * np.sin(2.0 * np.pi * window / max(window_count, 1))
        operators.append(
            build_ulam_operator(
                grid_size,
                shift,
                diffusion=diffusion,
                coherent_strength=coherent_strength,
            )
        )
    return operators
