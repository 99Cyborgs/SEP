# Nearly Decomposable Chain

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Nearly_Decomposable_Chain`
- branch: `linear`
- tier: `T1/T5`
- implementation_status: `complete`
- evidence_class: `synthetic_markov`
- run_modes: `sample_parameters, run_case`

## Formal System
Four-state row-stochastic chain with two metastable clusters and analysis on the generator P - I.

## Claim Links
- `T1_linear_autonomous`: `docs/theorem_notes/T1_linear_autonomous.tex` via gate `G1`
- `T5_stochastic`: `docs/theorem_notes/T5_stochastic.tex` via gate `G5`

## Primary Observables
- `spectral_gap`
- `block_residual_norm`
- `leakage_trajectory`
- `autonomy_horizon`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`linear_reference_relaxed`, expected_failure_modes=`none`

## Ground Truth Notes
- Clusters are planted as {0,1} and {2,3}.
- Slow carrier corresponds to the nearly conserved cluster modes.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Nearly_Decomposable_Chain`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Nearly_Decomposable_Chain`