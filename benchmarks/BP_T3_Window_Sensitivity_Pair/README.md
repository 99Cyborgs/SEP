# BP T3 Window Sensitivity Pair

## Formal System Definition
A paired transport benchmark built from the same row-stochastic ring flow construction used by `BP_Windowed_Transport_Flow`, but with one moderate-drift positive branch and one fast-drift mixed branch.

## Parameter Sets
- `reference`: `fast_drift_mixed`
- `matched_positive`: moderate-drift positive control

## Intended Use
- harden Paper B protocol evidence with a positive-versus-mixed transport comparison
- show that finite-window coherent advantage can disappear even when the flow remains structured and the singular gap stays plausible
- make window regrouping sensitivity explicit in the ledger rather than leaving it implicit in narrative text

## Expected Reading
- `matched_positive` should retain a positive coherent-versus-frozen horizon gain and lower carrier deformation
- `fast_drift_mixed` should show weaker or zero horizon advantage together with worse adjacent-window and regrouped carrier tracking
- the regrouped-window diagnostics are evidence only in this slice and are not gate-fatal

## Reference Commands
- `python benchmarks/BP_T3_Window_Sensitivity_Pair/generate.py`
- `python benchmarks/BP_T3_Window_Sensitivity_Pair/run_reference.py`
- `python benchmarks/BP_T3_Window_Sensitivity_Pair/run_matched_positive.py`
- `python benchmarks/BP_T3_Window_Sensitivity_Pair/figure_recipe.py`
