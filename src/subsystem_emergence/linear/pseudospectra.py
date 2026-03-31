"""Nonnormality diagnostics."""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm


def departure_from_normality(matrix: np.ndarray) -> float:
    """Frobenius norm of the commutator A*A - AA*."""

    commutator = matrix.conj().T @ matrix - matrix @ matrix.conj().T
    return float(np.linalg.norm(commutator, "fro"))


def transient_amplification(matrix: np.ndarray, times: np.ndarray) -> float:
    """Return sup_t ||e^{tA}|| exp(-t alpha(A))."""

    alpha = float(np.max(np.linalg.eigvals(matrix).real))
    profile = []
    for time in np.asarray(times, dtype=float):
        profile.append(np.linalg.norm(expm(time * matrix), 2) * np.exp(-time * alpha))
    return float(np.max(profile))


def semigroup_growth_profile(matrix: np.ndarray, times: np.ndarray) -> list[float]:
    """Return the semigroup growth curve."""

    return [float(np.linalg.norm(expm(float(time) * matrix), 2)) for time in times]


def pseudospectral_proxy(
    matrix: np.ndarray, epsilon: float = 1.0e-2, imag_bound: float = 5.0, samples: int = 41
) -> float:
    """Crude resolvent-based pseudospectral proxy."""

    alpha = float(np.max(np.linalg.eigvals(matrix).real))
    grid = np.linspace(-imag_bound, imag_bound, samples)
    proxies = []
    identity = np.eye(matrix.shape[0], dtype=complex)
    for value in grid:
        z = alpha + epsilon + 1j * value
        sigma_min = np.min(np.linalg.svd(z * identity - matrix, compute_uv=False))
        proxies.append(1.0 / max(float(sigma_min), 1.0e-12))
    return float(max(proxies))
