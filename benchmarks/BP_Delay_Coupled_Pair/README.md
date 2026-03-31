# BP Delay Coupled Pair

## Formal System Definition
A true fixed-lag linear delay-differential system for a two-module pair,
\[
x'(t) = A_0 x(t) + A_\tau x(t-\tau),
\]
analyzed through a sampled history propagator on a nodal history grid.

## Parameter Ranges
- delay: `0.2` to `0.8`
- self decay: `0.7` to `1.1`
- shear coupling: `1.5` to `2.6`
- delayed self feedback: `1.0` to `1.6`
- delayed cross feedback: `0.15` to `0.4`

## Ground Truth Notes
- The two slow modules are planted.
- The state is the physical two-module state; the higher-dimensional history operator exists only inside the diagnostic layer.
- Slow carriers are extracted from the sampled history propagator rather than from a lifted surrogate matrix.
- The benchmark now carries a required refinement ladder, so it should be cited as discretization-backed evidence rather than as a closed delay-semigroup theorem.

## Theorem Tier
`T2/T3`

## Expected Failure Modes
- `transient_growth_failure`
- `horizon_failure`

## Completion Contract
- Integrate the fixed-lag DDE with a fixed-step method of steps.
- Build a one-window history propagator from nodal history basis states.
- Revalidate `L3`, transient-growth, and refinement-ladder diagnostics on the true delayed dynamics without changing the public benchmark ID.

## Reference Commands
- `python benchmarks/BP_Delay_Coupled_Pair/generate.py`
- `python benchmarks/BP_Delay_Coupled_Pair/run_reference.py`
- `python benchmarks/BP_Delay_Coupled_Pair/figure_recipe.py`
