# BP Non Normal Shear

## Formal System Definition
A small nonnormal linear system with a slow two-dimensional shear block and a fast two-dimensional stable block. The spectrum alone suggests stability, while the slow shear creates transient amplification.

## Parameter Ranges
- shear amplitude: `1.0` to `5.0`
- slow-fast coupling: `0.01` to `0.10`
- sampled times: `0` to `6`

## Ground Truth Notes
- The slow subsystem partition is planted.
- Transient amplification is known to be the dominant threat model.

## Theorem Tier
`T2`

## Expected Failure Modes
- `transient_growth_failure`
- `horizon_failure`

## Reference Commands
- `python benchmarks/BP_Non_Normal_Shear/generate.py`
- `python benchmarks/BP_Non_Normal_Shear/run_reference.py`
- `python benchmarks/BP_Non_Normal_Shear/figure_recipe.py`
