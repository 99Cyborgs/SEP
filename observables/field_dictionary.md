# Observable Field Dictionary

This dictionary mirrors [catalog.json](/G:/GitHub/incubate/Subsystem%20Emergence%20Program/observables/catalog.json) and the package-level observable catalog.

| key | symbol | status | meaning |
| --- | --- | --- | --- |
| `spectral_gap` | `delta` | primary | Slow-fast spectral separation in autonomous systems. |
| `singular_gap` | `Delta` | primary | Retained-discarded singular separation in finite-time transport. |
| `projector_deformation` | `epsilon_s` | primary | Slow carrier deformation relative to baseline. |
| `coherent_projector_deformation` | `epsilon_c` | primary | Coherent carrier deformation across windows. |
| `block_residual_norm` | `rho` | primary | Off-block coupling inside the reduced carrier. |
| `leakage_trajectory` | `ell` | primary | Observed leakage sequence on the sampled horizon. |
| `autonomy_horizon` | `tau_eta` | primary | Last sampled horizon before leakage crosses `eta`. |
| `cross_subsystem_transfer_rate` | `chi` | secondary | Reduced-model cross-subsystem coupling or transfer. |
| `reduced_model_forecast_error` | `E_red` | secondary | Reduced-model mismatch against projected full evolution. |
| `transient_amplification_score` | `Gamma_T` | diagnostic | Semigroup amplification beyond spectral-abscissa decay. |
| `ensemble_averaged_leakage` | `E[ell]` | secondary | Ensemble mean leakage. |
| `leakage_variance` | `Var[ell]` | secondary | Ensemble leakage variance. |
| `affine_law_regression_coefficients` | `beta` | secondary | Coefficients for L1, L2, and L3 law fits. |
| `transportability_metrics` | `Theta` | diagnostic | Performance relative to frozen, coarse, or continuation surrogates. |
| `coordinate_sensitivity_metrics` | `Xi` | diagnostic | Robustness against admissible coordinate changes. |
| `numerical_refinement_metrics` | `R_num` | diagnostic | Relative spread across refinement levels. |
