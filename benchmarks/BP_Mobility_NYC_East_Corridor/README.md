# Mobility NYC East Corridor

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Mobility_NYC_East_Corridor`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- evidence_class: `application_real_data`
- run_modes: `sample_parameters, run_case`

## Formal System
Row-stochastic station-to-station mobility operators derived from a bundled Manhattan east-side slice of Citi Bike January 2024 trip history.

## Claim Links
- `T3_finite_time_transport`: `docs/theorem_notes/T3_finite_time_transport.tex` via gate `G3`
- `G6_application_identifiability`: `docs/protocols/external_application_evidence.md` via gate `G6`

## Primary Observables
- `singular_gap`
- `coherent_projector_deformation`
- `block_residual_norm`
- `leakage_trajectory`
- `autonomy_horizon`

## Fixtures
- `named_flow_fixture`: `benchmarks/BP_Mobility_NYC_East_Corridor/data/citibike_east_corridor_jan2024.json`, source_archive=`202401-citibike-tripdata.zip`

## Cases
- `reference`: role=`negative_control`, claim_status=`rejected`, acceptance_profile=`expected_failure_control`, expected_failure_modes=`carrier_failure, coupling_failure`

## Ground Truth Notes
- The benchmark is real-data and intended as a mixed external application case.
- The case shows stable refinement and substantial traffic, but not carrier stability or weak coupling.
- The benchmark broadens the external mobility evidence set beyond the Chicago Divvy archive without claiming a second accepted application case.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Mobility_NYC_East_Corridor`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Mobility_NYC_East_Corridor`