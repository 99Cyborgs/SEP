# Weakly Nonlinear Slow Manifold

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Weakly_Nonlinear_Slow_Manifold`
- branch: `nonlinear`
- tier: `T4`
- implementation_status: `complete`
- evidence_class: `synthetic_nonlinear`
- run_modes: `sample_parameters, run_case`

## Formal System
Weakly nonlinear fast-slow system with a two-dimensional slow oscillator sector and one slaved fast variable.

## Claim Links
- `T4_weakly_nonlinear`: `docs/theorem_notes/T4_weakly_nonlinear.tex` via gate `G4`

## Primary Observables
- `projector_deformation`
- `block_residual_norm`
- `leakage_trajectory`
- `autonomy_horizon`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`nonlinear_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Critical manifold is explicit in the benchmark construction.
- Curvature correction is required; no global nonlinear claim is intended.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Weakly_Nonlinear_Slow_Manifold`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Weakly_Nonlinear_Slow_Manifold`