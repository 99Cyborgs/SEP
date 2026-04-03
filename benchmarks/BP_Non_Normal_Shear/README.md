# Non Normal Shear

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Non_Normal_Shear`
- branch: `nonnormal`
- tier: `T2`
- implementation_status: `complete`
- evidence_class: `synthetic_nonnormal`
- run_modes: `sample_parameters, run_case`

## Formal System
Two-dimensional slow shear block weakly coupled to a fast stable block.

## Claim Links
- `T2_nonnormal`: `docs/theorem_notes/T2_nonnormal.tex` via gate `G2`

## Primary Observables
- `spectral_gap`
- `transient_amplification_score`
- `block_residual_norm`
- `leakage_trajectory`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`nonnormal_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Slow subsystem partition is planted.
- Transient amplification is intentionally strong despite stable eigenvalues.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Non_Normal_Shear`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Non_Normal_Shear`