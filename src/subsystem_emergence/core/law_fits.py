"""Deterministic least-squares fitting for the L1/L2/L3 leakage laws.

The fitting path is intentionally lightweight and reproducible so benchmark
artifacts can be regenerated bit-for-bit from the same samples.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np


@dataclass(slots=True)
class FitResult:
    """Structured report for a law fit."""

    law: str
    feature_names: list[str]
    coefficients: dict[str, float]
    train_rmse: float
    test_rmse: float
    residual_mean: float
    residual_std: float
    selected: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "law": self.law,
            "feature_names": self.feature_names,
            "coefficients": self.coefficients,
            "train_rmse": self.train_rmse,
            "test_rmse": self.test_rmse,
            "residual_mean": self.residual_mean,
            "residual_std": self.residual_std,
            "selected": self.selected,
            "notes": self.notes,
        }


@dataclass(slots=True)
class LawSelectionSummary:
    """Ranking summary across candidate leakage laws."""

    best_law: str
    ranked_laws: list[str]
    improvement_over_l1: float

    def to_dict(self) -> dict[str, object]:
        return {
            "best_law": self.best_law,
            "ranked_laws": self.ranked_laws,
            "improvement_over_l1": self.improvement_over_l1,
        }


def _split_indices(size: int) -> tuple[np.ndarray, np.ndarray]:
    """Return deterministic train/test indices for small benchmark sample sets."""

    if size <= 3:
        # Tiny benchmark sweeps do not support a meaningful hold-out split; reuse
        # the full sample on both sides rather than producing empty design blocks.
        indices = np.arange(size)
        return indices, indices
    rng = np.random.default_rng(0)
    indices = np.arange(size)
    rng.shuffle(indices)
    test_size = max(1, int(round(size / 3)))
    test = np.sort(indices[:test_size])
    train = np.sort(indices[test_size:])
    return train, test


def _rmse(predicted: np.ndarray, observed: np.ndarray) -> float:
    return float(np.sqrt(np.mean((predicted - observed) ** 2)))


def _fit_model(
    law: str,
    feature_names: list[str],
    design: np.ndarray,
    leakage: np.ndarray,
) -> FitResult:
    """Fit one candidate law and report held-out and residual diagnostics."""

    train_index, test_index = _split_indices(design.shape[0])
    train_design = design[train_index]
    train_leakage = leakage[train_index]
    coefficients, *_ = np.linalg.lstsq(train_design, train_leakage, rcond=None)
    train_pred = train_design @ coefficients
    test_pred = design[test_index] @ coefficients
    residuals = leakage - design @ coefficients
    return FitResult(
        law=law,
        feature_names=feature_names,
        coefficients={
            name: float(value) for name, value in zip(feature_names, coefficients, strict=True)
        },
        train_rmse=_rmse(train_pred, train_leakage),
        test_rmse=_rmse(test_pred, leakage[test_index]),
        residual_mean=float(np.mean(residuals)),
        residual_std=float(np.std(residuals)),
    )


def _as_array(values: Iterable[float]) -> np.ndarray:
    array = np.asarray(list(values), dtype=float)
    if array.ndim != 1:
        raise ValueError("expected a one-dimensional array")
    return array


def fit_l1(epsilon_s: Iterable[float], rho_tau: Iterable[float], leakage: Iterable[float]) -> FitResult:
    """Fit the pure affine law L1."""

    epsilon_s_array = _as_array(epsilon_s)
    rho_tau_array = _as_array(rho_tau)
    leakage_array = _as_array(leakage)
    design = np.column_stack([epsilon_s_array, rho_tau_array])
    return _fit_model("L1", ["epsilon_s", "rho_tau"], design, leakage_array)


def fit_l2(epsilon_s: Iterable[float], rho_tau: Iterable[float], leakage: Iterable[float]) -> FitResult:
    """Fit the affine-plus-quadratic law L2."""

    epsilon_s_array = _as_array(epsilon_s)
    rho_tau_array = _as_array(rho_tau)
    leakage_array = _as_array(leakage)
    design = np.column_stack([epsilon_s_array, rho_tau_array, rho_tau_array**2])
    return _fit_model(
        "L2",
        ["epsilon_s", "rho_tau", "rho_tau_sq"],
        design,
        leakage_array,
    )


def fit_l3(
    epsilon_s: Iterable[float],
    rho_tau: Iterable[float],
    leakage: Iterable[float],
    gamma: Iterable[float],
) -> FitResult:
    """Fit the nonnormality-corrected law L3."""

    epsilon_s_array = _as_array(epsilon_s)
    rho_tau_array = _as_array(rho_tau)
    gamma_array = _as_array(gamma)
    leakage_array = _as_array(leakage)
    corrected = gamma_array * rho_tau_array
    design = np.column_stack([epsilon_s_array, corrected, corrected**2])
    return _fit_model(
        "L3",
        ["epsilon_s", "gamma_rho_tau", "gamma_rho_tau_sq"],
        design,
        leakage_array,
    )


def fit_all_laws(
    epsilon_s: Iterable[float],
    rho_tau: Iterable[float],
    leakage: Iterable[float],
    gamma: Iterable[float] | None = None,
) -> dict[str, FitResult]:
    """Fit all supported laws under a shared sample set and selection rule.

    When `gamma` is omitted, L3 falls back to `gamma = 1`, making it comparable
    to the other laws without requiring branch-specific transient diagnostics.
    """

    leakage_array = _as_array(leakage)
    gamma_array = _as_array(gamma if gamma is not None else np.ones_like(leakage_array))
    results = {
        "L1": fit_l1(epsilon_s, rho_tau, leakage_array),
        "L2": fit_l2(epsilon_s, rho_tau, leakage_array),
        "L3": fit_l3(epsilon_s, rho_tau, leakage_array, gamma_array),
    }
    summary = law_selection_summary(results)
    results[summary.best_law].selected = True
    return results


def law_selection_summary(results: dict[str, FitResult]) -> LawSelectionSummary:
    """Rank candidate laws by held-out error, then in-sample error as a tiebreak."""

    ranked = sorted(results.values(), key=lambda result: (result.test_rmse, result.train_rmse))
    l1_rmse = results["L1"].test_rmse
    best = ranked[0]
    return LawSelectionSummary(
        best_law=best.law,
        ranked_laws=[result.law for result in ranked],
        improvement_over_l1=float(l1_rmse - best.test_rmse),
    )
