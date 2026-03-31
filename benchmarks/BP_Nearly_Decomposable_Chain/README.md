# BP Nearly Decomposable Chain

## Formal System Definition
A four-state nearly decomposable Markov chain with two planted metastable clusters. The analysis is performed on the generator `P - I` so the slow subspace is diagnosed spectrally in the autonomous sense while the chain remains interpretable as a stochastic benchmark.

## Parameter Ranges
- intra-cluster retention: `0.85` to `0.95`
- inter-cluster transfer: `0.01` to `0.08`
- sampled times: `0` to `18`

## Ground Truth Notes
- Ground truth clusters are `{0,1}` and `{2,3}`.
- The benchmark doubles as a bridge between T1 and T5 because the slow carrier is metastable.

## Theorem Tier
`T1/T5`

## Expected Failure Modes
- `gap_failure`
- `coupling_failure`
- `coordinate_artifact_failure`

## Reference Commands
- `python benchmarks/BP_Nearly_Decomposable_Chain/generate.py`
- `python benchmarks/BP_Nearly_Decomposable_Chain/run_reference.py`
- `python benchmarks/BP_Nearly_Decomposable_Chain/figure_recipe.py`
