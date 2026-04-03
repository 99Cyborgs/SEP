# Random Gap Ensemble

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Random_Gap_Ensemble`
- branch: `linear`
- tier: `T1/T2`
- implementation_status: `complete`
- evidence_class: `synthetic_ensemble`
- run_modes: `sample_parameters, run_case`

## Formal System
Ensemble of linear matrices with matched slow_count and deliberately varied nonnormality.

## Claim Links
- `T1_linear_autonomous`: `docs/theorem_notes/T1_linear_autonomous.tex` via gate `G1`
- `T2_nonnormal`: `docs/theorem_notes/T2_nonnormal.tex` via gate `G2`

## Primary Observables
- `spectral_gap`
- `projector_deformation`
- `block_residual_norm`
- `transient_amplification_score`
- `leakage_trajectory`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`linear_reference_relaxed`, expected_failure_modes=`none`

## Ground Truth Notes
- Slow subsystem count is planted at two.
- Normal and nonnormal branches are both represented.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Random_Gap_Ensemble`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Random_Gap_Ensemble`