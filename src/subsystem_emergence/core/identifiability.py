"""Identifiability and artifact-challenging diagnostics."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .projectors import projector_deformation


def random_orthogonal(dimension: int, seed: int) -> np.ndarray:
    """Sample a deterministic orthogonal matrix."""

    rng = np.random.default_rng(seed)
    matrix = rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(matrix)
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return q * signs


def coordinate_sensitivity(
    matrix: np.ndarray,
    analyzer: Callable[[np.ndarray], dict[str, object]],
    trials: int = 4,
    seed: int = 0,
) -> dict[str, float]:
    """Measure coordinate robustness under orthogonal transforms."""

    baseline = analyzer(matrix)
    numeric_keys = [
        key
        for key in ("spectral_gap", "block_residual_norm", "autonomy_horizon", "singular_gap")
        if key in baseline and baseline[key] is not None
    ]
    if not numeric_keys:
        return {"max_relative_change": 0.0, "mean_relative_change": 0.0, "projector_back_error": 0.0}
    relative_changes: list[float] = []
    projector_errors: list[float] = []
    baseline_projector = baseline.get("projector")
    for trial in range(trials):
        orthogonal = random_orthogonal(matrix.shape[0], seed + trial)
        transformed = orthogonal.T @ matrix @ orthogonal
        transformed_result = analyzer(transformed)
        for key in numeric_keys:
            baseline_value = float(baseline[key])
            transformed_value = float(transformed_result[key])
            scale = abs(baseline_value) + 1.0e-12
            relative_changes.append(abs(transformed_value - baseline_value) / scale)
        transformed_projector = transformed_result.get("projector")
        if baseline_projector is not None and transformed_projector is not None:
            pulled_back = orthogonal @ np.asarray(transformed_projector) @ orthogonal.T
            projector_errors.append(projector_deformation(pulled_back, np.asarray(baseline_projector)))
    return {
        "max_relative_change": float(max(relative_changes) if relative_changes else 0.0),
        "mean_relative_change": float(np.mean(relative_changes) if relative_changes else 0.0),
        "projector_back_error": float(np.mean(projector_errors) if projector_errors else 0.0),
    }


def numerical_refinement_metric(values: list[float]) -> dict[str, float]:
    """Relative spread across refinement levels."""

    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return {"max_relative_span": 0.0, "mean": 0.0}
    scale = abs(np.mean(array)) + 1.0e-12
    return {
        "max_relative_span": float((np.max(array) - np.min(array)) / scale),
        "mean": float(np.mean(array)),
    }


def coarse_graining_bias(matrix: np.ndarray, groups: list[list[int]]) -> dict[str, float]:
    """Compare a fine transition matrix against a simple coarse-grained reduction."""

    coarse = np.zeros((len(groups), len(groups)))
    for i, source_group in enumerate(groups):
        for j, target_group in enumerate(groups):
            submatrix = matrix[np.ix_(source_group, target_group)]
            coarse[i, j] = float(np.mean(np.sum(submatrix, axis=1)))
    row_sum_error = float(np.max(np.abs(np.sum(coarse, axis=1) - 1.0)))
    fine_singular = np.linalg.svd(matrix, compute_uv=False)
    coarse_singular = np.linalg.svd(coarse, compute_uv=False)
    fine_gap = float(fine_singular[0] - fine_singular[1]) if fine_singular.size > 1 else 0.0
    coarse_gap = float(coarse_singular[0] - coarse_singular[1]) if coarse_singular.size > 1 else 0.0
    return {
        "row_stochastic_error": row_sum_error,
        "singular_gap_change": coarse_gap - fine_gap,
        "coarse_state_count": float(len(groups)),
    }


def transient_coincidence_score(times: list[float], leakage: list[float]) -> float:
    """Score sensitivity of the law fit to dropping the earliest transient points."""

    if len(times) < 4:
        return 0.0
    early = np.asarray(leakage[: max(2, len(leakage) // 3)], dtype=float)
    late = np.asarray(leakage[max(1, len(leakage) // 3) :], dtype=float)
    return float(abs(np.mean(early) - np.mean(late)) / (np.mean(late) + 1.0e-12))


def post_hoc_projection_score(
    operator: np.ndarray, candidate_projector: np.ndarray, held_out_projector: np.ndarray
) -> float:
    """Compare candidate and held-out projectors on the same operator."""

    leakage_candidate = np.linalg.norm((np.eye(operator.shape[0]) - candidate_projector) @ operator @ candidate_projector, 2)
    leakage_held_out = np.linalg.norm((np.eye(operator.shape[0]) - held_out_projector) @ operator @ held_out_projector, 2)
    return float(abs(leakage_candidate - leakage_held_out) / (leakage_held_out + 1.0e-12))
