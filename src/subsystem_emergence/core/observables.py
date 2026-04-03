"""Canonical observable catalog and schema-complete record templates.

The catalog is the repository's stable vocabulary for ledgers, gate criteria,
and reports. Additions here change serialization surfaces across modules.
"""

from __future__ import annotations

from .types import ObservableDefinition


OBSERVABLE_CATALOG = [
    ObservableDefinition(
        key="spectral_gap",
        name="Spectral gap",
        symbol="delta",
        definition="Real-part separation between the retained slow eigenvalues and the leading discarded eigenvalue of an autonomous generator.",
        units="inverse time",
        norm_convention="spectral ordering by descending real part",
        diagnostic_status="primary",
        estimation_procedure="Sort eigenvalues of the generator by real part and subtract the first discarded real part from the last retained real part.",
        acceptance_tolerance=">= 5e-2 for controlled linear reference families",
    ),
    ObservableDefinition(
        key="singular_gap",
        name="Singular gap",
        symbol="Delta",
        definition="Difference between the last retained and first discarded singular values of a finite-time transfer operator.",
        units="dimensionless",
        norm_convention="operator 2-norm singular values",
        diagnostic_status="primary",
        estimation_procedure="Compute an SVD per window and take sigma_m - sigma_{m+1}.",
        acceptance_tolerance=">= 1e-2 for transport reference runs",
    ),
    ObservableDefinition(
        key="projector_deformation",
        name="Projector deformation",
        symbol="epsilon_s",
        definition="Operator-norm deviation between the estimated slow carrier projector and the planted or baseline slow carrier projector.",
        units="dimensionless",
        norm_convention="operator 2-norm",
        diagnostic_status="primary",
        estimation_procedure="Construct projectors from orthonormal bases and evaluate ||P_est - P_ref||_2.",
        acceptance_tolerance="<= 3e-1 for linear validity checks",
    ),
    ObservableDefinition(
        key="coherent_projector_deformation",
        name="Coherent projector deformation",
        symbol="epsilon_c",
        definition="Window-to-window or baseline-to-window deformation of coherent transport carriers.",
        units="dimensionless",
        norm_convention="operator 2-norm",
        diagnostic_status="primary",
        estimation_procedure="Compare coherent source/target projectors across successive windows.",
        acceptance_tolerance="<= 4e-1 for transport reference runs",
    ),
    ObservableDefinition(
        key="block_residual_norm",
        name="Block residual norm",
        symbol="rho",
        definition="Norm of the off-block residual in the reduced carrier dynamics after extracting the block-diagonal approximation.",
        units="inverse time or per window",
        norm_convention="operator 2-norm",
        diagnostic_status="primary",
        estimation_procedure="Project onto the identified carrier, remove block diagonal entries, and evaluate the residual norm.",
        acceptance_tolerance="<= 2.5e-1 on positive reference cases",
    ),
    ObservableDefinition(
        key="leakage_trajectory",
        name="Leakage trajectory",
        symbol="ell",
        definition="Observed finite-horizon leakage sequence for the benchmarked subsystem decomposition.",
        units="dimensionless",
        norm_convention="operator 2-norm for operator leakage or normalized state energy for nonlinear trajectories",
        diagnostic_status="primary",
        estimation_procedure="Evaluate leakage at each sampled time or window using the relevant projector/operator pairing.",
        acceptance_tolerance="path dependent; gate thresholds apply to horizon and fit residuals",
    ),
    ObservableDefinition(
        key="autonomy_horizon",
        name="Autonomy horizon",
        symbol="tau_eta",
        definition="Largest sampled time or window index for which leakage remains below the gate threshold eta.",
        units="time or windows",
        norm_convention="inherits the leakage norm convention",
        diagnostic_status="primary",
        estimation_procedure="Scan the leakage trajectory against eta and retain the largest admissible time.",
        acceptance_tolerance="benchmark dependent; compared against affine prediction",
    ),
    ObservableDefinition(
        key="cross_subsystem_transfer_rate",
        name="Cross-subsystem transfer rate",
        symbol="chi",
        definition="Off-block transport or coupling rate inside the reduced carrier.",
        units="inverse time or per window",
        norm_convention="operator 2-norm",
        diagnostic_status="secondary",
        estimation_procedure="Measure off-block operator norm or per-window coherent transfer in the reduced coordinates.",
        acceptance_tolerance="no universal threshold; inspect relative to rho",
    ),
    ObservableDefinition(
        key="reduced_model_forecast_error",
        name="Reduced model forecast error",
        symbol="E_red",
        definition="Mismatch between full projected evolution and reduced-model evolution on the identified carrier.",
        units="dimensionless",
        norm_convention="operator 2-norm averaged over forecast times",
        diagnostic_status="secondary",
        estimation_procedure="Compare projected full propagators against reduced propagators over the benchmark time grid.",
        acceptance_tolerance="<= 2.5e-1 on positive reference runs",
    ),
    ObservableDefinition(
        key="transient_amplification_score",
        name="Transient amplification score",
        symbol="Gamma_T",
        definition="Finite-horizon semigroup amplification beyond spectral abscissa decay.",
        units="dimensionless",
        norm_convention="operator 2-norm",
        diagnostic_status="diagnostic",
        estimation_procedure="Evaluate sup_t ||e^{tA}|| exp(-alpha(A)t) on the benchmark horizon.",
        acceptance_tolerance="> 1.5 is treated as nonnormal risk",
    ),
    ObservableDefinition(
        key="ensemble_averaged_leakage",
        name="Ensemble averaged leakage",
        symbol="E[ell]",
        definition="Mean leakage across stochastic trajectory or parameter ensembles.",
        units="dimensionless",
        norm_convention="inherits branch-specific leakage norm",
        diagnostic_status="secondary",
        estimation_procedure="Average leakage over ensemble members or bootstrap replicates.",
        acceptance_tolerance="stochastic gate dependent",
    ),
    ObservableDefinition(
        key="leakage_variance",
        name="Leakage variance",
        symbol="Var[ell]",
        definition="Variance of leakage across an ensemble or stochastic bootstrap.",
        units="dimensionless squared",
        norm_convention="inherits branch-specific leakage norm",
        diagnostic_status="secondary",
        estimation_procedure="Compute sample variance across trajectories or replicates.",
        acceptance_tolerance="<= 8e-2 on the reference stochastic family",
    ),
    ObservableDefinition(
        key="affine_law_regression_coefficients",
        name="Affine law regression coefficients",
        symbol="beta",
        definition="Estimated coefficients for candidate leakage laws L1, L2, and L3.",
        units="mixed coefficients",
        norm_convention="least-squares fit on leakage observables",
        diagnostic_status="secondary",
        estimation_procedure="Fit leakage against epsilon_s, rho tau, curvature, and transient-growth proxies with held-out evaluation.",
        acceptance_tolerance="selected law should improve held-out RMSE over weaker competitors when the extension is justified",
    ),
    ObservableDefinition(
        key="transportability_metrics",
        name="Transportability metrics",
        symbol="Theta",
        definition="Metrics comparing coherent transport performance against frozen or coarse surrogate models.",
        units="dimensionless",
        norm_convention="ratio or relative error conventions documented per benchmark",
        diagnostic_status="diagnostic",
        estimation_procedure="Compare coherent benchmark metrics against autonomous surrogates or held-out parameter shifts.",
        acceptance_tolerance="> 0.6 on positive transport cases",
    ),
    ObservableDefinition(
        key="coordinate_sensitivity_metrics",
        name="Coordinate sensitivity metrics",
        symbol="Xi",
        definition="Sensitivity of benchmark observables to admissible coordinate transforms or basis changes.",
        units="dimensionless",
        norm_convention="relative observable change and projector back-transformation error",
        diagnostic_status="diagnostic",
        estimation_procedure="Apply random orthogonal changes of coordinates, recompute observables, and summarize the induced relative variation.",
        acceptance_tolerance="<= 3.5e-1 on accepted subsystem claims",
    ),
    ObservableDefinition(
        key="numerical_refinement_metrics",
        name="Numerical refinement metrics",
        symbol="R_num",
        definition="Variation of benchmark observables across refinement levels such as time-step, grid, or ensemble size.",
        units="dimensionless",
        norm_convention="relative span across refinement ladders",
        diagnostic_status="diagnostic",
        estimation_procedure="Repeat the analysis at at least two refinement levels and report the relative spread of core observables.",
        acceptance_tolerance="<= 2e-1 on accepted claims",
    ),
]


def observable_catalog() -> list[ObservableDefinition]:
    """Return a shallow copy of the canonical observable catalog."""

    return OBSERVABLE_CATALOG.copy()


def observable_catalog_dicts() -> list[dict[str, str | None]]:
    """Return the catalog in JSON-serializable form, preserving declaration order."""

    return [item.to_dict() for item in OBSERVABLE_CATALOG]


def empty_observables() -> dict[str, object]:
    """Return a schema-complete observable record with explicit null placeholders."""

    return {definition.key: None for definition in OBSERVABLE_CATALOG}
