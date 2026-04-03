# T4 Local Validity Pair

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_T4_Local_Validity_Pair`
- branch: `nonlinear`
- tier: `T4`
- implementation_status: `complete`
- evidence_class: `synthetic_counterexample`
- run_modes: `sample_parameters, run_case`

## Formal System
Paired weakly nonlinear fast-slow systems with the same structural template but different local-validity posture.

## Claim Links
- `T4_weakly_nonlinear`: `docs/theorem_notes/T4_weakly_nonlinear.tex` via gate `G4`

## Primary Observables
- `projector_deformation`
- `leakage_trajectory`
- `autonomy_horizon`
- `local_validity_metrics`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`negative_control`, claim_status=`counterexample`, acceptance_profile=`local_validity_counterexample`, expected_failure_modes=`carrier_failure, coupling_failure, horizon_failure`
- `matched_local`: role=`positive_control`, claim_status=`supported`, acceptance_profile=`nonlinear_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Both branches use the same three-dimensional fast-slow template.
- The matched local branch stays closer to the slaved fast-variable relation and keeps the local-validity margin positive.
- The amplitude-breakdown branch increases anchor drift and fast slaving defect without claiming a global nonlinear instability theorem.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_T4_Local_Validity_Pair`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_T4_Local_Validity_Pair`