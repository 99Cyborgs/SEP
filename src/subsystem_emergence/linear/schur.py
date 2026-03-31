"""Schur-based invariant subspace helpers."""

from __future__ import annotations

import numpy as np
from scipy.linalg import schur

from subsystem_emergence.core.projectors import orthonormal_basis


def complex_schur(matrix: np.ndarray):
    """Return complex Schur factors."""

    return schur(matrix, output="complex")


def extract_slow_subspace_schur(matrix: np.ndarray, slow_count: int) -> np.ndarray:
    """Extract the slow Schur carrier by sorting on real part."""

    eigenvalues = np.linalg.eigvals(matrix)
    cutoff = np.sort(eigenvalues.real)[::-1][slow_count - 1]
    sorted_schur = schur(
        matrix,
        output="complex",
        sort=lambda value: value.real >= cutoff - 1.0e-12,
    )
    if len(sorted_schur) == 3:
        _, schur_vectors, selected = sorted_schur
        if selected == slow_count:
            return orthonormal_basis(schur_vectors[:, :slow_count])
    _, schur_vectors = complex_schur(matrix)
    return orthonormal_basis(schur_vectors[:, :slow_count])
