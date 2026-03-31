"""Projector construction and deformation utilities."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.linalg import subspace_angles


def orthonormal_basis(columns: np.ndarray, rank: int | None = None) -> np.ndarray:
    """Return an orthonormal basis for the supplied columns."""

    q, _ = np.linalg.qr(np.asarray(columns, dtype=complex), mode="reduced")
    if rank is None:
        return q
    return q[:, :rank]


def orth_projector(columns: np.ndarray) -> np.ndarray:
    """Return the orthogonal projector onto the span of the supplied columns."""

    basis = orthonormal_basis(columns)
    return basis @ basis.conj().T


def projector_from_indices(dimension: int, indices: Sequence[int]) -> np.ndarray:
    """Canonical projector onto selected coordinates."""

    projector = np.zeros((dimension, dimension), dtype=complex)
    for index in indices:
        projector[index, index] = 1.0
    return projector


def basis_from_projector(projector: np.ndarray, rank: int) -> np.ndarray:
    """Recover a basis from a projector via its dominant eigenvectors."""

    eigenvalues, eigenvectors = np.linalg.eigh(np.asarray(projector, dtype=complex))
    order = np.argsort(eigenvalues.real)[::-1]
    return orthonormal_basis(eigenvectors[:, order[:rank]])


def projector_deformation(projector_estimate: np.ndarray, projector_reference: np.ndarray) -> float:
    """Return ||P_est - P_ref||_2."""

    return float(np.linalg.norm(projector_estimate - projector_reference, 2))


def coherent_projector_deformation(
    projector_estimate: np.ndarray, projector_reference: np.ndarray
) -> float:
    """Alias for coherent finite-time carriers."""

    return projector_deformation(projector_estimate, projector_reference)


def principal_angle_spectrum(basis_a: np.ndarray, basis_b: np.ndarray) -> list[float]:
    """Principal angles between two subspaces."""

    angles = subspace_angles(orthonormal_basis(basis_a), orthonormal_basis(basis_b))
    return [float(angle) for angle in angles]
