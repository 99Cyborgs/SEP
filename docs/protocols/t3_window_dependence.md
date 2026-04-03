# T3 Window Dependence Protocol

## Purpose
Interpret `T3` evidence as a bounded finite-window claim rather than as a general theorem about nonautonomous transfer-operator cocycles.

## What Is Held Fixed
- the underlying ring transport construction
- the coarse subsystem partition
- the coherent rank used in transport analysis
- the frozen-surrogate comparison rule

## What Is Varied
- drift persistence through `phase_increment`
- coherent carrier strength
- one fixed alternate window partition given by `[[0], [1, 2], [3], [4, 5]]`

## Reading Rule
- `BP_Windowed_Transport_Flow` is the accepted moderate-drift positive reference
- `BP_T3_Window_Sensitivity_Pair/matched_positive` is a positive control under the paired protocol
- `BP_T3_Window_Sensitivity_Pair/reference` is mixed or negative evidence retained to show that coherent advantage can disappear under faster drift without collapsing the transport construction into noise

## Diagnostic Contract
Transport evidence bundles should now expose:
- adjacent-window carrier deformation
- regrouped-window carrier deformation
- coherent-versus-frozen horizon gain under the native windowing
- coherent-versus-frozen horizon gain under the fixed regrouping

These diagnostics are interpreted as protocol evidence only in the current slice. They are reported in `G3`, but they do not alter the gate pass/fail rule yet.
