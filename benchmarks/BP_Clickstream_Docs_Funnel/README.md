# Clickstream Docs Funnel

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Clickstream_Docs_Funnel`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- evidence_class: `application_repository_fixture`
- run_modes: `sample_parameters, run_case`

## Formal System
Row-stochastic page-to-page clickstream operators derived from a bundled documentation navigation fixture.

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
- `named_flow_fixture`: `benchmarks/BP_Clickstream_Docs_Funnel/data/docs_navigation_funnel_q1_2026.json`, source_archive=`docs_navigation_funnel_q1_2026.json`

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`application_navigation_reference`, expected_failure_modes=`none`
- `negative_detour`: role=`negative_control`, claim_status=`rejected`, acceptance_profile=`expected_failure_control`, expected_failure_modes=`carrier_failure, coupling_failure`

## Ground Truth Notes
- This is a bounded cross-domain application fixture, not a public-data theorem claim.
- The reference case is intended to show stable coherent structure outside mobility.
- The negative detour case is retained to preserve explicit rejection evidence.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Clickstream_Docs_Funnel`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Clickstream_Docs_Funnel`