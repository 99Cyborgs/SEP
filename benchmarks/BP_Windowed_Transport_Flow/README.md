# BP Windowed Transport Flow

## Formal System Definition
A windowed sequence of row-stochastic transport operators on a ring, with two coherent lobes that persist but drift across windows. The benchmark is built to compare coherent-window analysis against frozen autonomous surrogates.

## Parameter Ranges
- grid size: `24` to `64`
- window count: `4` to `12`
- base shift: `0.6` to `1.2`
- phase increment: `0.7` to `1.3`
- diffusion: `1.0` to `4.0`
- coherent strength: `1.5` to `3.0`

## Ground Truth Notes
- The coherent structures are synthetic but explicit.
- The benchmark is time dependent by construction; frozen surrogates are expected to underperform.
- The accepted reference case uses moderate drift and relatively broad kernels so the coherent carriers move, but do not decohere between adjacent windows.
- The frozen surrogate still sees the same average transport, but it washes out the phase-dependent alignment that keeps the coherent-window horizon positive.

## Accepted Reference Case
- `base_shift = 0.8`
- `phase_increment = 0.9`
- `diffusion = 2.8`
- `coherent_strength = 2.4`
- Expected behavior: mean singular gap remains above gate floor, coherent leakage beats the frozen surrogate on most windows, and `G3` passes with a positive horizon gain.

## Excluded Regimes
- Larger phase increments can force carrier mismatch quickly enough that the coherent method loses its horizon advantage.
- Weaker coherent strength or sharper kernels can leave the singular gap intact while still destroying persistent carrier alignment.
- Effectively stationary parameter choices are not accepted as positive evidence because they erase the paper's coherent-versus-frozen comparison.

## Theorem Tier
`T3`

## Expected Failure Modes
- `gap_failure`
- `horizon_failure`

## Reference Commands
- `python benchmarks/BP_Windowed_Transport_Flow/generate.py`
- `python benchmarks/BP_Windowed_Transport_Flow/run_reference.py`
- `python benchmarks/BP_Windowed_Transport_Flow/figure_recipe.py`
