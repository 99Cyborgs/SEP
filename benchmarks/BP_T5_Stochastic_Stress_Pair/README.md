# BP T5 Stochastic Stress Pair

## Formal System Definition
A paired stochastic benchmark using the same four-state metastable transition structure as `BP_Noisy_Metastable_Network`, but comparing an adequately sampled branch against a sample-stressed branch.

## Parameter Sets
- `reference`: `sample_stress`
- `matched_metastable`: accepted stochastic control branch

## Intended Use
- harden Paper D with explicit uncertainty-limited failure geometry
- isolate sample stress as the source of wider bootstrap bands and weaker confidence-bounded horizons
- keep the underlying metastable model fixed so the comparison stays attributable

## Expected Reading
- `matched_metastable` should keep a narrow bootstrap band and a materially positive confidence-bounded horizon
- `sample_stress` should widen the bootstrap band, worsen estimation error, and reduce the confidence-bounded horizon

## Reference Commands
- `python benchmarks/BP_T5_Stochastic_Stress_Pair/generate.py`
- `python benchmarks/BP_T5_Stochastic_Stress_Pair/run_reference.py`
- `python benchmarks/BP_T5_Stochastic_Stress_Pair/run_matched_metastable.py`
- `python benchmarks/BP_T5_Stochastic_Stress_Pair/figure_recipe.py`
