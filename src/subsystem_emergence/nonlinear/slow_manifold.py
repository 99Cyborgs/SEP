"""Slow-manifold estimation and local leakage diagnostics."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from subsystem_emergence.core.projectors import orth_projector, projector_deformation
from subsystem_emergence.linear.spectral import extract_slow_subspace_eig, spectral_gap


def estimate_slow_manifold(states: np.ndarray, slow_dim: int) -> np.ndarray:
    """Return the slow coordinates from a trajectory sample."""

    return np.asarray(states, dtype=float)[:, :slow_dim]


def instantaneous_slow_projectors(jacobians: Sequence[np.ndarray], slow_dim: int) -> list[np.ndarray]:
    """Carrier projectors inferred from local Jacobians."""

    return [orth_projector(extract_slow_subspace_eig(jacobian, slow_dim)) for jacobian in jacobians]


def state_leakage_trajectory(states: np.ndarray, projectors: Sequence[np.ndarray]) -> list[float]:
    """Normalized leakage of states out of the instantaneous slow carrier."""

    trajectory = []
    for state, projector in zip(np.asarray(states), projectors, strict=True):
        lifted = projector @ state
        leakage = state - lifted.real
        trajectory.append(float(np.linalg.norm(leakage) / (np.linalg.norm(state) + 1.0e-12)))
    return trajectory


def local_spectral_gaps(jacobians: Sequence[np.ndarray], slow_dim: int) -> list[float]:
    """Local real-part gap profile along a trajectory."""

    return [spectral_gap(np.linalg.eigvals(jacobian), slow_dim) for jacobian in jacobians]


def local_projector_tracking(projectors: Sequence[np.ndarray]) -> dict[str, object]:
    """Window-to-window carrier tracking diagnostics for local nonlinear runs."""

    if len(projectors) < 2:
        return {
            "adjacent_mean_deformation": 0.0,
            "adjacent_max_deformation": 0.0,
            "adjacent_deformation_trajectory": [],
            "anchor_mean_deformation": 0.0,
            "anchor_max_deformation": 0.0,
            "anchor_deformation_trajectory": [],
        }
    adjacent = [
        projector_deformation(projectors[index + 1], projectors[index])
        for index in range(len(projectors) - 1)
    ]
    anchor = [projector_deformation(projector, projectors[0]) for projector in projectors]
    return {
        "adjacent_mean_deformation": float(np.mean(adjacent)),
        "adjacent_max_deformation": float(np.max(adjacent)),
        "adjacent_deformation_trajectory": adjacent,
        "anchor_mean_deformation": float(np.mean(anchor)),
        "anchor_max_deformation": float(np.max(anchor)),
        "anchor_deformation_trajectory": anchor,
    }
