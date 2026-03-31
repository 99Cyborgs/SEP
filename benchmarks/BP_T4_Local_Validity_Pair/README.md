# BP T4 Local Validity Pair

## Formal System Definition
A paired weakly nonlinear fast-slow benchmark using the same three-dimensional template as `BP_Weakly_Nonlinear_Slow_Manifold`, but split into a locally valid branch and an amplitude-driven local-validity breakdown branch.

## Parameter Sets
- `reference`: `amplitude_breakdown`
- `matched_local`: accepted local control branch

## Intended Use
- harden Paper D with explicit nonlinear local-validity failure geometry
- show that bounded local validity can degrade even when the same benchmark structure is retained
- surface fast slaving defect, anchor drift, and local-validity margin directly in the ledger

## Expected Reading
- `matched_local` should keep `L2` competitive with `L1`, preserve a positive local-validity margin, and retain smaller fast slaving defect
- `amplitude_breakdown` should show worse anchor drift, worse fast slaving defect, and a weaker `L2` advantage

## Reference Commands
- `python benchmarks/BP_T4_Local_Validity_Pair/generate.py`
- `python benchmarks/BP_T4_Local_Validity_Pair/run_reference.py`
- `python benchmarks/BP_T4_Local_Validity_Pair/run_matched_local.py`
- `python benchmarks/BP_T4_Local_Validity_Pair/figure_recipe.py`
