"""Reduced carrier block decomposition helpers."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def block_slices(block_sizes: Sequence[int]) -> list[slice]:
    """Convert block sizes into slicing objects."""

    start = 0
    slices: list[slice] = []
    for size in block_sizes:
        stop = start + int(size)
        slices.append(slice(start, stop))
        start = stop
    return slices


def reduced_operator(generator: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Project an operator into the supplied carrier basis."""

    return basis.conj().T @ generator @ basis


def block_diagonal_part(matrix: np.ndarray, block_sizes: Sequence[int]) -> np.ndarray:
    """Extract the block diagonal defined by block_sizes."""

    diagonal = np.zeros_like(matrix, dtype=complex)
    for block in block_slices(block_sizes):
        diagonal[block, block] = matrix[block, block]
    return diagonal


def block_residual(matrix: np.ndarray, block_sizes: Sequence[int]) -> float:
    """Return ||R|| where D is the block-diagonal extraction of matrix."""

    residual = matrix - block_diagonal_part(matrix, block_sizes)
    return float(np.linalg.norm(residual, 2))
