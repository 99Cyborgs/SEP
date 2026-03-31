# BP Random Gap Ensemble

## Formal System Definition
An ensemble of low-dimensional linear systems with matched nominal gap scales but different nonnormal structure. Half of the ensemble is close to normal, half is intentionally nonnormal.

## Parameter Ranges
- gap: `0.05` to `0.30`
- condition number / nonnormality: normal branch near `1`, nonnormal branch intentionally elevated
- sampled times: `0` to `5`

## Ground Truth Notes
- Slow subsystem count is planted at `2`.
- The ensemble is designed to test whether pure affine laws fail when transient growth is introduced without changing spectral order in a misleading way.

## Theorem Tier
`T1/T2`

## Expected Failure Modes
- `gap_failure`
- `transient_growth_failure`
- `horizon_failure`

## Reference Commands
- `python benchmarks/BP_Random_Gap_Ensemble/generate.py`
- `python benchmarks/BP_Random_Gap_Ensemble/run_reference.py`
- `python benchmarks/BP_Random_Gap_Ensemble/figure_recipe.py`
