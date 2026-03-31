# Observable Definitions

The machine-readable source of truth is [observables/catalog.json](/G:/GitHub/incubate/Subsystem%20Emergence%20Program/observables/catalog.json). This document explains the same observables in protocol form.

## Primary Observables

### Spectral gap

For autonomous systems,

```math
\delta = \Re \lambda_m - \Re \lambda_{m+1}
```

after ordering eigenvalues by descending real part.

### Singular gap

For finite-time transport,

```math
\Delta = \sigma_m(T) - \sigma_{m+1}(T).
```

### Projector deformation

```math
\varepsilon_s = \|P_{\mathrm{est}} - P_{\mathrm{ref}}\|_2.
```

### Coherent projector deformation

```math
\varepsilon_c = \|\Pi_{q+1} - \Pi_q\|_2
```

or against a baseline coherent carrier where appropriate.

### Reduced off-block residual

With reduced carrier operator `A = D + R`,

```math
\rho = \|R\|_2.
```

### Leakage trajectory

Autonomous:

```math
\ell_i(t) = \|(I - Q_i)e^{tL}Q_i\|_2,
\qquad
\ell(t) = \max_i \ell_i(t).
```

Finite-time transport:

```math
\ell(q) = \|(I - \Pi_q)T_{q-1}\cdots T_0\Pi_0\|_2.
```

Weakly nonlinear:

```math
\ell(t) = \frac{\|(I-P_t)x(t)\|_2}{\|x(t)\|_2 + 10^{-12}}.
```

### Autonomy horizon

```math
\tau_\eta = \sup\{\tau : \ell(\tau) \le \eta\}.
```

## Secondary Observables

- `cross_subsystem_transfer_rate`: off-block reduced coupling.
- `reduced_model_forecast_error`: projected full evolution versus reduced evolution.
- `ensemble_averaged_leakage`: stochastic or ensemble mean leakage.
- `leakage_variance`: stochastic or ensemble leakage variance.
- `affine_law_regression_coefficients`: coefficients for L1, L2, and L3.

## Diagnostic Observables

- `transient_amplification_score`: nonnormality correction proxy.
- `transportability_metrics`: coherent-vs-frozen and continuation-style stress tests.
- `coordinate_sensitivity_metrics`: admissible basis-change robustness.
- `numerical_refinement_metrics`: stability across refinement levels.
