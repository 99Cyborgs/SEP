# BP Weakly Nonlinear Slow Manifold

## Formal System Definition
A three-dimensional weakly nonlinear fast-slow system with a two-dimensional slow oscillator-like sector and a slaved fast variable. Leakage is measured as normalized state energy outside the instantaneous slow carrier estimated from local Jacobians.

## Parameter Ranges
- `epsilon`: `0.05` to `0.12`
- slow coupling `rho`: `0.03` to `0.10`
- sampled times: `0` to `12`

## Ground Truth Notes
- The critical manifold is explicit in the benchmark construction.
- Curvature corrections are required; this benchmark is not meant to certify a global nonlinear theorem.
- The accepted reference case is local: deformation is tracked between adjacent instantaneous carriers, not against the initial carrier over the entire horizon.
- The fast coordinate must remain slaved throughout the run; large-amplitude excursions are treated as outside the accepted T4 neighborhood.

## Accepted Reference Case
- `epsilon = 0.08`
- slow coupling `rho = 0.07`
- initial state `[1.0, -0.6, 0.3]`
- Gate-facing deformation uses adjacent projector drift, with anchor-to-initial drift retained only as a diagnostic.

## Excluded Regimes
- Large initial fast offsets that keep leakage small but force long-horizon drift away from the local carrier anchor are not accepted as positive T4 evidence.
- Claims based on global persistence of a single fixed carrier are out of scope for this benchmark.

## Theorem Tier
`T4`

## Expected Failure Modes
- `carrier_failure`
- `coupling_failure`
- `horizon_failure`

## Reference Commands
- `python benchmarks/BP_Weakly_Nonlinear_Slow_Manifold/generate.py`
- `python benchmarks/BP_Weakly_Nonlinear_Slow_Manifold/run_reference.py`
- `python benchmarks/BP_Weakly_Nonlinear_Slow_Manifold/figure_recipe.py`
