# Linear Two Block

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Linear_Two_Block`
- branch: `linear`
- tier: `T1`
- implementation_status: `complete`
- evidence_class: `synthetic_constructive`
- run_modes: `sample_parameters, run_case`

## Formal System
Q^T (diag(L_slow, L_fast) + R_slow) Q with planted 4-dimensional slow carrier.

## Claim Links
- `T1_linear_autonomous`: `docs/theorem_notes/T1_linear_autonomous.tex` via gate `G1`

## Primary Observables
- `spectral_gap`
- `projector_deformation`
- `block_residual_norm`
- `leakage_trajectory`
- `autonomy_horizon`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`linear_reference_strict`, expected_failure_modes=`none`

## Ground Truth Notes
- Planted slow carrier is known before coordinate mixing.
- Subsystem partition is fixed at 2 + 2 within the slow carrier.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Linear_Two_Block`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Linear_Two_Block`