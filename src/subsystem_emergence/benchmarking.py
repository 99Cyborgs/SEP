"""Benchmark registry access, concrete generators, and reference runs."""

from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
from time import perf_counter

import numpy as np

from subsystem_emergence.application.acceptance import evaluate_application_acceptance
from subsystem_emergence.application.mobility import (
    build_windowed_mobility_operators,
    mobility_evaluation_cases,
    mobility_parameter_set,
)
from subsystem_emergence.application.clickstream import (
    build_windowed_clickstream_operators,
    clickstream_parameter_set,
)
from subsystem_emergence.application.support import (
    build_windowed_support_operators,
    support_parameter_set,
)
from subsystem_emergence.application.workflow import (
    build_windowed_workflow_operators,
    workflow_parameter_set,
)
from subsystem_emergence.core.failures import (
    DEFAULT_FAILURE_TAXONOMY_THRESHOLDS,
    archive_failure_reports,
    evaluate_failure_signatures,
)
from subsystem_emergence.core.horizons import horizon_ratio
from subsystem_emergence.core.identifiability import (
    coarse_graining_bias,
    coordinate_sensitivity,
    numerical_refinement_metric,
    transient_coincidence_score,
)
from subsystem_emergence.delay import analyze_delay_system, delay_refinement_diagnostics
from subsystem_emergence.core.law_fits import fit_all_laws, law_selection_summary
from subsystem_emergence.core.observables import empty_observables
from subsystem_emergence.io.ledgers import current_code_hash, repo_relative_path, repository_root, write_ledger
from subsystem_emergence.io.registry import benchmark_definitions
from subsystem_emergence.linear.pseudospectra import pseudospectral_proxy, semigroup_growth_profile
from subsystem_emergence.linear.spectral import analyze_linear_generator
from subsystem_emergence.nonlinear.continuation import continue_family
from subsystem_emergence.nonlinear.curvature_corrections import curvature_indicator
from subsystem_emergence.nonlinear.local_linearization import integrate_trajectory, jacobian_sequence
from subsystem_emergence.nonlinear.slow_manifold import (
    estimate_slow_manifold,
    instantaneous_slow_projectors,
    local_projector_tracking,
    local_spectral_gaps,
    state_leakage_trajectory,
)
from subsystem_emergence.stochastic.bootstrap import bootstrap_ci
from subsystem_emergence.stochastic.monte_carlo import ensemble_leakage_trajectory, run_mc
from subsystem_emergence.stochastic.msm import build_msm
from subsystem_emergence.stochastic.propagators import (
    analyze_stochastic_transition,
    estimate_propagator,
)
from subsystem_emergence.transport.transport_leakage import analyze_windowed_transport
from subsystem_emergence.transport.ulam import build_windowed_transport_flow


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _rotation_mix(dimension: int, seed: int) -> np.ndarray:
    matrix = _rng(seed).normal(size=(dimension, dimension))
    q, _ = np.linalg.qr(matrix)
    return q


def _invoke_runner(runner, seed: int, parameter_id: str) -> tuple[dict, dict]:
    """Call a benchmark runner, passing parameter_id only when supported."""

    if "parameter_id" in inspect.signature(runner).parameters:
        return runner(seed, parameter_id=parameter_id)
    return runner(seed)


def _base_record(
    benchmark_id: str,
    branch: str,
    theorem_tier: str,
    parameter_id: str,
    seed: int,
    parameters: dict,
) -> dict:
    return {
        "benchmark_id": benchmark_id,
        "branch": branch,
        "theorem_tier": theorem_tier,
        "parameter_id": parameter_id,
        "seed": seed,
        "parameters": parameters,
        "metadata": {
            "code_hash": current_code_hash(),
            "solver": "",
            "runtime_seconds": 0.0,
            "source_of_truth": {
                "embedded_zip_found": False,
                "reconciliation_note": "No embedded zip archive was found; the live scaffold was reconciled in place.",
            },
        },
        "observables": empty_observables(),
        "law_fits": {},
        "law_selection_summary": {},
        "gate_outcomes": {},
        "failure_labels": [],
        "figure_references": [],
        "notes": [],
    }


def _fit_and_finalize(record: dict, analysis: dict, root: Path) -> dict:
    gamma = np.asarray(
        analysis.pop(
            "fit_gamma",
            np.ones(len(analysis["leakage_trajectory"])),
        ),
        dtype=float,
    )
    notes = analysis.pop("notes", [])
    times = np.asarray(record["parameters"].get("times") or record["parameters"].get("windows"), dtype=float)
    leakage = np.asarray(analysis["leakage_trajectory"], dtype=float)
    epsilon_value = float(
        analysis.get("projector_deformation")
        or analysis.get("coherent_projector_deformation")
        or 0.0
    )
    epsilon = np.full_like(leakage, epsilon_value)
    rho = np.full_like(leakage, float(analysis["block_residual_norm"])) * np.maximum(times, 1.0e-12)
    fits = fit_all_laws(epsilon, rho, leakage, gamma=gamma)
    selection = law_selection_summary(fits)
    record["observables"].update(
        {
            key: value
            for key, value in analysis.items()
            if key
            not in {
                "projector",
                "reduced_operator",
                "projectors",
                "history_operator",
                "history_basis",
                "terminal_state_projector",
            }
        }
    )
    record["observables"]["affine_law_regression_coefficients"] = {
        key: result.coefficients for key, result in fits.items()
    }
    record["observables"]["transient_coincidence_score"] = transient_coincidence_score(
        times.tolist(),
        leakage.tolist(),
    )
    record["law_fits"] = {key: value.to_dict() for key, value in fits.items()}
    record["law_selection_summary"] = selection.to_dict()
    record["notes"].extend(notes)
    reports = evaluate_failure_signatures(record, dict(DEFAULT_FAILURE_TAXONOMY_THRESHOLDS))
    record["failure_labels"] = [report.label for report in reports if report.triggered]
    archive_failure_reports(root, record["branch"], record, reports)
    return record


def _persist_record(
    benchmark_id: str,
    branch: str,
    theorem_tier: str,
    seed: int,
    parameter_id: str,
    parameters: dict,
    analysis: dict,
    root: Path,
    started: float,
) -> dict:
    """Persist a completed benchmark analysis through the shared ledger path."""

    record = _base_record(benchmark_id, branch, theorem_tier, parameter_id, seed, parameters)
    record = _fit_and_finalize(record, analysis, root)
    record["metadata"]["runtime_seconds"] = perf_counter() - started
    record["metadata"]["solver"] = "scipy/numpy reference routines"
    json_path, md_path = write_ledger(root, record)
    record["metadata"]["ledger_json"] = repo_relative_path(json_path, root)
    record["metadata"]["ledger_markdown"] = repo_relative_path(md_path, root)
    return record


def _linear_two_block(seed: int) -> tuple[dict, dict]:
    params = {
        "gap": 1.05,
        "rho": 0.06,
        "perturbation": 0.005,
        "times": np.linspace(0.0, 8.0, 25).tolist(),
        "eta": 0.35,
        "slow_count": 4,
        "block_sizes": [2, 2],
    }
    slow = np.diag([-0.08, -0.11, -0.13, -0.15])
    fast = np.diag([-1.2, -1.4, -1.7, -1.9])
    generator = np.block([[slow, np.zeros((4, 4))], [np.zeros((4, 4)), fast]])
    generator[0, 2] = params["rho"]
    generator[1, 3] = -0.5 * params["rho"]
    generator[2, 0] = -0.3 * params["rho"]
    generator[3, 1] = 0.25 * params["rho"]
    mix = _rotation_mix(generator.shape[0], seed)
    generator = mix.T @ generator @ mix
    identified = generator + params["perturbation"] * _rng(seed + 13).normal(size=generator.shape)
    reference_basis = None
    analysis = analyze_linear_generator(
        generator,
        slow_count=params["slow_count"],
        block_sizes=params["block_sizes"],
        times=params["times"],
        eta=params["eta"],
        reference_basis=reference_basis,
        identified_generator=identified,
        method="eig",
    )

    def analyzer(matrix: np.ndarray) -> dict[str, object]:
        result = analyze_linear_generator(
            matrix,
            slow_count=params["slow_count"],
            block_sizes=params["block_sizes"],
            times=params["times"],
            eta=params["eta"],
        )
        return {
            "spectral_gap": result["spectral_gap"],
            "block_residual_norm": result["block_residual_norm"],
            "autonomy_horizon": result["autonomy_horizon"],
            "projector": result["projector"],
        }

    analysis["coordinate_sensitivity_metrics"] = coordinate_sensitivity(generator, analyzer)
    refined = analyze_linear_generator(
        generator,
        slow_count=params["slow_count"],
        block_sizes=params["block_sizes"],
        times=np.linspace(0.0, 8.0, 49).tolist(),
        eta=params["eta"],
        reference_basis=reference_basis,
        identified_generator=identified,
        method="schur",
    )
    analysis["numerical_refinement_metrics"] = numerical_refinement_metric(
        [analysis["autonomy_horizon"], refined["autonomy_horizon"]]
    )
    analysis["transportability_metrics"] = {
        "horizon_ratio": horizon_ratio(
            float(analysis["autonomy_horizon"]),
            float(analysis["predicted_autonomy_horizon"]),
        )
    }
    return params, analysis


def _random_gap_ensemble(seed: int) -> tuple[dict, dict]:
    params = {
        "ensemble_size": 8,
        "times": np.linspace(0.0, 5.0, 18).tolist(),
        "eta": 0.4,
        "slow_count": 2,
        "block_sizes": [1, 1],
    }
    rng = _rng(seed)
    per_member = []
    gamma_values = []
    proxy_values = []
    for index in range(params["ensemble_size"]):
        gap = 0.05 + 0.25 * index / params["ensemble_size"]
        base = np.diag([-0.1, -0.1 - gap, -1.0, -1.2])
        if index % 2 == 0:
            matrix = base + 0.02 * rng.normal(size=(4, 4))
        else:
            matrix = base + np.array(
                [[0.0, 2.0, 0.0, 0.0], [0.0, 0.0, 0.12, 0.0], [0.0, 0.0, 0.0, 0.3], [0.0, 0.0, 0.0, 0.0]]
            )
        result = analyze_linear_generator(
            matrix,
            slow_count=params["slow_count"],
            block_sizes=params["block_sizes"],
            times=params["times"],
            eta=params["eta"],
        )
        per_member.append(result)
        gamma_values.append(float(result["transient_amplification_score"]))
        proxy_values.append(float(pseudospectral_proxy(result["reduced_operator"])))
    mean_leakage = np.mean(
        np.asarray([member["leakage_trajectory"] for member in per_member], dtype=float),
        axis=0,
    )
    analysis = {
        "spectral_gap": float(np.mean([member["spectral_gap"] for member in per_member])),
        "projector_deformation": float(np.mean([member["projector_deformation"] for member in per_member])),
        "block_residual_norm": float(np.mean([member["block_residual_norm"] for member in per_member])),
        "leakage_trajectory": mean_leakage.tolist(),
        "autonomy_horizon": float(np.mean([member["autonomy_horizon"] for member in per_member])),
        "predicted_autonomy_horizon": float(np.mean([member["predicted_autonomy_horizon"] for member in per_member])),
        "cross_subsystem_transfer_rate": float(np.mean([member["cross_subsystem_transfer_rate"] for member in per_member])),
        "reduced_model_forecast_error": float(np.mean([member["reduced_model_forecast_error"] for member in per_member])),
        "transient_amplification_score": float(np.mean([member["transient_amplification_score"] for member in per_member])),
        "pseudospectral_proxy": float(np.mean(proxy_values)),
        "coordinate_sensitivity_metrics": {"max_relative_change": 0.0, "mean_relative_change": 0.0, "projector_back_error": 0.0},
        "numerical_refinement_metrics": {"max_relative_span": 0.0, "mean": float(np.mean(mean_leakage))},
        "transportability_metrics": {
            "ensemble_size": float(params["ensemble_size"]),
            "pseudospectral_proxy_mean": float(np.mean(proxy_values)),
            "pseudospectral_proxy_max": float(np.max(proxy_values)),
        },
        "fit_gamma": np.full(len(params["times"]), float(np.mean(gamma_values))),
    }
    return params, analysis


def _nearly_decomposable_chain(seed: int) -> tuple[dict, dict]:
    params = {
        "times": np.linspace(0.0, 18.0, 19).tolist(),
        "eta": 0.3,
        "slow_count": 2,
        "block_sizes": [1, 1],
    }
    intra = 0.9
    inter = 0.04 + 0.005 * seed
    transition = np.array(
        [
            [intra, inter, 1.0 - intra - inter, 0.0],
            [inter, intra, 0.0, 1.0 - intra - inter],
            [1.0 - intra - inter, 0.0, intra, inter],
            [0.0, 1.0 - intra - inter, inter, intra],
        ]
    )
    generator = transition - np.eye(4)
    analysis = analyze_linear_generator(
        generator,
        slow_count=params["slow_count"],
        block_sizes=params["block_sizes"],
        times=params["times"],
        eta=params["eta"],
    )
    analysis["coordinate_sensitivity_metrics"] = {"max_relative_change": 0.0, "mean_relative_change": 0.0, "projector_back_error": 0.0}
    analysis["numerical_refinement_metrics"] = numerical_refinement_metric([analysis["autonomy_horizon"]])
    analysis["transportability_metrics"] = coarse_graining_bias(transition, [[0, 1], [2, 3]])
    return params, analysis


def _nonnormal_shear(seed: int) -> tuple[dict, dict]:
    params = {
        "times": np.linspace(0.0, 6.0, 25).tolist(),
        "eta": 0.45,
        "slow_count": 2,
        "block_sizes": [1, 1],
    }
    matrix = np.array(
        [[-0.08, 3.2, 0.08, 0.0], [0.0, -0.08, 0.0, 0.06], [0.0, 0.0, -1.1, 0.4], [0.0, 0.0, 0.0, -1.3]]
    )
    analysis = analyze_linear_generator(
        matrix,
        slow_count=params["slow_count"],
        block_sizes=params["block_sizes"],
        times=params["times"],
        eta=params["eta"],
    )
    analysis["coordinate_sensitivity_metrics"] = coordinate_sensitivity(
        matrix,
        lambda candidate: analyze_linear_generator(
            candidate,
            slow_count=params["slow_count"],
            block_sizes=params["block_sizes"],
            times=params["times"],
            eta=params["eta"],
        ),
    )
    refined = analyze_linear_generator(
        matrix,
        slow_count=params["slow_count"],
        block_sizes=params["block_sizes"],
        times=np.linspace(0.0, 6.0, 49).tolist(),
        eta=params["eta"],
    )
    refinement_gap = numerical_refinement_metric(
        [float(analysis["spectral_gap"]), float(refined["spectral_gap"])]
    )
    refinement_residual = numerical_refinement_metric(
        [float(analysis["block_residual_norm"]), float(refined["block_residual_norm"])]
    )
    refinement_transient = numerical_refinement_metric(
        [float(analysis["transient_amplification_score"]), float(refined["transient_amplification_score"])]
    )
    analysis["numerical_refinement_metrics"] = {
        "max_relative_span": float(
            max(
                refinement_gap["max_relative_span"],
                refinement_residual["max_relative_span"],
                refinement_transient["max_relative_span"],
            )
        ),
        "mean": float(
            np.mean(
                [
                    refinement_gap["mean"],
                    refinement_residual["mean"],
                    refinement_transient["mean"],
                ]
            )
        ),
        "refined_time_count": 49.0,
        "refinement_axis": "time_grid_density",
        "spectral_gap_relative_span": refinement_gap["max_relative_span"],
        "block_residual_relative_span": refinement_residual["max_relative_span"],
        "transient_relative_span": refinement_transient["max_relative_span"],
    }
    analysis["transportability_metrics"] = {
        "horizon_ratio": horizon_ratio(
            float(analysis["autonomy_horizon"]),
            float(analysis["predicted_autonomy_horizon"]),
        )
    }
    analysis["pseudospectral_proxy"] = float(pseudospectral_proxy(analysis["reduced_operator"]))
    analysis["transportability_metrics"]["pseudospectral_proxy"] = float(analysis["pseudospectral_proxy"])
    analysis["notes"] = [
        "Nonnormal refinement compares continuous observables across a denser time grid; thresholded autonomy horizon is excluded because near-zero horizon changes discretely under resampling.",
    ]
    return params, analysis


def _delay_coupled_pair(seed: int) -> tuple[dict, dict]:
    params = {
        "times": np.linspace(0.0, 4.8, 13).tolist(),
        "eta": 0.69,
        "slow_count": 2,
        "block_sizes": [1, 1],
        "delay": 0.4,
        "history_kind": "nodal_piecewise_linear",
        "history_grid_size": 6,
        "step_size": 0.0125,
        "history_grid_ladder": [6, 8, 10],
        "step_size_ladder": [0.0125, 0.00625, 0.003125],
        "self_decay": 0.9,
        "shear": 2.2,
        "cross_coupling": 0.15,
        "delay_feedback": 1.3,
        "delay_cross_feedback": 0.25,
    }
    a0 = np.array(
        [
            [-params["self_decay"], params["shear"]],
            [0.0, -(params["self_decay"] + params["cross_coupling"])],
        ]
    )
    a_delay = np.array(
        [
            [params["delay_feedback"], 0.0],
            [params["delay_cross_feedback"], params["delay_feedback"] - 0.08],
        ]
    )
    analysis = analyze_delay_system(
        a0,
        a_delay,
        delay=params["delay"],
        history_grid_size=params["history_grid_size"],
        step_size=params["step_size"],
        slow_count=params["slow_count"],
        block_sizes=params["block_sizes"],
        times=params["times"],
        eta=params["eta"],
    )
    refinement = delay_refinement_diagnostics(
        a0,
        a_delay,
        delay=params["delay"],
        history_grid_sizes=params["history_grid_ladder"],
        step_sizes=params["step_size_ladder"],
        slow_count=params["slow_count"],
        block_sizes=params["block_sizes"],
        times=params["times"],
        eta=params["eta"],
    )
    analysis["coordinate_sensitivity_metrics"] = {"max_relative_change": 0.0, "mean_relative_change": 0.0, "projector_back_error": 0.0}
    analysis["numerical_refinement_metrics"] = refinement
    analysis["pseudospectral_proxy"] = float(pseudospectral_proxy(analysis["reduced_operator"]))
    analysis["delay_semigroup_metrics"] = {
        "history_grid_ladder": params["history_grid_ladder"],
        "step_size_ladder": params["step_size_ladder"],
        "history_operator_dimensions": refinement["history_operator_dimensions"],
        "autonomy_horizon_span": float(refinement["autonomy_horizon_relative_span"]),
        "transient_amplification_span": float(refinement["transient_relative_span"]),
        "reduced_coupling_span": float(refinement["block_residual_relative_span"]),
        "sampled_surrogate_span": float(refinement["surrogate_relative_span"]),
        "constant_history_projector_span": float(refinement["constant_history_projector_relative_span"]),
        "adjacent_terminal_projector_deformation_max": float(refinement["adjacent_terminal_projector_deformation_max"]),
        "adjacent_horizon_relative_change_max": float(refinement["adjacent_horizon_relative_change_max"]),
        "bounded_correspondence_summary": {
            "constant_history_projector_deformation": float(analysis["constant_history_projector_deformation"]),
            "terminal_correspondence_norm_min": float(refinement["terminal_correspondence_norm_min"]),
            "terminal_correspondence_norm_max": float(refinement["terminal_correspondence_norm_max"]),
        },
        "levels": refinement["levels"],
    }
    analysis["transportability_metrics"] = {
        "horizon_ratio": horizon_ratio(
            float(analysis["autonomy_horizon"]),
            float(analysis["predicted_autonomy_horizon"]),
        ),
        "history_operator_dimension": float(params["slow_count"] * params["history_grid_size"]),
        "pseudospectral_proxy": float(analysis["pseudospectral_proxy"]),
        "delay_refinement_protocol": {
            "history_grid_sizes": params["history_grid_ladder"],
            "step_sizes": params["step_size_ladder"],
            "surrogate_relative_span": refinement["surrogate_relative_span"],
            "transient_relative_span": refinement["transient_relative_span"],
            "block_residual_relative_span": refinement["block_residual_relative_span"],
            "adjacent_terminal_projector_deformation_max": refinement["adjacent_terminal_projector_deformation_max"],
        },
    }
    analysis["notes"] = [
        "True fixed-lag delay benchmark analyzed through a sampled history propagator and treated as discretization-backed evidence rather than a full delay-semigroup theorem.",
        "A history-grid and step-size refinement ladder is required before the delay benchmark is counted as admissible T2/T3 supporting evidence.",
        "Delay evidence is cited only with the bounded correspondence metrics and adjacent refinement-stability diagnostics reported together.",
        f"Seed {seed} leaves the reference delay configuration deterministic.",
    ]
    return params, analysis


def _t2_same_spectrum_counterexample(seed: int, parameter_id: str = "reference") -> tuple[dict, dict]:
    del seed
    if parameter_id not in {"reference", "matched_normal"}:
        raise KeyError(f"unknown parameter_id for BP_T2_Same_Spectrum_Pair: {parameter_id}")

    times = np.linspace(0.0, 6.0, 25)
    eta = 0.45
    slow_count = 2
    block_sizes = [1, 1]
    slow_eigenvalues = np.diag([-0.08, -0.13])
    rotation = np.array(
        [
            [np.cos(0.7), -np.sin(0.7)],
            [np.sin(0.7), np.cos(0.7)],
        ],
        dtype=float,
    )
    slow_normal = rotation @ slow_eigenvalues @ rotation.T
    slow_nonnormal = np.array([[-0.08, 2.2], [0.0, -0.13]], dtype=float)
    fast = np.array([[-1.1, 0.08], [0.0, -1.3]], dtype=float)
    coupling = np.array([[0.05, 0.0], [0.0, 0.04]], dtype=float)
    zero = np.zeros((2, 2), dtype=float)
    perturbation = 0.01 * np.array(
        [
            [0.1, -0.2, 0.1, 0.0],
            [0.0, 0.2, 0.0, -0.1],
            [0.0, 0.1, -0.2, 0.0],
            [0.0, 0.0, 0.1, 0.2],
        ],
        dtype=float,
    )

    branches = {
        "matched_normal": {
            "label": "matched_normal",
            "generator": np.block([[slow_normal, coupling], [zero, fast]]),
            "description": "Rotated normal slow block with the same retained eigenvalues as the counterexample branch.",
        },
        "reference": {
            "label": "matched_nonnormal",
            "generator": np.block([[slow_nonnormal, coupling], [zero, fast]]),
            "description": "Upper-triangular nonnormal slow block with the same retained eigenvalues as the matched normal branch.",
        },
    }

    analyses: dict[str, dict] = {}
    fit_summaries: dict[str, dict] = {}
    fit_tables: dict[str, dict] = {}
    for branch_id, branch in branches.items():
        generator = np.asarray(branch["generator"], dtype=float)
        identified_generator = generator + perturbation
        result = analyze_linear_generator(
            generator,
            slow_count=slow_count,
            block_sizes=block_sizes,
            times=times.tolist(),
            eta=eta,
            identified_generator=identified_generator,
        )
        gamma_profile = np.asarray(semigroup_growth_profile(result["reduced_operator"], times), dtype=float)
        leakage = np.asarray(result["leakage_trajectory"], dtype=float)
        epsilon = np.full_like(leakage, float(result["projector_deformation"]))
        rho = np.full_like(leakage, float(result["block_residual_norm"])) * np.maximum(times, 1.0e-12)
        fits = fit_all_laws(epsilon, rho, leakage, gamma=gamma_profile)
        result["fit_gamma"] = gamma_profile
        result["pseudospectral_proxy"] = float(pseudospectral_proxy(result["reduced_operator"]))
        analyses[branch_id] = result
        fit_summaries[branch_id] = law_selection_summary(fits).to_dict()
        fit_tables[branch_id] = {key: value.to_dict() for key, value in fits.items()}

    current = analyses[parameter_id]
    current_id = parameter_id
    paired_id = "matched_normal" if current_id == "reference" else "reference"
    current_label = branches[current_id]["label"]
    paired_label = branches[paired_id]["label"]
    current_fit_summary = fit_summaries[current_id]
    current_fit_table = fit_tables[current_id]
    paired_analysis = analyses[paired_id]
    paired_fit_summary = fit_summaries[paired_id]
    paired_fit_table = fit_tables[paired_id]

    current["transportability_metrics"] = {
        "same_spectrum_counterexample": {
            "current_branch": current_label,
            "paired_branch": paired_label,
            "current_gap": float(current["spectral_gap"]),
            "paired_gap": float(paired_analysis["spectral_gap"]),
            "gap_difference": float(current["spectral_gap"] - paired_analysis["spectral_gap"]),
            "current_transient_amplification": float(current["transient_amplification_score"]),
            "paired_transient_amplification": float(paired_analysis["transient_amplification_score"]),
            "transient_amplification_ratio": float(
                current["transient_amplification_score"] / max(float(paired_analysis["transient_amplification_score"]), 1.0e-12)
            ),
            "current_autonomy_horizon": float(current["autonomy_horizon"]),
            "paired_autonomy_horizon": float(paired_analysis["autonomy_horizon"]),
            "current_pseudospectral_proxy": float(current["pseudospectral_proxy"]),
            "paired_pseudospectral_proxy": float(paired_analysis["pseudospectral_proxy"]),
            "current_best_law": current_fit_summary["best_law"],
            "paired_best_law": paired_fit_summary["best_law"],
            "current_l3_minus_l1_rmse": float(current_fit_table["L1"]["test_rmse"] - current_fit_table["L3"]["test_rmse"]),
            "paired_l3_minus_l1_rmse": float(paired_fit_table["L1"]["test_rmse"] - paired_fit_table["L3"]["test_rmse"]),
        }
    }
    current["notes"] = [
        "This benchmark holds the retained slow eigenvalues fixed while changing the slow-block geometry from rotated normal to upper-triangular nonnormal form.",
        "The paired branch comparison is intended as Paper C failure-geometry evidence, not as a new theorem closure claim.",
    ]
    params = {
        "parameter_id": current_label,
        "times": times.tolist(),
        "eta": eta,
        "slow_count": slow_count,
        "block_sizes": block_sizes,
        "paired_parameter_id": paired_label,
        "slow_eigenvalues": [-0.08, -0.13],
        "fast_eigenvalues": [-1.1, -1.3],
        "pairing_rule": "same retained eigenvalues, different slow-block geometry",
    }
    return params, current


def _windowed_transport_flow(seed: int) -> tuple[dict, dict]:
    del seed
    params = {
        "windows": list(range(1, 7)),
        "eta": 0.38,
        "grid_size": 24,
        "window_count": 6,
        "coherent_rank": 2,
        "block_sizes": [1, 1],
        "base_shift": 0.8,
        "phase_increment": 0.9,
        "diffusion": 2.8,
        "coherent_strength": 2.4,
    }
    operators = build_windowed_transport_flow(
        grid_size=params["grid_size"],
        window_count=params["window_count"],
        base_shift=params["base_shift"],
        phase_increment=params["phase_increment"],
        diffusion=params["diffusion"],
        coherent_strength=params["coherent_strength"],
    )
    params["window_groups"] = [[0], [1, 2], [3], [4, 5]]
    analysis = _analyze_transport_case(
        operators,
        eta=params["eta"],
        coherent_rank=params["coherent_rank"],
        block_sizes=params["block_sizes"],
        window_groups=params["window_groups"],
    )
    analysis["notes"] = [
        "Reference transport case uses moderate phase drift so coherent lobes persist across windows without collapsing into a frozen surrogate.",
        "The frozen surrogate is retained as a weaker baseline and should lose autonomy horizon relative to coherent-window tracking.",
        "A fixed regrouping diagnostic is reported to expose finite-window sensitivity without promoting it to a gate-fatal condition yet.",
    ]
    return params, analysis


def _merge_transport_windows(operators: list[np.ndarray], window_groups: list[list[int]]) -> list[np.ndarray]:
    """Compose adjacent window operators into a coarser partition."""

    merged: list[np.ndarray] = []
    for group in window_groups:
        product = np.eye(operators[0].shape[0], dtype=float)
        for index in group:
            product = operators[index] @ product
        merged.append(product)
    return merged


def _analyze_transport_case(
    operators: list[np.ndarray],
    *,
    eta: float,
    coherent_rank: int,
    block_sizes: list[int],
    window_groups: list[list[int]] | None = None,
) -> dict:
    analysis = analyze_windowed_transport(
        operators,
        coherent_rank=coherent_rank,
        block_sizes=block_sizes,
        eta=eta,
    )
    coherent_diagnostics = analysis.pop("transport_diagnostics", {})
    frozen = analyze_windowed_transport(
        [sum(operators) / len(operators)] * len(operators),
        coherent_rank=coherent_rank,
        block_sizes=block_sizes,
        eta=eta,
    )
    frozen_diagnostics = frozen.pop("transport_diagnostics", {})
    coherent_leakage = [float(value) for value in analysis["leakage_trajectory"]]
    frozen_leakage = [float(value) for value in frozen["leakage_trajectory"]]
    leakage_advantage = [coherent - baseline for coherent, baseline in zip(coherent_leakage, frozen_leakage, strict=True)]
    transportability_metrics = {
        "coherent_vs_frozen_horizon_gain": float(analysis["autonomy_horizon"] - frozen["autonomy_horizon"]),
        "coherent_horizon": float(analysis["autonomy_horizon"]),
        "frozen_horizon": float(frozen["autonomy_horizon"]),
        "coherent_mean_leakage": float(np.mean(coherent_leakage)),
        "frozen_mean_leakage": float(np.mean(frozen_leakage)),
        "coherent_peak_leakage": float(coherent_diagnostics.get("cumulative_peak_leakage", 0.0)),
        "frozen_peak_leakage": float(frozen_diagnostics.get("cumulative_peak_leakage", 0.0)),
        "coherent_better_window_count": float(sum(delta <= 0.0 for delta in leakage_advantage)),
        "coherent_minus_frozen_leakage": leakage_advantage,
        "coherent_window_leakage": coherent_diagnostics.get("window_leakage_trajectory", []),
        "frozen_window_leakage": frozen_diagnostics.get("window_leakage_trajectory", []),
        "coherent_window_singular_gaps": coherent_diagnostics.get("singular_gap_trajectory", []),
        "frozen_window_singular_gaps": frozen_diagnostics.get("singular_gap_trajectory", []),
        "source_tracking": coherent_diagnostics.get("source_tracking", {}),
        "target_tracking": coherent_diagnostics.get("target_tracking", {}),
        "carrier_tracking": coherent_diagnostics.get("carrier_tracking", {}),
    }
    if window_groups is not None:
        regrouped = analyze_windowed_transport(
            _merge_transport_windows(operators, window_groups),
            coherent_rank=coherent_rank,
            block_sizes=block_sizes,
            eta=eta,
        )
        regrouped_diagnostics = regrouped.pop("transport_diagnostics", {})
        base_horizon_gain = float(analysis["autonomy_horizon"] - frozen["autonomy_horizon"])
        regrouped_frozen = analyze_windowed_transport(
            [sum(_merge_transport_windows(operators, window_groups)) / len(window_groups)] * len(window_groups),
            coherent_rank=coherent_rank,
            block_sizes=block_sizes,
            eta=eta,
        )
        regrouped_frozen.pop("transport_diagnostics", {})
        regrouped_horizon_gain = float(regrouped["autonomy_horizon"] - regrouped_frozen["autonomy_horizon"])
        base_carrier = float(coherent_diagnostics.get("carrier_tracking", {}).get("mean_deformation", 0.0))
        regrouped_carrier = float(regrouped_diagnostics.get("carrier_tracking", {}).get("mean_deformation", 0.0))
        base_horizon = float(analysis["autonomy_horizon"])
        regrouped_horizon = float(regrouped["autonomy_horizon"])
        transportability_metrics["window_sensitivity"] = {
            "window_groups": window_groups,
            "base_window_count": len(operators),
            "regrouped_window_count": len(window_groups),
            "regrouped_horizon_gain": regrouped_horizon_gain,
            "regrouped_autonomy_horizon": regrouped_horizon,
            "regrouped_singular_gap": float(regrouped["singular_gap"]),
            "regrouped_carrier_mean_deformation": regrouped_carrier,
            "regrouped_carrier_max_deformation": float(
                regrouped_diagnostics.get("carrier_tracking", {}).get("max_deformation", 0.0)
            ),
            "adjacent_window_carrier_mean_deformation": base_carrier,
            "adjacent_window_carrier_max_deformation": float(
                coherent_diagnostics.get("carrier_tracking", {}).get("max_deformation", 0.0)
            ),
            "autonomy_horizon_relative_span": abs(base_horizon - regrouped_horizon) / max(abs(base_horizon), 1.0),
            "horizon_gain_relative_span": abs(base_horizon_gain - regrouped_horizon_gain) / max(abs(base_horizon_gain), 1.0),
            "carrier_deformation_relative_span": abs(base_carrier - regrouped_carrier) / max(abs(base_carrier), 1.0e-6),
        }
    analysis["transportability_metrics"] = transportability_metrics
    analysis["coordinate_sensitivity_metrics"] = {"max_relative_change": 0.0, "mean_relative_change": 0.0, "projector_back_error": 0.0}
    analysis["numerical_refinement_metrics"] = numerical_refinement_metric([analysis["autonomy_horizon"]])
    return analysis


def _t3_window_sensitivity_pair(seed: int, parameter_id: str = "reference") -> tuple[dict, dict]:
    del seed
    branches = {
        "reference": {
            "case_label": "fast_drift_mixed",
            "phase_increment": 2.4,
            "diffusion": 2.8,
            "coherent_strength": 2.0,
            "paired_parameter_id": "matched_positive",
        },
        "matched_positive": {
            "case_label": "moderate_drift_positive",
            "phase_increment": 0.9,
            "diffusion": 2.8,
            "coherent_strength": 2.4,
            "paired_parameter_id": "reference",
        },
    }
    selected = branches[parameter_id]
    paired = branches[selected["paired_parameter_id"]]
    common = {
        "windows": list(range(1, 7)),
        "eta": 0.38,
        "grid_size": 24,
        "window_count": 6,
        "coherent_rank": 2,
        "block_sizes": [1, 1],
        "base_shift": 0.8,
        "window_groups": [[0], [1, 2], [3], [4, 5]],
    }
    current_operators = build_windowed_transport_flow(
        grid_size=common["grid_size"],
        window_count=common["window_count"],
        base_shift=common["base_shift"],
        phase_increment=selected["phase_increment"],
        diffusion=selected["diffusion"],
        coherent_strength=selected["coherent_strength"],
    )
    paired_operators = build_windowed_transport_flow(
        grid_size=common["grid_size"],
        window_count=common["window_count"],
        base_shift=common["base_shift"],
        phase_increment=paired["phase_increment"],
        diffusion=paired["diffusion"],
        coherent_strength=paired["coherent_strength"],
    )
    current = _analyze_transport_case(
        current_operators,
        eta=common["eta"],
        coherent_rank=common["coherent_rank"],
        block_sizes=common["block_sizes"],
        window_groups=common["window_groups"],
    )
    paired_analysis = _analyze_transport_case(
        paired_operators,
        eta=common["eta"],
        coherent_rank=common["coherent_rank"],
        block_sizes=common["block_sizes"],
        window_groups=common["window_groups"],
    )
    current_transport = current["transportability_metrics"]
    paired_transport = paired_analysis["transportability_metrics"]
    current_transport["positive_negative_transport_pair"] = {
        "current_branch": selected["case_label"],
        "paired_branch": paired["case_label"],
        "current_horizon_gain": float(current_transport["coherent_vs_frozen_horizon_gain"]),
        "paired_horizon_gain": float(paired_transport["coherent_vs_frozen_horizon_gain"]),
        "current_carrier_deformation": float(current_transport["carrier_tracking"].get("mean_deformation", 0.0)),
        "paired_carrier_deformation": float(paired_transport["carrier_tracking"].get("mean_deformation", 0.0)),
        "current_singular_gap": float(current["singular_gap"]),
        "paired_singular_gap": float(paired_analysis["singular_gap"]),
        "current_regrouped_horizon_gain": float(
            current_transport.get("window_sensitivity", {}).get("regrouped_horizon_gain", 0.0)
        ),
        "paired_regrouped_horizon_gain": float(
            paired_transport.get("window_sensitivity", {}).get("regrouped_horizon_gain", 0.0)
        ),
        "current_regrouped_carrier_deformation": float(
            current_transport.get("window_sensitivity", {}).get("regrouped_carrier_mean_deformation", 0.0)
        ),
        "paired_regrouped_carrier_deformation": float(
            paired_transport.get("window_sensitivity", {}).get("regrouped_carrier_mean_deformation", 0.0)
        ),
    }
    current["notes"] = [
        "This paired T3 family keeps the transport construction fixed while changing phase drift and coherent strength to expose window-sensitive failure geometry.",
        "The moderate-drift branch is a positive control; the fast-drift branch is mixed or negative evidence and is reported without becoming gate-fatal in G3.",
    ]
    params = {
        **common,
        "parameter_id": parameter_id,
        "case_label": selected["case_label"],
        "phase_increment": selected["phase_increment"],
        "diffusion": selected["diffusion"],
        "coherent_strength": selected["coherent_strength"],
        "paired_parameter_id": selected["paired_parameter_id"],
        "paired_case_label": paired["case_label"],
        "paired_phase_increment": paired["phase_increment"],
        "paired_diffusion": paired["diffusion"],
        "paired_coherent_strength": paired["coherent_strength"],
    }
    return params, current


def _analyze_application_transport(
    operators: list[np.ndarray],
    *,
    refined_operators: list[np.ndarray],
    eta: float,
    coherent_rank: int,
    block_sizes: list[int],
) -> dict:
    """Shared transport-style analysis for application benchmarks."""

    analysis = analyze_windowed_transport(
        operators,
        coherent_rank=coherent_rank,
        block_sizes=block_sizes,
        eta=eta,
    )
    coherent_diagnostics = analysis.pop("transport_diagnostics", {})
    frozen = analyze_windowed_transport(
        [sum(operators) / len(operators)] * len(operators),
        coherent_rank=coherent_rank,
        block_sizes=block_sizes,
        eta=eta,
    )
    frozen_diagnostics = frozen.pop("transport_diagnostics", {})
    refined = analyze_windowed_transport(
        refined_operators,
        coherent_rank=coherent_rank,
        block_sizes=block_sizes,
        eta=eta,
    )
    coherent_leakage = [float(value) for value in analysis["leakage_trajectory"]]
    frozen_leakage = [float(value) for value in frozen["leakage_trajectory"]]
    leakage_advantage = [coherent - baseline for coherent, baseline in zip(coherent_leakage, frozen_leakage, strict=True)]
    refinement_gap = numerical_refinement_metric(
        [float(analysis["singular_gap"]), float(refined["singular_gap"])]
    )
    refinement_deformation = numerical_refinement_metric(
        [float(analysis["coherent_projector_deformation"]), float(refined["coherent_projector_deformation"])]
    )
    refinement_residual = numerical_refinement_metric(
        [float(analysis["block_residual_norm"]), float(refined["block_residual_norm"])]
    )
    analysis["transportability_metrics"] = {
        "coherent_vs_frozen_horizon_gain": float(analysis["autonomy_horizon"] - frozen["autonomy_horizon"]),
        "coherent_horizon": float(analysis["autonomy_horizon"]),
        "frozen_horizon": float(frozen["autonomy_horizon"]),
        "coherent_mean_leakage": float(np.mean(coherent_leakage)),
        "frozen_mean_leakage": float(np.mean(frozen_leakage)),
        "coherent_minus_frozen_leakage": leakage_advantage,
        "coherent_window_singular_gaps": coherent_diagnostics.get("singular_gap_trajectory", []),
        "frozen_window_singular_gaps": frozen_diagnostics.get("singular_gap_trajectory", []),
        "coherent_window_leakage": coherent_diagnostics.get("window_leakage_trajectory", []),
        "frozen_window_leakage": frozen_diagnostics.get("window_leakage_trajectory", []),
        "carrier_tracking": coherent_diagnostics.get("carrier_tracking", {}),
    }
    analysis["coordinate_sensitivity_metrics"] = {
        "max_relative_change": 0.0,
        "mean_relative_change": 0.0,
        "projector_back_error": 0.0,
    }
    analysis["numerical_refinement_metrics"] = {
        "max_relative_span": float(
            max(
                refinement_gap["max_relative_span"],
                refinement_deformation["max_relative_span"],
                refinement_residual["max_relative_span"],
            )
        ),
        "mean": float(
            np.mean(
                [
                    refinement_gap["mean"],
                    refinement_deformation["mean"],
                    refinement_residual["mean"],
                ]
            )
        ),
        "refinement_axis": "pseudocount_smoothing",
        "singular_gap_relative_span": refinement_gap["max_relative_span"],
        "carrier_relative_span": refinement_deformation["max_relative_span"],
        "residual_relative_span": refinement_residual["max_relative_span"],
    }
    return analysis


def _nonlinear_slaving_profile(states: np.ndarray) -> np.ndarray:
    return 0.3 * (states[:, 0] ** 2 + 0.6 * states[:, 1] ** 2)


def _analyze_weakly_nonlinear_case(
    *,
    times: list[float],
    eta: float,
    slow_dim: int,
    epsilon_values: list[float],
    coupling: float,
    epsilon: float,
    initial_state: list[float],
) -> dict:
    def rhs(time: float, state: np.ndarray) -> np.ndarray:
        x1, x2, y = state
        return np.array(
            [
                -0.08 * x1 + 0.35 * x2 + coupling * (x2 - x1) + epsilon * y,
                -0.35 * x1 - 0.09 * x2 + coupling * (x1 - x2),
                -2.6 * (y - 0.3 * (x1**2 + 0.6 * x2**2)),
            ]
        )

    states = integrate_trajectory(rhs, initial_state, times)
    jacobians = jacobian_sequence(rhs, states, times)
    projectors = instantaneous_slow_projectors(jacobians, slow_dim)
    leakage = state_leakage_trajectory(states, projectors)
    curvature = float(curvature_indicator(estimate_slow_manifold(states, 2), states[:, 2:]))
    local_gaps = local_spectral_gaps(jacobians, slow_dim)
    projector_tracking = local_projector_tracking(projectors)
    deformation = float(projector_tracking["adjacent_mean_deformation"])
    anchor_deformation = float(projector_tracking["anchor_mean_deformation"])
    observed_horizon = max(time for time, value in zip(times, leakage, strict=True) if value <= eta)
    state_norms = np.linalg.norm(states, axis=1)
    max_state_norm = float(np.max(state_norms))
    slaved_profile = _nonlinear_slaving_profile(states)
    fast_slaving_defect = float(np.max(np.abs(states[:, 2] - slaved_profile)))
    epsilon_array = np.full(len(times), deformation, dtype=float)
    rho_array = np.full(len(times), coupling, dtype=float) * np.maximum(np.asarray(times, dtype=float), 1.0e-12)
    gamma = np.full(len(times), curvature, dtype=float)
    fits = fit_all_laws(epsilon_array, rho_array, np.asarray(leakage, dtype=float), gamma=gamma)
    local_validity_margin = float(
        min(
            0.2 - fast_slaving_defect,
            0.65 - anchor_deformation,
            1.5 - max_state_norm,
        )
    )
    return {
        "spectral_gap": float(np.mean(local_gaps)),
        "projector_deformation": deformation,
        "block_residual_norm": float(coupling),
        "leakage_trajectory": leakage,
        "autonomy_horizon": float(observed_horizon),
        "predicted_autonomy_horizon": max((eta - deformation) / coupling, 0.0),
        "cross_subsystem_transfer_rate": float(coupling),
        "reduced_model_forecast_error": float(np.mean(np.abs(states[:, 2]))),
        "transient_amplification_score": 1.0,
        "coordinate_sensitivity_metrics": {"max_relative_change": 0.0, "mean_relative_change": 0.0, "projector_back_error": 0.0},
        "numerical_refinement_metrics": {"max_relative_span": 0.0, "mean": float(observed_horizon)},
        "local_validity_metrics": {
            "adjacent_projector_deformation": deformation,
            "anchor_projector_deformation": anchor_deformation,
            "fast_slaving_defect": fast_slaving_defect,
            "curvature_indicator": curvature,
            "max_state_norm": max_state_norm,
            "local_validity_margin": local_validity_margin,
            "l2_minus_l1_rmse": float(fits["L1"].test_rmse - fits["L2"].test_rmse),
        },
        "transportability_metrics": {
            "curvature_indicator": curvature,
            "projector_tracking": projector_tracking,
            "local_validity_neighborhood": {
                "initial_state_norm": float(np.linalg.norm(states[0])),
                "max_state_norm": max_state_norm,
                "fast_coordinate_abs_max": float(np.max(np.abs(states[:, 2]))),
                "fast_slaving_defect": fast_slaving_defect,
                "local_validity_margin": local_validity_margin,
            },
            "continuation": continue_family(
                epsilon_values,
                lambda value: {"epsilon": value, "fast_bias": float(value - epsilon)},
            ),
        },
        "fit_gamma": gamma,
    }


def _weakly_nonlinear_slow_manifold(seed: int) -> tuple[dict, dict]:
    del seed
    params = {
        "times": np.linspace(0.0, 12.0, 61).tolist(),
        "eta": 0.32,
        "slow_dim": 2,
        "block_sizes": [1, 1],
        "epsilon_values": [0.05, 0.08, 0.12],
        "coupling": 0.07,
        "epsilon": 0.08,
        "initial_state": [1.0, -0.6, 0.3],
    }
    analysis = _analyze_weakly_nonlinear_case(
        times=params["times"],
        eta=params["eta"],
        slow_dim=params["slow_dim"],
        epsilon_values=params["epsilon_values"],
        coupling=params["coupling"],
        epsilon=params["epsilon"],
        initial_state=params["initial_state"],
    )
    analysis["notes"] = [
        "Nonlinear projector deformation is measured by adjacent carrier drift, matching the local-manifold T4 claim rather than long-horizon drift from the initial carrier.",
        "The accepted reference case remains local: the fast coordinate stays slaved while curvature corrections remain diagnostic rather than dominant.",
    ]
    return params, analysis


def _t4_local_validity_pair(seed: int, parameter_id: str = "reference") -> tuple[dict, dict]:
    del seed
    branches = {
        "reference": {
            "case_label": "amplitude_breakdown",
            "epsilon": 0.04,
            "coupling": 0.04,
            "initial_state": [1.6, -0.96, 0.5],
            "paired_parameter_id": "matched_local",
        },
        "matched_local": {
            "case_label": "matched_local",
            "epsilon": 0.08,
            "coupling": 0.07,
            "initial_state": [1.0, -0.6, 0.3],
            "paired_parameter_id": "reference",
        },
    }
    common = {
        "times": np.linspace(0.0, 12.0, 61).tolist(),
        "eta": 0.32,
        "slow_dim": 2,
        "block_sizes": [1, 1],
        "epsilon_values": [0.04, 0.08, 0.12],
    }
    analyses: dict[str, dict] = {}
    fit_summaries: dict[str, dict] = {}
    fit_tables: dict[str, dict] = {}
    for branch_id, branch in branches.items():
        result = _analyze_weakly_nonlinear_case(
            times=common["times"],
            eta=common["eta"],
            slow_dim=common["slow_dim"],
            epsilon_values=common["epsilon_values"],
            coupling=branch["coupling"],
            epsilon=branch["epsilon"],
            initial_state=branch["initial_state"],
        )
        leakage = np.asarray(result["leakage_trajectory"], dtype=float)
        gamma = np.asarray(result["fit_gamma"], dtype=float)
        epsilon_array = np.full_like(leakage, float(result["projector_deformation"]))
        rho_array = np.full_like(leakage, branch["coupling"]) * np.maximum(np.asarray(common["times"], dtype=float), 1.0e-12)
        fits = fit_all_laws(epsilon_array, rho_array, leakage, gamma=gamma)
        analyses[branch_id] = result
        fit_summaries[branch_id] = law_selection_summary(fits).to_dict()
        fit_tables[branch_id] = {key: value.to_dict() for key, value in fits.items()}
    current = analyses[parameter_id]
    paired_id = branches[parameter_id]["paired_parameter_id"]
    current_local = current["local_validity_metrics"]
    paired_analysis = analyses[paired_id]
    paired_local = paired_analysis["local_validity_metrics"]
    current["transportability_metrics"]["local_validity_pair"] = {
        "current_branch": branches[parameter_id]["case_label"],
        "paired_branch": branches[paired_id]["case_label"],
        "current_best_law": fit_summaries[parameter_id]["best_law"],
        "paired_best_law": fit_summaries[paired_id]["best_law"],
        "current_local_validity_margin": float(current_local["local_validity_margin"]),
        "paired_local_validity_margin": float(paired_local["local_validity_margin"]),
        "current_fast_slaving_defect": float(current_local["fast_slaving_defect"]),
        "paired_fast_slaving_defect": float(paired_local["fast_slaving_defect"]),
        "current_anchor_projector_deformation": float(current_local["anchor_projector_deformation"]),
        "paired_anchor_projector_deformation": float(paired_local["anchor_projector_deformation"]),
        "current_l2_minus_l1_rmse": float(current_local["l2_minus_l1_rmse"]),
        "paired_l2_minus_l1_rmse": float(paired_local["l2_minus_l1_rmse"]),
    }
    current["notes"] = [
        "This paired T4 family keeps the same fast-slow template while separating a locally valid regime from an amplitude-driven local-validity breakdown regime.",
        "The pair is protocol evidence for bounded local validity, not a global nonlinear theorem claim.",
    ]
    params = {
        **common,
        "parameter_id": branches[parameter_id]["case_label"],
        "paired_parameter_id": branches[paired_id]["case_label"],
        "epsilon": branches[parameter_id]["epsilon"],
        "coupling": branches[parameter_id]["coupling"],
        "initial_state": branches[parameter_id]["initial_state"],
        "paired_epsilon": branches[paired_id]["epsilon"],
        "paired_coupling": branches[paired_id]["coupling"],
        "paired_initial_state": branches[paired_id]["initial_state"],
    }
    return params, current


def _series_horizon(times: list[float], values: np.ndarray, eta: float) -> float:
    horizon = float(times[0])
    for time, value in zip(times, values, strict=True):
        if value <= eta:
            horizon = float(time)
    return horizon


def _analyze_stochastic_case(
    transition: np.ndarray,
    *,
    steps: int,
    eta: float,
    slow_count: int,
    trajectories: int,
    source_states: list[int],
    seed: int,
) -> dict:
    analysis = analyze_stochastic_transition(
        transition,
        source_states=source_states,
        slow_count=slow_count,
        steps=steps,
        eta=eta,
    )
    sampled = run_mc(
        transition,
        start_distribution=[0.5, 0.5, 0.0, 0.0],
        steps=steps,
        trajectories=trajectories,
        seed=seed,
    )
    ensemble = ensemble_leakage_trajectory(sampled, set(source_states))
    terminal = 1.0 - np.isin(sampled[:, -1], source_states).astype(float)
    estimated = estimate_propagator(sampled, transition.shape[0])
    lower, upper = bootstrap_ci(terminal, seed=seed)
    bootstrap_width = float(upper - lower)
    confidence_series = np.minimum(ensemble + bootstrap_width, 1.0)
    msm = build_msm(estimated)
    analysis["ensemble_averaged_leakage"] = float(np.mean(terminal))
    analysis["leakage_variance"] = float(np.var(terminal, ddof=1))
    analysis["stochastic_uncertainty_metrics"] = {
        "bootstrap_width": bootstrap_width,
        "ensemble_mean_leakage": float(np.mean(terminal)),
        "metastability_score": float(msm["metastability_score"]),
        "effective_sample_size": float(trajectories),
        "estimated_horizon": _series_horizon(list(range(steps + 1)), ensemble, eta),
        "confidence_bounded_horizon": _series_horizon(list(range(steps + 1)), confidence_series, eta),
        "estimation_error_proxy": float(np.linalg.norm(estimated - transition, ord=2)),
    }
    analysis["transportability_metrics"] = {
        "bootstrap_ci_lower": lower,
        "bootstrap_ci_upper": upper,
        "metastability_score": msm["metastability_score"],
    }
    analysis["coordinate_sensitivity_metrics"] = {"max_relative_change": 0.0, "mean_relative_change": 0.0, "projector_back_error": 0.0}
    analysis["numerical_refinement_metrics"] = numerical_refinement_metric([float(np.mean(ensemble))])
    return analysis


def _noisy_metastable_network(seed: int) -> tuple[dict, dict]:
    params = {
        "times": list(range(13)),
        "steps": 12,
        "eta": 0.28,
        "slow_count": 2,
        "trajectories": 400,
        "source_states": [0, 1],
    }
    transition = np.array(
        [[0.90, 0.07, 0.02, 0.01], [0.06, 0.90, 0.01, 0.03], [0.03, 0.01, 0.90, 0.06], [0.01, 0.03, 0.07, 0.89]]
    )
    analysis = _analyze_stochastic_case(
        transition,
        steps=params["steps"],
        eta=params["eta"],
        slow_count=params["slow_count"],
        trajectories=params["trajectories"],
        source_states=params["source_states"],
        seed=seed,
    )
    analysis["notes"] = [
        "The accepted stochastic reference keeps the metastable network fixed and uses enough trajectories to keep the bootstrap width narrow relative to the leakage threshold.",
        "Paper D treats the reported confidence-bounded horizon as a probabilistic evidence object rather than a theorem-level guarantee.",
    ]
    return params, analysis


def _t5_stochastic_stress_pair(seed: int, parameter_id: str = "reference") -> tuple[dict, dict]:
    branches = {
        "reference": {
            "case_label": "sample_stress",
            "trajectories": 40,
            "paired_parameter_id": "matched_metastable",
        },
        "matched_metastable": {
            "case_label": "matched_metastable",
            "trajectories": 400,
            "paired_parameter_id": "reference",
        },
    }
    common = {
        "times": list(range(13)),
        "steps": 12,
        "eta": 0.28,
        "slow_count": 2,
        "source_states": [0, 1],
    }
    transition = np.array(
        [[0.90, 0.07, 0.02, 0.01], [0.06, 0.90, 0.01, 0.03], [0.03, 0.01, 0.90, 0.06], [0.01, 0.03, 0.07, 0.89]]
    )
    analyses: dict[str, dict] = {}
    for branch_id, branch in branches.items():
        analyses[branch_id] = _analyze_stochastic_case(
            transition,
            steps=common["steps"],
            eta=common["eta"],
            slow_count=common["slow_count"],
            trajectories=branch["trajectories"],
            source_states=common["source_states"],
            seed=seed,
        )
    current = analyses[parameter_id]
    paired_id = branches[parameter_id]["paired_parameter_id"]
    current_uncertainty = current["stochastic_uncertainty_metrics"]
    paired_uncertainty = analyses[paired_id]["stochastic_uncertainty_metrics"]
    current["transportability_metrics"]["stochastic_uncertainty_pair"] = {
        "current_branch": branches[parameter_id]["case_label"],
        "paired_branch": branches[paired_id]["case_label"],
        "current_bootstrap_width": float(current_uncertainty["bootstrap_width"]),
        "paired_bootstrap_width": float(paired_uncertainty["bootstrap_width"]),
        "current_confidence_bounded_horizon": float(current_uncertainty["confidence_bounded_horizon"]),
        "paired_confidence_bounded_horizon": float(paired_uncertainty["confidence_bounded_horizon"]),
        "current_estimation_error_proxy": float(current_uncertainty["estimation_error_proxy"]),
        "paired_estimation_error_proxy": float(paired_uncertainty["estimation_error_proxy"]),
        "current_effective_sample_size": float(current_uncertainty["effective_sample_size"]),
        "paired_effective_sample_size": float(paired_uncertainty["effective_sample_size"]),
    }
    current["notes"] = [
        "This paired T5 family keeps the metastable transition structure fixed and isolates sample stress as the source of wider uncertainty and degraded confidence-bounded horizons.",
        "The pair is evidence for bounded probabilistic validity, not a finite-sample concentration theorem.",
    ]
    params = {
        **common,
        "parameter_id": branches[parameter_id]["case_label"],
        "paired_parameter_id": branches[paired_id]["case_label"],
        "trajectories": branches[parameter_id]["trajectories"],
        "paired_trajectories": branches[paired_id]["trajectories"],
    }
    return params, current


def _mobility_chicago_corridors(
    seed: int,
    parameter_id: str = "reference",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    return _mobility_application_benchmark(
        seed,
        benchmark_id="BP_Mobility_Chicago_Corridors",
        parameter_id=parameter_id,
        overrides=overrides,
        benchmark_note="Derived real-data fixture from 202401-divvy-tripdata.zip using the Hyde Park station slice documented in the benchmark README.",
    )


def _mobility_downtown_routing_instability(
    seed: int,
    parameter_id: str = "reference",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    return _mobility_application_benchmark(
        seed,
        benchmark_id="BP_Mobility_Downtown_Routing_Instability",
        parameter_id=parameter_id,
        overrides=overrides,
        benchmark_note="Derived real-data fixture from 202401-divvy-tripdata.zip using a downtown Chicago station slice selected for route-instability rather than low-count sparsity.",
    )


def _mobility_nyc_east_corridor(
    seed: int,
    parameter_id: str = "reference",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    return _mobility_application_benchmark(
        seed,
        benchmark_id="BP_Mobility_NYC_East_Corridor",
        parameter_id=parameter_id,
        overrides=overrides,
        benchmark_note="Derived real-data fixture from 202401-citibike-tripdata.zip using a Manhattan east-side station slice selected as a mixed external application case.",
    )


def _mobility_application_benchmark(
    seed: int,
    *,
    benchmark_id: str,
    parameter_id: str = "reference",
    overrides: dict | None = None,
    benchmark_note: str,
) -> tuple[dict, dict]:
    del seed
    fixture = mobility_parameter_set(parameter_id, overrides=overrides, benchmark_id=benchmark_id)
    operators, fixture_metadata = build_windowed_mobility_operators(
        fixture,
        pseudocount=float(fixture["pseudocount"]),
        benchmark_id=benchmark_id,
    )
    params = {
        "windows": list(range(1, len(operators) + 1)),
        "window_labels": fixture["window_labels"],
        "eta": fixture["eta"],
        "coherent_rank": fixture["coherent_rank"],
        "block_sizes": fixture["block_sizes"],
        "station_names": fixture_metadata["station_names"],
        "station_ids": fixture_metadata["station_ids"],
        "total_trips": fixture["total_trips"],
        "pseudocount": fixture["pseudocount"],
        "refined_pseudocount": fixture["refined_pseudocount"],
        "case_label": fixture["case_label"],
        "source_archive": fixture_metadata["source_archive"],
        "base_parameter_id": fixture["base_parameter_id"],
    }
    if fixture_metadata.get("station_subset_indices") is not None:
        params["station_subset_indices"] = fixture_metadata["station_subset_indices"]
    if fixture_metadata.get("window_groups") is not None:
        params["window_groups"] = fixture_metadata["window_groups"]
    refined_operators, _ = build_windowed_mobility_operators(
        fixture,
        pseudocount=float(fixture["refined_pseudocount"]),
        benchmark_id=benchmark_id,
    )
    analysis = _analyze_application_transport(
        operators,
        refined_operators=refined_operators,
        eta=params["eta"],
        coherent_rank=params["coherent_rank"],
        block_sizes=params["block_sizes"],
    )
    analysis["transportability_metrics"].update({
        "source_page": fixture_metadata["source_page"],
        "source_archive": fixture_metadata["source_archive"],
        "derivation_summary": fixture_metadata["derivation_summary"],
        "selected_station_names": fixture_metadata["station_names"],
        "selected_station_ids": fixture_metadata["station_ids"],
        "total_trips": float(fixture["total_trips"]),
        "case_label": fixture["case_label"],
        "base_parameter_id": fixture["base_parameter_id"],
    })
    analysis["numerical_refinement_metrics"].update(
        {
            "coarse_pseudocount": float(fixture["pseudocount"]),
            "refined_pseudocount": float(fixture["refined_pseudocount"]),
        }
    )
    analysis["notes"] = [
        benchmark_note,
        "Coordinate sensitivity is left neutral because arbitrary orthogonal basis changes are not meaningful on named mobility stations in this first application case study.",
    ]
    return params, analysis


def _named_navigation_application_benchmark(
    seed: int,
    *,
    parameter_id: str,
    overrides: dict | None,
    benchmark_id: str,
    parameter_loader,
    operator_builder,
    note_lines: list[str],
) -> tuple[dict, dict]:
    del seed
    fixture = parameter_loader(parameter_id, overrides=overrides, benchmark_id=benchmark_id)
    operators, fixture_metadata = operator_builder(
        fixture,
        pseudocount=float(fixture["pseudocount"]),
        benchmark_id=benchmark_id,
    )
    params = {
        "windows": list(range(1, len(operators) + 1)),
        "window_labels": fixture["window_labels"],
        "eta": fixture["eta"],
        "coherent_rank": fixture["coherent_rank"],
        "block_sizes": fixture["block_sizes"],
        "page_names": fixture_metadata["page_names"],
        "page_ids": fixture_metadata["page_ids"],
        "total_sessions": fixture["total_sessions"],
        "pseudocount": fixture["pseudocount"],
        "refined_pseudocount": fixture["refined_pseudocount"],
        "case_label": fixture["case_label"],
        "source_archive": fixture_metadata["source_archive"],
        "base_parameter_id": fixture["base_parameter_id"],
        "dataset_name": fixture_metadata["dataset_name"],
    }
    if fixture_metadata.get("page_subset_indices") is not None:
        params["page_subset_indices"] = fixture_metadata["page_subset_indices"]
    if fixture_metadata.get("window_groups") is not None:
        params["window_groups"] = fixture_metadata["window_groups"]
    refined_operators, _ = operator_builder(
        fixture,
        pseudocount=float(fixture["refined_pseudocount"]),
        benchmark_id=benchmark_id,
    )
    analysis = _analyze_application_transport(
        operators,
        refined_operators=refined_operators,
        eta=params["eta"],
        coherent_rank=params["coherent_rank"],
        block_sizes=params["block_sizes"],
    )
    analysis["transportability_metrics"].update(
        {
            "source_page": fixture_metadata["source_page"],
            "source_archive": fixture_metadata["source_archive"],
            "derivation_summary": fixture_metadata["derivation_summary"],
            "selected_page_names": fixture_metadata["page_names"],
            "selected_page_ids": fixture_metadata["page_ids"],
            "total_sessions": float(fixture["total_sessions"]),
            "case_label": fixture["case_label"],
            "base_parameter_id": fixture["base_parameter_id"],
            "dataset_name": fixture_metadata["dataset_name"],
        }
    )
    analysis["numerical_refinement_metrics"].update(
        {
            "coarse_pseudocount": float(fixture["pseudocount"]),
            "refined_pseudocount": float(fixture["refined_pseudocount"]),
        }
    )
    analysis["notes"] = note_lines
    return params, analysis


def _clickstream_docs_funnel(
    seed: int,
    parameter_id: str = "reference",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    return _named_navigation_application_benchmark(
        seed,
        parameter_id=parameter_id,
        overrides=overrides,
        benchmark_id="BP_Clickstream_Docs_Funnel",
        parameter_loader=clickstream_parameter_set,
        operator_builder=build_windowed_clickstream_operators,
        note_lines=[
            "Bundled non-mobility clickstream fixture extends the operator-valued application evidence beyond bike-share mobility without claiming a public-data theorem.",
            "The negative detour variant is retained to show that cross-domain application evidence still preserves explicit rejection labels when carrier geometry collapses.",
        ],
    )


def _support_navigation_funnel(
    seed: int,
    parameter_id: str = "reference",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    return _named_navigation_application_benchmark(
        seed,
        parameter_id=parameter_id,
        overrides=overrides,
        benchmark_id="BP_Support_Portal_Funnel",
        parameter_loader=support_parameter_set,
        operator_builder=build_windowed_support_operators,
        note_lines=[
            "Bundled support-navigation fixture provides a second non-mobility application domain using the same named-window operator pipeline as the clickstream benchmark.",
            "The detour-heavy support variant is retained to show that accepted and rejection-labeled cases can coexist inside the same digital-navigation evidence track.",
        ],
    )


def _workflow_queue_funnel(
    seed: int,
    parameter_id: str = "reference",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    del seed
    fixture = workflow_parameter_set(parameter_id, overrides=overrides, benchmark_id="BP_Workflow_Queue_Funnel")
    operators, fixture_metadata = build_windowed_workflow_operators(
        fixture,
        pseudocount=float(fixture["pseudocount"]),
        benchmark_id="BP_Workflow_Queue_Funnel",
    )
    params = {
        "windows": list(range(1, len(operators) + 1)),
        "window_labels": fixture["window_labels"],
        "eta": fixture["eta"],
        "coherent_rank": fixture["coherent_rank"],
        "block_sizes": fixture["block_sizes"],
        "stage_names": fixture_metadata["stage_names"],
        "stage_ids": fixture_metadata["stage_ids"],
        "total_cases": fixture["total_cases"],
        "pseudocount": fixture["pseudocount"],
        "refined_pseudocount": fixture["refined_pseudocount"],
        "case_label": fixture["case_label"],
        "source_archive": fixture_metadata["source_archive"],
        "base_parameter_id": fixture["base_parameter_id"],
        "dataset_name": fixture_metadata["dataset_name"],
    }
    if fixture_metadata.get("stage_subset_indices") is not None:
        params["stage_subset_indices"] = fixture_metadata["stage_subset_indices"]
    if fixture_metadata.get("window_groups") is not None:
        params["window_groups"] = fixture_metadata["window_groups"]
    refined_operators, _ = build_windowed_workflow_operators(
        fixture,
        pseudocount=float(fixture["refined_pseudocount"]),
        benchmark_id="BP_Workflow_Queue_Funnel",
    )
    analysis = _analyze_application_transport(
        operators,
        refined_operators=refined_operators,
        eta=params["eta"],
        coherent_rank=params["coherent_rank"],
        block_sizes=params["block_sizes"],
    )
    analysis["transportability_metrics"].update(
        {
            "source_page": fixture_metadata["source_page"],
            "source_archive": fixture_metadata["source_archive"],
            "derivation_summary": fixture_metadata["derivation_summary"],
            "selected_stage_names": fixture_metadata["stage_names"],
            "selected_stage_ids": fixture_metadata["stage_ids"],
            "total_cases": float(fixture["total_cases"]),
            "case_label": fixture["case_label"],
            "base_parameter_id": fixture["base_parameter_id"],
            "dataset_name": fixture_metadata["dataset_name"],
        }
    )
    analysis["numerical_refinement_metrics"].update(
        {
            "coarse_pseudocount": float(fixture["pseudocount"]),
            "refined_pseudocount": float(fixture["refined_pseudocount"]),
        }
    )
    analysis["notes"] = [
        "Bundled workflow-queue fixture extends the application track beyond navigation by modeling intake-to-closure operational transitions as ordered stochastic operators.",
        "The negative detour variant is retained to preserve explicit rejection evidence when triage loops and rework destroy coherent stage separation.",
    ]
    return params, analysis


def _mobility_application_status(record: dict) -> dict:
    """Evaluate Paper E application acceptance on one mobility run."""

    return evaluate_application_acceptance(record)


def _clickstream_application_status(record: dict) -> dict:
    """Evaluate acceptance on the cross-domain clickstream application."""

    return evaluate_application_acceptance(record)


def _support_application_status(record: dict) -> dict:
    """Evaluate acceptance on the support-navigation application."""

    return evaluate_application_acceptance(record)


def _workflow_application_status(record: dict) -> dict:
    """Evaluate acceptance on the workflow-queue application."""

    return evaluate_application_acceptance(record)


def run_application_case(
    *,
    benchmark_id: str = "BP_Mobility_Chicago_Corridors",
    seed: int = 0,
    parameter_id: str = "reference",
    root: str | Path | None = None,
    overrides: dict | None = None,
) -> dict:
    """Run and persist one application case, including benchmark-local variants."""

    repo_root = repository_root(Path(root) if root is not None else None)
    started = perf_counter()
    _, theorem_tier, runner = RUNNERS[benchmark_id]
    parameters, analysis = runner(seed, parameter_id=parameter_id, overrides=overrides)
    resolved_parameter_id = str((overrides or {}).get("parameter_id", parameter_id))
    return _persist_record(
        benchmark_id,
        "application",
        theorem_tier,
        seed,
        resolved_parameter_id,
        parameters,
        analysis,
        repo_root,
        started,
    )


def run_mobility_case(
    *,
    benchmark_id: str = "BP_Mobility_Chicago_Corridors",
    seed: int = 0,
    parameter_id: str = "reference",
    root: str | Path | None = None,
    overrides: dict | None = None,
) -> dict:
    """Backward-compatible wrapper for mobility application runs."""

    return run_application_case(
        benchmark_id=benchmark_id,
        seed=seed,
        parameter_id=parameter_id,
        root=root,
        overrides=overrides,
    )


def run_mobility_application_evaluation(*, seed: int = 0, root: str | Path | None = None) -> dict:
    """Run the fixed Paper E robustness sweep and write a compact summary artifact."""

    repo_root = repository_root(Path(root) if root is not None else None)
    summary_dir = repo_root / "results" / "application" / "BP_Mobility_Chicago_Corridors"
    summary_dir.mkdir(parents=True, exist_ok=True)
    case_results = []
    weekday_records = []
    for case in mobility_evaluation_cases():
        record = run_mobility_case(
            seed=seed,
            parameter_id=str(case["base_parameter_id"]),
            root=repo_root,
            overrides=dict(case["overrides"]),
        )
        status = _mobility_application_status(record)
        case_results.append(
            {
                "case_id": case["case_id"],
                "profile": case["profile"],
                "description": case["description"],
                "base_parameter_id": case["base_parameter_id"],
                "accepted": status["accepted"],
                "application_status": status,
                "failure_labels": record["failure_labels"],
                "ledger_json": record["metadata"]["ledger_json"],
                "ledger_markdown": record["metadata"]["ledger_markdown"],
            }
        )
        if case["profile"] == "accepted":
            weekday_records.append(record)
    negative_entry = next(entry for entry in case_results if entry["profile"] == "failure")
    summary = {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "seed": seed,
        "summary_kind": "paper_e_application_evaluation",
        "acceptance_criteria": case_results[0]["application_status"]["package_acceptance_thresholds"],
        "threshold_layers": {
            "taxonomy_thresholds": case_results[0]["application_status"]["taxonomy_thresholds"],
            "package_acceptance_thresholds": case_results[0]["application_status"]["package_acceptance_thresholds"],
            "blocking_failure_labels": case_results[0]["application_status"]["blocking_failure_labels"],
            "advisory_failure_labels": case_results[0]["application_status"]["advisory_failure_labels"],
        },
        "cases": case_results,
        "aggregate_stability_summary": {
            "weekday_case_count": len(weekday_records),
            "weekday_all_cases_accepted": all(entry["accepted"] for entry in case_results if entry["profile"] == "accepted"),
            "weekday_min_singular_gap": float(min(record["observables"]["singular_gap"] for record in weekday_records)),
            "weekday_max_coherent_projector_deformation": float(
                max(record["observables"]["coherent_projector_deformation"] for record in weekday_records)
            ),
            "weekday_min_autonomy_horizon": float(min(record["observables"]["autonomy_horizon"] for record in weekday_records)),
            "weekday_max_refinement_span": float(
                max(record["observables"]["numerical_refinement_metrics"]["max_relative_span"] for record in weekday_records)
            ),
            "negative_case_rejected": not negative_entry["accepted"],
            "negative_failure_labels": negative_entry["failure_labels"],
        },
        "notes": [
            "The weekday commute profile is treated as usable only if all fixed local perturbations remain above the declared package floors while avoiding benchmark-local blocking failures.",
            "A global coupling_failure can remain visible in accepted Hyde Park weekday runs because the Paper E package treats it as advisory rather than blocking.",
            "The weekend-night profile is retained as a negative case and is expected to remain rejection-labeled rather than being tuned into acceptance.",
        ],
    }
    json_path = summary_dir / "paper_e_application_summary.json"
    md_path = summary_dir / "paper_e_application_summary.md"
    json_path.write_text(json.dumps(summary, indent=2))
    md_path.write_text(
        "\n".join(
            [
                "# BP_Mobility_Chicago_Corridors Application Evaluation",
                "",
                f"- Seed: `{seed}`",
                f"- Weekday sweep accepted: `{summary['aggregate_stability_summary']['weekday_all_cases_accepted']}`",
                f"- Negative case rejected: `{summary['aggregate_stability_summary']['negative_case_rejected']}`",
                f"- Summary JSON: `results/application/BP_Mobility_Chicago_Corridors/paper_e_application_summary.json`",
                "",
                "## Cases",
            ]
            + [
                f"- `{entry['case_id']}`: accepted=`{entry['accepted']}`, ledger=`{entry['ledger_json']}`"
                for entry in case_results
            ]
        )
    )
    summary["summary_json"] = repo_relative_path(json_path, repo_root)
    summary["summary_markdown"] = repo_relative_path(md_path, repo_root)
    return summary


RUNNERS = {
    "BP_Linear_Two_Block": ("linear", "T1", _linear_two_block),
    "BP_Random_Gap_Ensemble": ("linear", "T2", _random_gap_ensemble),
    "BP_Nearly_Decomposable_Chain": ("linear", "T1/T5", _nearly_decomposable_chain),
    "BP_Windowed_Transport_Flow": ("transport", "T3", _windowed_transport_flow),
    "BP_T3_Window_Sensitivity_Pair": ("transport", "T3", _t3_window_sensitivity_pair),
    "BP_Non_Normal_Shear": ("nonnormal", "T2", _nonnormal_shear),
    "BP_Delay_Coupled_Pair": ("nonnormal", "T2/T3", _delay_coupled_pair),
    "BP_T2_Same_Spectrum_Pair": ("nonnormal", "T2", _t2_same_spectrum_counterexample),
    "BP_Weakly_Nonlinear_Slow_Manifold": ("nonlinear", "T4", _weakly_nonlinear_slow_manifold),
    "BP_T4_Local_Validity_Pair": ("nonlinear", "T4", _t4_local_validity_pair),
    "BP_Noisy_Metastable_Network": ("stochastic", "T5", _noisy_metastable_network),
    "BP_T5_Stochastic_Stress_Pair": ("stochastic", "T5", _t5_stochastic_stress_pair),
    "BP_Mobility_Chicago_Corridors": ("application", "T3/G6", _mobility_chicago_corridors),
    "BP_Mobility_Downtown_Routing_Instability": ("application", "T3/G6", _mobility_downtown_routing_instability),
    "BP_Mobility_NYC_East_Corridor": ("application", "T3/G6", _mobility_nyc_east_corridor),
    "BP_Clickstream_Docs_Funnel": ("application", "T3/G6", _clickstream_docs_funnel),
    "BP_Support_Portal_Funnel": ("application", "T3/G6", _support_navigation_funnel),
    "BP_Workflow_Queue_Funnel": ("application", "T3/G6", _workflow_queue_funnel),
}


def list_benchmarks() -> list[dict]:
    """List registry benchmarks."""

    return [definition.to_dict() for definition in benchmark_definitions()]


def sample_parameters(benchmark_id: str, *, seed: int = 0, parameter_id: str = "reference") -> dict:
    """Return the reference parameter set without writing outputs."""

    _, _, runner = RUNNERS[benchmark_id]
    parameters, _ = _invoke_runner(runner, seed, parameter_id)
    return parameters


def run_reference_benchmark(
    benchmark_id: str,
    *,
    seed: int = 0,
    parameter_id: str = "reference",
    root: str | Path | None = None,
) -> dict:
    """Run a concrete benchmark reference configuration and persist its ledger."""

    repo_root = repository_root(Path(root) if root is not None else None)
    branch, theorem_tier, runner = RUNNERS[benchmark_id]
    if branch == "application":
        return run_application_case(benchmark_id=benchmark_id, seed=seed, parameter_id=parameter_id, root=repo_root)
    started = perf_counter()
    parameters, analysis = _invoke_runner(runner, seed, parameter_id)
    return _persist_record(benchmark_id, branch, theorem_tier, seed, parameter_id, parameters, analysis, repo_root, started)


def main() -> None:
    """CLI for listing and executing reference benchmarks."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List benchmark registry entries")
    run_parser = subparsers.add_parser("run-reference", help="Run a reference benchmark")
    run_parser.add_argument("benchmark_id", choices=sorted(RUNNERS))
    run_parser.add_argument("--seed", type=int, default=0)
    run_parser.add_argument("--parameter-id", default="reference")
    sample_parser = subparsers.add_parser("sample-parameters", help="Print reference parameters")
    sample_parser.add_argument("benchmark_id", choices=sorted(RUNNERS))
    sample_parser.add_argument("--seed", type=int, default=0)
    sample_parser.add_argument("--parameter-id", default="reference")
    args = parser.parse_args()
    if args.command == "list":
        for item in list_benchmarks():
            print(item["benchmark_id"])
    elif args.command == "sample-parameters":
        print(sample_parameters(args.benchmark_id, seed=args.seed, parameter_id=args.parameter_id))
    else:
        print(run_reference_benchmark(args.benchmark_id, seed=args.seed, parameter_id=args.parameter_id))


if __name__ == "__main__":
    main()
