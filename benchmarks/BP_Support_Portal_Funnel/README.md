# BP Support Portal Funnel

## Formal System Definition
A bundled support-portal navigation benchmark with four named pages and four ordered support-lifecycle windows. Raw page-to-page counts are converted into row-stochastic operators with a documented pseudocount smoother.

## Data Provenance
- source page: `bundled_repository_fixture`
- source archive: `support_navigation_funnel_q1_2026.json`
- domain: support and help navigation
- bundled fixture: repository-curated support-session transitions used only as reproducible cross-domain application evidence

## Page Slice
- `Help Home`
- `Search Results`
- `Troubleshooting Guide`
- `Ticket Form`

## Parameter Sets
- `reference`: stable support funnel with persistent self-serve versus escalation structure
- `negative_detour`: detour-heavy support routing pattern retained as an explicit rejection case

## Cross-Domain Application Claim
- This benchmark adds a second non-mobility navigation domain without changing the named-window operator workflow.
- The `reference` case is accepted only as a bounded transport-style application slice.
- The `negative_detour` case is expected to remain rejection-labeled because its singular gap collapses and its carrier geometry deforms too far.

## Acceptance Layer Notes
- package acceptance uses stricter benchmark-local floors than the repository-wide failure taxonomy
- the negative detour case is rejected by package criteria even though its residual coupling stays just below the global `coupling_failure` cutoff

## Expected Failure Modes
- current negative fixture: `gap_failure`, `carrier_failure`
- the package overlay would also block `coupling_failure` or `numerical_artifact_failure` if later variants triggered them

## Reference Commands
- `python benchmarks/BP_Support_Portal_Funnel/generate.py`
- `python benchmarks/BP_Support_Portal_Funnel/run_reference.py`
- `python benchmarks/BP_Support_Portal_Funnel/run_negative_detour.py`
- `python benchmarks/BP_Support_Portal_Funnel/figure_recipe.py`
