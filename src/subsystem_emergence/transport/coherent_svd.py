"""Finite-time coherent carrier extraction."""

from __future__ import annotations

import numpy as np

from subsystem_emergence.core.projectors import orth_projector


def coherent_svd(transfer_operator: np.ndarray, rank: int):
    """Return truncated SVD pieces for a transfer operator."""

    left, singular_values, right_h = np.linalg.svd(transfer_operator, full_matrices=False)
    return left[:, :rank], singular_values[:rank], right_h[:rank, :]


def singular_gap(singular_values: np.ndarray, rank: int) -> float:
    """Gap between the retained and discarded singular values."""

    values = np.asarray(singular_values, dtype=float)
    if values.size <= rank:
        return 0.0
    return float(values[rank - 1] - values[rank])


def carrier_projectors(transfer_operator: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Source projector, target projector, and singular values."""

    left, singular_values, right_h = coherent_svd(transfer_operator, rank)
    source = orth_projector(right_h.conj().T)
    target = orth_projector(left)
    return source, target, singular_values
