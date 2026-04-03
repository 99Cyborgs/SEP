# T2 Same Spectrum Pair

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_T2_Same_Spectrum_Pair`
- branch: `nonnormal`
- tier: `T2`
- implementation_status: `complete`
- evidence_class: `synthetic_counterexample`
- run_modes: `sample_parameters, run_case`

## Formal System
Two autonomous linear systems with matched retained slow eigenvalues but different slow-block geometry.

## Claim Links
- `T2_nonnormal`: `docs/theorem_notes/T2_nonnormal.tex` via gate `G2`

## Primary Observables
- `spectral_gap`
- `transient_amplification_score`
- `pseudospectral_proxy`
- `leakage_trajectory`
- `autonomy_horizon`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`negative_control`, claim_status=`counterexample`, acceptance_profile=`same_spectrum_counterexample`, expected_failure_modes=`transient_growth_failure, horizon_failure`
- `matched_normal`: role=`positive_control`, claim_status=`supported`, acceptance_profile=`linear_reference_relaxed`, expected_failure_modes=`none`

## Ground Truth Notes
- The retained slow eigenvalues are held fixed across the pair.
- The paired systems differ in slow-block geometry rather than nominal gap scale.
- The purpose is to expose failure geometry for Paper C, not to close T2.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_T2_Same_Spectrum_Pair`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_T2_Same_Spectrum_Pair`