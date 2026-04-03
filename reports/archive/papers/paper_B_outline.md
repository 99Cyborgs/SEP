# Paper B. Finite-Time Coherent Subsystem Emergence

## Claim
Subsystem emergence in nonautonomous systems is a singular-gap and coherent-subspace phenomenon rather than a frozen-generator eigenvalue phenomenon.

## Minimal Theorem Content
- T3 finite-window leakage theorem candidate.
- Window-dependent autonomy horizon and coherent carrier tracking statement.

## Figure List
- singular spectra and gap ladders
- coherent carriers across windows
- horizon versus window-length plots
- static surrogate failure examples
- positive-versus-mixed transport comparison
- regrouped-window sensitivity comparison

## Anticipated Criticism
The result may depend on arbitrary window choices and synthetic transport examples.

## Response Strategy
Show explicit window sensitivity diagnostics, compare against frozen surrogates, and keep claims at the benchmarked finite-window level.
Anchor the positive reference case in the moderate-drift transport regime where coherent lobes persist across windows without collapsing into a stationary surrogate.
Treat fast-drift or weak-coherence transport settings as negative evidence rather than folding them into the accepted T3 case.
Use `BP_Windowed_Transport_Flow` as the accepted moderate-drift reference and `BP_T3_Window_Sensitivity_Pair` as the positive-versus-mixed failure-geometry exhibit.
Report adjacent-window carrier deformation and fixed regrouping diagnostics as part of the protocol contract, while keeping them nonfatal until thresholds stabilize.
