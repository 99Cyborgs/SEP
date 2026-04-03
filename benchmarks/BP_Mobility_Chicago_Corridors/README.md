# Mobility Chicago Corridors

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Mobility_Chicago_Corridors`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- evidence_class: `application_real_data`
- run_modes: `sample_parameters, run_case, validation_matrix`

## Formal System
Row-stochastic station-to-station mobility operators derived from a bundled Hyde Park slice of Divvy January 2024 trip history.

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
- `named_flow_fixture`: `benchmarks/BP_Mobility_Chicago_Corridors/data/divvy_hyde_park_jan2024.json`, source_archive=`202401-divvy-tripdata.zip`

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`application_mobility_reference`, expected_failure_modes=`none`
- `weekday_pseudocount_tight`: role=`reference_variant`, claim_status=`supported`, acceptance_profile=`application_mobility_reference`, expected_failure_modes=`none`
- `weekday_pseudocount_loose`: role=`reference_variant`, claim_status=`supported`, acceptance_profile=`application_mobility_reference`, expected_failure_modes=`none`
- `weekday_three_station_corridor`: role=`reference_variant`, claim_status=`supported`, acceptance_profile=`application_mobility_reference`, expected_failure_modes=`none`
- `weekday_window_coarsened`: role=`reference_variant`, claim_status=`supported`, acceptance_profile=`application_mobility_reference`, expected_failure_modes=`none`
- `negative_weekend`: role=`negative_control`, claim_status=`rejected`, acceptance_profile=`expected_failure_control`, expected_failure_modes=`carrier_failure, numerical_artifact_failure`

## Ground Truth Notes
- The benchmark is real-data and case-study-only; no new universal theorem is claimed.
- The reference case is usable because corridor structure is interpretable and reproducible from a bundled fixture.
- The weekend-night case is retained as an instructive negative application slice.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Mobility_Chicago_Corridors`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Mobility_Chicago_Corridors`