# BP Clickstream Docs Funnel

## Formal System Definition
A bundled documentation-portal clickstream benchmark with four named pages and four ordered lifecycle windows. Raw page-to-page counts are converted into row-stochastic operators with a documented pseudocount smoother.

## Data Provenance
- source page: `bundled_repository_fixture`
- source archive: `docs_navigation_funnel_q1_2026.json`
- domain: documentation navigation clickstreams
- bundled fixture: repository-curated page-transition counts used only as reproducible cross-domain application evidence

## Page Slice
- `Docs Home`
- `Quickstart`
- `API Reference`
- `SDK Guides`

## Parameter Sets
- `reference`: stable documentation funnel with persistent guide/API separation
- `negative_detour`: detour-heavy navigation pattern retained as an explicit rejection case

## Cross-Domain Application Claim
- This benchmark extends application evidence beyond bike-share mobility without claiming a public-data theorem.
- The `reference` case is accepted only as a bounded transport-style application slice.
- The `negative_detour` case is expected to remain rejection-labeled because carrier geometry and reduced coupling both degrade.

## Expected Failure Modes
- `carrier_failure`
- `coupling_failure`
- `numerical_artifact_failure`

## Reference Commands
- `python benchmarks/BP_Clickstream_Docs_Funnel/generate.py`
- `python benchmarks/BP_Clickstream_Docs_Funnel/run_reference.py`
- `python benchmarks/BP_Clickstream_Docs_Funnel/run_negative_detour.py`
- `python benchmarks/BP_Clickstream_Docs_Funnel/figure_recipe.py`
