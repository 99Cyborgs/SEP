# T3 Window Sensitivity Pair

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_T3_Window_Sensitivity_Pair`
- branch: `transport`
- tier: `T3`
- implementation_status: `complete`
- evidence_class: `synthetic_counterexample`
- run_modes: `sample_parameters, run_case`

## Formal System
Paired windowed row-stochastic transport flows with matched geometry but different drift persistence across analysis windows.

## Claim Links
- `T3_finite_time_transport`: `docs/theorem_notes/T3_finite_time_transport.tex` via gate `G3`

## Primary Observables
- `singular_gap`
- `coherent_projector_deformation`
- `autonomy_horizon`
- `transportability_metrics`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`negative_control`, claim_status=`counterexample`, acceptance_profile=`transport_counterexample`, expected_failure_modes=`carrier_failure, horizon_failure`
- `matched_positive`: role=`positive_control`, claim_status=`supported`, acceptance_profile=`transport_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Both branches use the same ring transport construction and coarse subsystem partition.
- The positive branch preserves coherent carriers across adjacent windows strongly enough to beat the frozen surrogate.
- The fast-drift branch keeps plausible transport structure while degrading coherent persistence and regrouping stability.
- The pair is intended as Paper B protocol evidence, not as a general cocycle theorem.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_T3_Window_Sensitivity_Pair`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_T3_Window_Sensitivity_Pair`