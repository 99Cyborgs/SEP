# T5 Stochastic Stress Pair

This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.

## Family Contract
- benchmark_id: `BP_T5_Stochastic_Stress_Pair`
- branch: `stochastic`
- tier: `T5`
- implementation_status: `complete`
- evidence_class: `synthetic_counterexample`
- run_modes: `sample_parameters, run_case`

## Formal System
Paired four-state metastable networks with identical transition structure and different Monte Carlo sample counts.

## Claim Links
- `T5_stochastic`: `docs/theorem_notes/T5_stochastic.tex` via gate `G5`

## Primary Observables
- `ensemble_averaged_leakage`
- `leakage_variance`
- `autonomy_horizon`
- `stochastic_uncertainty_metrics`

## Fixtures
- `synthetic_generator`: runtime-generated benchmark fixture

## Cases
- `reference`: role=`negative_control`, claim_status=`counterexample`, acceptance_profile=`stochastic_stress_counterexample`, expected_failure_modes=`horizon_failure, numerical_artifact_failure`
- `matched_metastable`: role=`positive_control`, claim_status=`supported`, acceptance_profile=`stochastic_reference`, expected_failure_modes=`none`

## Ground Truth Notes
- Both branches keep the same metastable network and source-state partition.
- The matched branch uses enough trajectories to keep bootstrap width and confidence-bounded horizon stable.
- The sample-stress branch widens uncertainty and degrades the confidence-bounded horizon without introducing a new stochastic model class.

## Canonical Commands
- `python -m subsystem_emergence.benchmarking run-case BP_T5_Stochastic_Stress_Pair`
- `python -m subsystem_emergence.benchmarking sample-parameters BP_T5_Stochastic_Stress_Pair`