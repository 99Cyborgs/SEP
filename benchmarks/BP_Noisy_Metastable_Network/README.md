# BP Noisy Metastable Network

## Formal System Definition
A four-state stochastic network with two metastable state sets and low-probability cross transitions. The benchmark supports exact propagator calculations, Monte Carlo estimation, bootstrap confidence intervals, and a minimal MSM summary.

## Parameter Ranges
- state count: fixed at `4` for the reference path
- trajectories: `200` to `2000`
- sampled steps: `0` to `12`

## Ground Truth Notes
- Metastable state sets are `{0,1}` and `{2,3}`.
- The benchmark is the repository's inspectable Markov-state-style stochastic case.

## Theorem Tier
`T5`

## Expected Failure Modes
- `gap_failure`
- `horizon_failure`
- `numerical_artifact_failure`

## Reference Commands
- `python benchmarks/BP_Noisy_Metastable_Network/generate.py`
- `python benchmarks/BP_Noisy_Metastable_Network/run_reference.py`
- `python benchmarks/BP_Noisy_Metastable_Network/figure_recipe.py`
