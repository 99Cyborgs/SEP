# Delay Coupled Pair

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Delay_Coupled_Pair`
- branch: `nonnormal`
- tier: `T2/T3`
- implementation_status: `surrogate`
- evidence_class: `surrogate_delay`
- run_modes: `sample_parameters, run_case`

## Formal System
x'(t) = A0 x(t) + A_tau x(t - tau) with sampled history-propagator diagnostics.

## Claim Links
- `T2_nonnormal`: `docs/theorem_notes/T2_nonnormal.tex` via gate `G2`
- `T3_finite_time_transport`: `docs/theorem_notes/T3_finite_time_transport.tex` via gate `G3`

## Primary Observables
- `transient_amplification_score`
- `block_residual_norm`
- `leakage_trajectory`
- `autonomy_horizon`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`qualified`, acceptance_profile=`delay_surrogate_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Two-module partition is planted.
- The physical state stays two-dimensional; the history snapshot space is diagnostic only.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Delay_Coupled_Pair`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Delay_Coupled_Pair`