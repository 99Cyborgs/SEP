# T4 Local Validity Protocol

## Purpose
Interpret `T4` evidence as a bounded local-validity statement rather than a global nonlinear theorem.

## What Is Held Fixed
- the three-dimensional fast-slow template
- the two-dimensional slow sector
- the leakage threshold and time grid
- the use of adjacent projector deformation as the gate-facing local stability diagnostic

## What Is Varied
- nonlinear coupling strength
- effective amplitude through the initial condition
- the resulting fast slaving defect and anchor drift

## Diagnostic Contract
`T4` ledgers should now expose:
- `adjacent_projector_deformation`
- `anchor_projector_deformation`
- `fast_slaving_defect`
- `curvature_indicator`
- `max_state_norm`
- `local_validity_margin`
- `l2_minus_l1_rmse`

`BP_Weakly_Nonlinear_Slow_Manifold` is the accepted local reference. `BP_T4_Local_Validity_Pair/reference` is retained as amplitude-breakdown evidence and is reported in `G4` without becoming gate-fatal.
