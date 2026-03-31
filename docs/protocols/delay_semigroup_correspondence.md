# Delay Semigroup Correspondence

## Purpose
This note records how the repository relates the infinite-dimensional fixed-lag delay semigroup to the executable sampled-history benchmark path used in `BP_Delay_Coupled_Pair`.

## Two-Layer Program
- analytical layer: the physical delay system lives on a history state space over `[-tau, 0]`
- executable layer: the repository builds a one-window sampled-history operator on a finite nodal grid and extracts slow carriers from that operator

## Admissibility Conditions
- the delay is fixed and positive
- the sampled times are integer multiples of the delay
- the history interpolant is piecewise linear on the chosen nodal grid
- the refinement ladder must show stable autonomy horizon, transient amplification, and reduced coupling under increasing history-grid resolution and decreasing step size

## What The Benchmark Supports
- evidence that the corrected T2/T3 numerical protocol survives a fixed-lag delay setting
- evidence that the sampled-history diagnostic is not wildly unstable under the declared refinement ladder
- a bounded correspondence claim between the physical delay system and the executable surrogate family
- evidence that adjacent refinement levels do not radically change the learned physical-state carrier slice under the declared ladder

## What The Benchmark Does Not Support
- a theorem for arbitrary delay semigroups
- a discretization-independent carrier theorem
- a claim that the sampled-history propagator is exact beyond the declared refinement diagnostics

## Required Diagnostics
- `autonomy_horizon_relative_span`
- `transient_relative_span`
- `block_residual_relative_span`
- `surrogate_relative_span`
- `adjacent_terminal_projector_deformation_max`
- `constant_history_projector_deformation`

The delay benchmark should be cited as bounded theorem support only after these diagnostics are reported alongside the usual nonnormal correction metrics and the delay-specific `G2` summary metrics.
