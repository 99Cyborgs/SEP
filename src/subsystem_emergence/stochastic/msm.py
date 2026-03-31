"""Markov state model utilities."""

from __future__ import annotations

import numpy as np


def cluster_membership_from_slow_mode(transition_matrix: np.ndarray) -> list[int]:
    """Two-cluster assignment from the dominant nontrivial slow mode."""

    eigenvalues, eigenvectors = np.linalg.eig(transition_matrix.T)
    order = np.argsort(np.abs(eigenvalues))[::-1]
    slow_vector = eigenvectors[:, order[1]].real
    median = float(np.median(slow_vector))
    return [int(value >= median) for value in slow_vector]


def metastability_score(transition_matrix: np.ndarray, membership: list[int]) -> float:
    """Mean within-cluster retention probability."""

    matrix = np.asarray(transition_matrix, dtype=float)
    scores = []
    for state, cluster in enumerate(membership):
        peers = [index for index, label in enumerate(membership) if label == cluster]
        scores.append(float(np.sum(matrix[state, peers])))
    return float(np.mean(scores))


def build_msm(transition_matrix: np.ndarray) -> dict[str, object]:
    """Construct a minimal Markov state model summary."""

    membership = cluster_membership_from_slow_mode(transition_matrix)
    return {
        "membership": membership,
        "metastability_score": metastability_score(transition_matrix, membership),
    }
