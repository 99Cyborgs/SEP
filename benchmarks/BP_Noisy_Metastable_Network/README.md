# Noisy Metastable Network

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Noisy_Metastable_Network`
- branch: `stochastic`
- tier: `T5`
- implementation_status: `complete`
- evidence_class: `synthetic_stochastic`
- run_modes: `sample_parameters, run_case`

## Formal System
Four-state stochastic network with two metastable sets and low-probability cross-cluster transitions.

## Claim Links
- `T5_stochastic`: `docs/theorem_notes/T5_stochastic.tex` via gate `G5`

## Primary Observables
- `spectral_gap`
- `block_residual_norm`
- `ensemble_averaged_leakage`
- `leakage_variance`
- `autonomy_horizon`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`stochastic_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Metastable sets are {0,1} and {2,3}.
- Benchmark supports both exact propagator diagnostics and Monte Carlo estimates.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Noisy_Metastable_Network`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Noisy_Metastable_Network`