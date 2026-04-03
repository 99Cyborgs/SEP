# Windowed Transport Flow

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_Windowed_Transport_Flow`
- branch: `transport`
- tier: `T3`
- implementation_status: `complete`
- evidence_class: `synthetic_transport`
- run_modes: `sample_parameters, run_case`

## Formal System
Windowed row-stochastic transport flow with two coherent lobes on a ring.

## Claim Links
- `T3_finite_time_transport`: `docs/theorem_notes/T3_finite_time_transport.tex` via gate `G3`

## Primary Observables
- `singular_gap`
- `coherent_projector_deformation`
- `block_residual_norm`
- `leakage_trajectory`
- `autonomy_horizon`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`reference`, claim_status=`supported`, acceptance_profile=`transport_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Two coherent lobes persist while drifting across windows.
- Frozen autonomous surrogates are intentionally weaker than the coherent-window treatment.
- The accepted positive reference uses moderate drift rather than a nearly stationary flow.
- Parameter regimes that preserve singular gaps but destroy window-to-window carrier alignment are treated as negative transport evidence.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_Windowed_Transport_Flow`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_Windowed_Transport_Flow`