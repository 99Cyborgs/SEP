# BP Linear Two Block

## Formal System Definition
An 8-dimensional autonomous linear ODE with a planted 4-dimensional slow carrier and two 2-dimensional subsystem blocks:

`L = Q^T (diag(L_slow, L_fast) + R_slow) Q`

where `L_fast` is strongly stable, `L_slow` is weakly damped, and `R_slow` is an off-block perturbation controlling `rho`.

## Parameter Ranges
- `gap`: `0.5` to `2.0`
- `rho`: `0.01` to `0.12`
- `perturbation`: `0.0` to `0.08`
- `times`: `0` to `8`

## Ground Truth Notes
- Planted slow carrier is known before mixing.
- Ground-truth subsystem partition is `2 + 2` inside the slow carrier.
- Coordinate sensitivity is tested with orthogonal changes of basis only.

## Theorem Tier
`T1`

## Expected Failure Modes
- `gap_failure`
- `carrier_failure`
- `coupling_failure`
- `numerical_artifact_failure`

## Reference Commands
- `python benchmarks/BP_Linear_Two_Block/generate.py`
- `python benchmarks/BP_Linear_Two_Block/run_reference.py`
- `python benchmarks/BP_Linear_Two_Block/figure_recipe.py`
