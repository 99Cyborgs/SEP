"""Spectral diagnostics for autonomous linear systems."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from subsystem_emergence.core.horizons import autonomy_horizon, predicted_autonomy_horizon
from subsystem_emergence.core.leakage import (
    autonomous_leakage_trajectory,
    cross_subsystem_transfer_rate,
    reduced_block_leakage_trajectory,
    reduced_model_forecast_error,
)
from subsystem_emergence.core.projectors import orth_projector, orthonormal_basis, projector_deformation
from subsystem_emergence.linear.block_reduce import block_residual, reduced_operator
from subsystem_emergence.linear.pseudospectra import transient_amplification
from subsystem_emergence.linear.schur import extract_slow_subspace_schur


def ordered_eigensystem(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Eigenvalues and eigenvectors ordered by descending real part."""

    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    order = np.argsort(eigenvalues.real)[::-1]
    return eigenvalues[order], eigenvectors[:, order]


def spectral_gap(evals: np.ndarray, slow_count: int) -> float:
    """Real-part spectral gap after ordering by descending real part."""

    values = np.asarray(evals)
    if values.size <= slow_count:
        return 0.0
    order = np.argsort(values.real)[::-1]
    values = values[order]
    return float(values[slow_count - 1].real - values[slow_count].real)


def extract_slow_subspace_eig(matrix: np.ndarray, slow_count: int) -> np.ndarray:
    """Dense eigendecomposition route to the slow carrier."""

    _, eigenvectors = ordered_eigensystem(matrix)
    return orthonormal_basis(eigenvectors[:, :slow_count])


def eigenvector_condition_number(matrix: np.ndarray) -> float:
    """Condition number of the eigenvector matrix."""

    _, eigenvectors = np.linalg.eig(matrix)
    return float(np.linalg.cond(eigenvectors))


def analyze_linear_generator(
    generator: np.ndarray,
    *,
    slow_count: int,
    block_sizes: Sequence[int],
    times: Sequence[float],
    eta: float,
    reference_basis: np.ndarray | None = None,
    identified_generator: np.ndarray | None = None,
    method: str = "eig",
) -> dict[str, object]:
    """End-to-end linear autonomous analysis for T1 and T2 pathways."""

    eigenvalues, _ = ordered_eigensystem(generator)
    extractor = extract_slow_subspace_eig if method == "eig" else extract_slow_subspace_schur
    estimated_basis = extractor(identified_generator if identified_generator is not None else generator, slow_count)
    reference_basis = reference_basis if reference_basis is not None else extract_slow_subspace_eig(generator, slow_count)
    estimated_projector = orth_projector(estimated_basis)
    reference_projector = orth_projector(reference_basis)
    reduced = reduced_operator(generator, estimated_basis)
    autonomous = autonomous_leakage_trajectory(generator, estimated_projector, times)
    reduced_leakage = reduced_block_leakage_trajectory(reduced, block_sizes, times)
    total_leakage = [max(a, b) for a, b in zip(autonomous, reduced_leakage, strict=True)]
    deformation = projector_deformation(estimated_projector, reference_projector)
    rho = block_residual(reduced, block_sizes)
    gamma = transient_amplification(reduced, np.asarray(times, dtype=float))
    observed_horizon = autonomy_horizon(times, total_leakage, eta)
    predicted_horizon = predicted_autonomy_horizon(deformation, rho, eta)
    return {
        "spectral_gap": spectral_gap(eigenvalues, slow_count),
        "projector_deformation": deformation,
        "block_residual_norm": rho,
        "leakage_trajectory": total_leakage,
        "autonomy_horizon": observed_horizon,
        "predicted_autonomy_horizon": predicted_horizon,
        "cross_subsystem_transfer_rate": cross_subsystem_transfer_rate(reduced, block_sizes),
        "reduced_model_forecast_error": reduced_model_forecast_error(generator, estimated_basis, reduced, times),
        "transient_amplification_score": gamma,
        "eigenvector_condition_number": eigenvector_condition_number(generator),
        "projector": estimated_projector,
        "reduced_operator": reduced,
    }
