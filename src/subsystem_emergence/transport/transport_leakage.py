"""Leakage measures for products of transfer operators."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from subsystem_emergence.core.horizons import finite_window_autonomy_horizon, predicted_autonomy_horizon
from subsystem_emergence.core.leakage import cross_subsystem_transfer_rate, transport_leakage_trajectory
from subsystem_emergence.core.projectors import coherent_projector_deformation
from subsystem_emergence.linear.block_reduce import reduced_operator
from subsystem_emergence.transport.coherent_svd import carrier_projectors, singular_gap
from subsystem_emergence.transport.window_tracking import track_windows


def product_leakage(operators: Sequence[np.ndarray], source_projector: np.ndarray, target_projector: np.ndarray) -> float:
    """Compute ||(I-Q1) (T_n ... T_1) Q0||_2."""

    product = np.eye(operators[0].shape[0])
    for operator in operators:
        product = operator @ product
    return float(np.linalg.norm((np.eye(product.shape[0]) - target_projector) @ product @ source_projector, 2))


def analyze_windowed_transport(
    operators: Sequence[np.ndarray],
    *,
    coherent_rank: int,
    block_sizes: Sequence[int],
    eta: float,
) -> dict[str, object]:
    """Finite-time transport analysis for T3."""

    source_projectors: list[np.ndarray] = []
    target_projectors: list[np.ndarray] = []
    singular_gaps: list[float] = []
    reduced_couplings: list[float] = []
    singular_values_list: list[list[float]] = []
    window_leakage: list[float] = []
    for operator in operators:
        source_projector, target_projector, singular_values = carrier_projectors(operator, coherent_rank)
        source_projectors.append(source_projector)
        target_projectors.append(target_projector)
        singular_gaps.append(singular_gap(np.linalg.svd(operator, compute_uv=False), coherent_rank))
        window_leakage.append(
            float(
                np.linalg.norm(
                    (np.eye(operator.shape[0]) - target_projector) @ operator @ source_projector,
                    2,
                )
            )
        )
        source_basis = np.linalg.eigh(source_projector)[1][:, -coherent_rank:]
        reduced = reduced_operator(operator, source_basis)
        reduced_couplings.append(cross_subsystem_transfer_rate(reduced, block_sizes))
        singular_values_list.append([float(value) for value in singular_values])
    all_projectors = [source_projectors[0], *target_projectors]
    leakage = transport_leakage_trajectory(list(operators), all_projectors)
    window_indices = list(range(1, len(leakage) + 1))
    deformations = [
        coherent_projector_deformation(source_projectors[index + 1], target_projectors[index])
        for index in range(len(source_projectors) - 1)
    ]
    average_deformation = float(np.mean(deformations)) if deformations else 0.0
    max_deformation = float(np.max(deformations)) if deformations else 0.0
    average_rho = float(np.mean(reduced_couplings)) if reduced_couplings else 0.0
    source_tracking = track_windows(source_projectors)
    target_tracking = track_windows(target_projectors)
    carrier_tracking = {
        "mean_deformation": average_deformation,
        "max_deformation": max_deformation,
        "trajectory": deformations,
    }
    return {
        "singular_gap": float(np.mean(singular_gaps)) if singular_gaps else 0.0,
        "coherent_projector_deformation": average_deformation,
        "block_residual_norm": average_rho,
        "leakage_trajectory": leakage,
        "autonomy_horizon": finite_window_autonomy_horizon(window_indices, leakage, eta),
        "predicted_autonomy_horizon": predicted_autonomy_horizon(average_deformation, average_rho, eta),
        "cross_subsystem_transfer_rate": average_rho,
        "singular_values": singular_values_list,
        "projectors": all_projectors,
        "transport_diagnostics": {
            "window_leakage_trajectory": window_leakage,
            "source_tracking": source_tracking,
            "target_tracking": target_tracking,
            "carrier_tracking": carrier_tracking,
            "singular_gap_trajectory": singular_gaps,
            "cumulative_peak_leakage": float(np.max(leakage)) if leakage else 0.0,
            "window_peak_leakage": float(np.max(window_leakage)) if window_leakage else 0.0,
        },
    }
