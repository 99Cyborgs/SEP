"""Leakage observables for autonomous and windowed dynamics."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
from scipy.linalg import expm


def _block_slices(block_sizes: Sequence[int]) -> list[slice]:
    start = 0
    slices: list[slice] = []
    for size in block_sizes:
        stop = start + int(size)
        slices.append(slice(start, stop))
        start = stop
    return slices


def autonomous_leakage(generator: np.ndarray, projector: np.ndarray, time: float) -> float:
    """Compute ||(I-P)e^{tL}P||_2."""

    identity = np.eye(generator.shape[0], dtype=complex)
    propagated = expm(float(time) * generator)
    return float(np.linalg.norm((identity - projector) @ propagated @ projector, 2))


def autonomous_leakage_trajectory(
    generator: np.ndarray, projector: np.ndarray, times: Iterable[float]
) -> list[float]:
    """Leakage trajectory for an autonomous generator."""

    return [autonomous_leakage(generator, projector, time) for time in times]


def reduced_block_leakage(reduced_operator: np.ndarray, block_sizes: Sequence[int], time: float) -> float:
    """Maximal cross-block propagation in the reduced carrier."""

    slices = _block_slices(block_sizes)
    propagated = expm(float(time) * reduced_operator)
    best = 0.0
    for block in slices:
        projector = np.zeros_like(reduced_operator, dtype=complex)
        size = block.stop - block.start
        projector[block, block] = np.eye(size, dtype=complex)
        candidate = np.linalg.norm(
            (np.eye(reduced_operator.shape[0], dtype=complex) - projector)
            @ propagated
            @ projector,
            2,
        )
        best = max(best, float(candidate))
    return best


def reduced_block_leakage_trajectory(
    reduced_operator: np.ndarray, block_sizes: Sequence[int], times: Iterable[float]
) -> list[float]:
    """Leakage trajectory inside the reduced carrier."""

    return [reduced_block_leakage(reduced_operator, block_sizes, time) for time in times]


def transport_leakage(
    operator: np.ndarray, source_projector: np.ndarray, target_projector: np.ndarray
) -> float:
    """Single-window coherent leakage."""

    return float(
        np.linalg.norm(
            (np.eye(operator.shape[0]) - target_projector) @ operator @ source_projector,
            2,
        )
    )


def transport_leakage_trajectory(
    operators: Sequence[np.ndarray], projectors: Sequence[np.ndarray]
) -> list[float]:
    """Cumulative coherent leakage across windows."""

    if len(projectors) != len(operators) + 1:
        raise ValueError("expected len(projectors) = len(operators) + 1")
    product = np.eye(operators[0].shape[0])
    trajectory: list[float] = []
    for index, operator in enumerate(operators):
        product = operator @ product
        trajectory.append(
            float(
                np.linalg.norm(
                    (np.eye(product.shape[0]) - projectors[index + 1]) @ product @ projectors[0],
                    2,
                )
            )
        )
    return trajectory


def cross_subsystem_transfer_rate(reduced_operator: np.ndarray, block_sizes: Sequence[int]) -> float:
    """Operator norm of the off-block residual."""

    residual = np.array(reduced_operator, dtype=complex, copy=True)
    for block in _block_slices(block_sizes):
        residual[block, block] = 0.0
    return float(np.linalg.norm(residual, 2))


def reduced_model_forecast_error(
    generator: np.ndarray,
    basis: np.ndarray,
    reduced_operator: np.ndarray,
    times: Iterable[float],
) -> float:
    """Mean propagated mismatch between full and reduced dynamics."""

    projector = basis @ basis.conj().T
    errors = []
    for time in times:
        full = projector @ expm(float(time) * generator) @ projector
        reduced = basis @ expm(float(time) * reduced_operator) @ basis.conj().T
        errors.append(np.linalg.norm(full - reduced, 2))
    return float(np.mean(errors))


def ensemble_summary(leakage_samples: np.ndarray) -> dict[str, float]:
    """Return sample mean and variance for ensemble leakage observations."""

    sample = np.asarray(leakage_samples, dtype=float)
    return {
        "mean": float(np.mean(sample)),
        "variance": float(np.var(sample, ddof=1)) if sample.size > 1 else 0.0,
    }
