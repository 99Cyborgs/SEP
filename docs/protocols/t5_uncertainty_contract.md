# T5 Uncertainty Contract

## Purpose
Interpret `T5` evidence as a probabilistic finite-sample statement rather than a theorem with uniform concentration guarantees.

## What Is Held Fixed
- the four-state metastable transition structure
- the source-state partition `{0, 1}`
- the leakage threshold and time horizon

## What Is Varied
- Monte Carlo sample count
- the resulting bootstrap width, estimation error, and confidence-bounded horizon

## Diagnostic Contract
`T5` evidence bundles should now expose:
- `bootstrap_width`
- `ensemble_mean_leakage`
- `metastability_score`
- `effective_sample_size`
- `estimated_horizon`
- `confidence_bounded_horizon`
- `estimation_error_proxy`

`BP_Noisy_Metastable_Network` is the accepted stochastic reference. `BP_T5_Stochastic_Stress_Pair/reference` is retained as sample-stress evidence and is reported in `G5` without becoming gate-fatal.
