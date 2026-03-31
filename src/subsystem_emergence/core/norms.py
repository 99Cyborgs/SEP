"""Norm utilities and norm registry."""

from __future__ import annotations

from typing import Callable

import numpy as np


def operator_2_norm(array: np.ndarray) -> float:
    """Operator 2-norm for vectors or matrices."""

    return float(np.linalg.norm(array, 2))


def frobenius_norm(array: np.ndarray) -> float:
    """Frobenius norm for matrices."""

    return float(np.linalg.norm(array, "fro"))


def vector_l2_norm(array: np.ndarray) -> float:
    """Euclidean norm for vectors."""

    return float(np.linalg.norm(array.ravel(), 2))


def l1_norm(array: np.ndarray) -> float:
    """Elementwise l1 norm."""

    return float(np.linalg.norm(array.ravel(), 1))


def total_variation_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Total variation distance between probability vectors."""

    return 0.5 * float(np.linalg.norm(np.asarray(p) - np.asarray(q), 1))


def weighted_l2_norm(vector: np.ndarray, weights: np.ndarray) -> float:
    """Weighted Euclidean norm."""

    vector_array = np.asarray(vector, dtype=float)
    weights_array = np.asarray(weights, dtype=float)
    return float(np.sqrt(np.sum(weights_array * vector_array**2)))


NORM_REGISTRY: dict[str, Callable[..., float]] = {
    "operator_2": operator_2_norm,
    "frobenius": frobenius_norm,
    "vector_l2": vector_l2_norm,
    "l1": l1_norm,
}


def evaluate_norm(name: str, array: np.ndarray, *extra_args: np.ndarray) -> float:
    """Evaluate a registered norm by name."""

    if name == "weighted_l2":
        if len(extra_args) != 1:
            raise ValueError("weighted_l2 requires a weights array")
        return weighted_l2_norm(array, extra_args[0])
    try:
        return NORM_REGISTRY[name](array)
    except KeyError as error:
        raise KeyError(f"unknown norm convention: {name}") from error
