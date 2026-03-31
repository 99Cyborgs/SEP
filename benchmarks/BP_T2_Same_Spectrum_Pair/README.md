# BP T2 Same Spectrum Pair

## Formal System Definition
A paired autonomous linear benchmark where both branches share the same retained slow eigenvalues and fast decay scales, but the slow block geometry changes from rotated normal to upper-triangular nonnormal.

## Parameter Sets
- `reference`: `matched_nonnormal`
- `matched_normal`: rotated normal control branch

## Intended Use
- make Paper C failure geometry concrete
- show that nominal spectral separation can stay fixed while transient amplification and held-out law behavior diverge
- retain both branches as first-class evidence rather than treating the normal branch as disposable setup

## Expected Reading
- `matched_normal` should have low transient amplification, small pseudospectral proxy, and weak need for correction
- `matched_nonnormal` should have similar spectral gap but much larger transient amplification, larger pseudospectral proxy, and a substantially stronger L3-vs-L1 gap

## Reference Commands
- `python benchmarks/BP_T2_Same_Spectrum_Pair/generate.py`
- `python benchmarks/BP_T2_Same_Spectrum_Pair/run_reference.py`
- `python benchmarks/BP_T2_Same_Spectrum_Pair/run_matched_normal.py`
- `python benchmarks/BP_T2_Same_Spectrum_Pair/figure_recipe.py`
