# Benchmark Catalog

Generated from `benchmarks/registry.yaml`.

## BP_Linear_Two_Block
- title: `Linear Two Block`
- branch: `linear`
- tier: `T1`
- implementation_status: `complete`
- claims: `T1_linear_autonomous`
- cases: `reference`

## BP_Random_Gap_Ensemble
- title: `Random Gap Ensemble`
- branch: `linear`
- tier: `T1/T2`
- implementation_status: `complete`
- claims: `T1_linear_autonomous, T2_nonnormal`
- cases: `reference`

## BP_Nearly_Decomposable_Chain
- title: `Nearly Decomposable Chain`
- branch: `linear`
- tier: `T1/T5`
- implementation_status: `complete`
- claims: `T1_linear_autonomous, T5_stochastic`
- cases: `reference`

## BP_Windowed_Transport_Flow
- title: `Windowed Transport Flow`
- branch: `transport`
- tier: `T3`
- implementation_status: `complete`
- claims: `T3_finite_time_transport`
- cases: `reference`

## BP_T3_Window_Sensitivity_Pair
- title: `T3 Window Sensitivity Pair`
- branch: `transport`
- tier: `T3`
- implementation_status: `complete`
- claims: `T3_finite_time_transport`
- cases: `reference, matched_positive`

## BP_Non_Normal_Shear
- title: `Non Normal Shear`
- branch: `nonnormal`
- tier: `T2`
- implementation_status: `complete`
- claims: `T2_nonnormal`
- cases: `reference`

## BP_Delay_Coupled_Pair
- title: `Delay Coupled Pair`
- branch: `nonnormal`
- tier: `T2/T3`
- implementation_status: `surrogate`
- claims: `T2_nonnormal, T3_finite_time_transport`
- cases: `reference`

## BP_T2_Same_Spectrum_Pair
- title: `T2 Same Spectrum Pair`
- branch: `nonnormal`
- tier: `T2`
- implementation_status: `complete`
- claims: `T2_nonnormal`
- cases: `reference, matched_normal`

## BP_Weakly_Nonlinear_Slow_Manifold
- title: `Weakly Nonlinear Slow Manifold`
- branch: `nonlinear`
- tier: `T4`
- implementation_status: `complete`
- claims: `T4_weakly_nonlinear`
- cases: `reference`

## BP_T4_Local_Validity_Pair
- title: `T4 Local Validity Pair`
- branch: `nonlinear`
- tier: `T4`
- implementation_status: `complete`
- claims: `T4_weakly_nonlinear`
- cases: `reference, matched_local`

## BP_Noisy_Metastable_Network
- title: `Noisy Metastable Network`
- branch: `stochastic`
- tier: `T5`
- implementation_status: `complete`
- claims: `T5_stochastic`
- cases: `reference`

## BP_T5_Stochastic_Stress_Pair
- title: `T5 Stochastic Stress Pair`
- branch: `stochastic`
- tier: `T5`
- implementation_status: `complete`
- claims: `T5_stochastic`
- cases: `reference, matched_metastable`

## BP_Mobility_Chicago_Corridors
- title: `Mobility Chicago Corridors`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- claims: `T3_finite_time_transport, G6_application_identifiability`
- cases: `reference, weekday_pseudocount_tight, weekday_pseudocount_loose, weekday_three_station_corridor, weekday_window_coarsened, negative_weekend`

## BP_Mobility_Downtown_Routing_Instability
- title: `Mobility Downtown Routing Instability`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- claims: `T3_finite_time_transport, G6_application_identifiability`
- cases: `reference`

## BP_Mobility_NYC_East_Corridor
- title: `Mobility NYC East Corridor`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- claims: `T3_finite_time_transport, G6_application_identifiability`
- cases: `reference`

## BP_Clickstream_Docs_Funnel
- title: `Clickstream Docs Funnel`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- claims: `T3_finite_time_transport, G6_application_identifiability`
- cases: `reference, negative_detour`

## BP_Support_Portal_Funnel
- title: `Support Portal Funnel`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- claims: `T3_finite_time_transport, G6_application_identifiability`
- cases: `reference, negative_detour`

## BP_Workflow_Queue_Funnel
- title: `Workflow Queue Funnel`
- branch: `application`
- tier: `T3/G6`
- implementation_status: `complete`
- claims: `T3_finite_time_transport, G6_application_identifiability`
- cases: `reference, negative_detour`

## Claims
- `G6_application_identifiability`: `docs/protocols/external_application_evidence.md` via gate `G6`
- `T1_linear_autonomous`: `docs/theorem_notes/T1_linear_autonomous.tex` via gate `G1`
- `T2_nonnormal`: `docs/theorem_notes/T2_nonnormal.tex` via gate `G2`
- `T3_finite_time_transport`: `docs/theorem_notes/T3_finite_time_transport.tex` via gate `G3`
- `T4_weakly_nonlinear`: `docs/theorem_notes/T4_weakly_nonlinear.tex` via gate `G4`
- `T5_stochastic`: `docs/theorem_notes/T5_stochastic.tex` via gate `G5`