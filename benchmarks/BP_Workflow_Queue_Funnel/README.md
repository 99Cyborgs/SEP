# BP Workflow Queue Funnel

## Formal System Definition
A bundled workflow-queue benchmark with four named operational stages and four ordered reporting windows. Raw stage-to-stage counts are converted into row-stochastic operators with a documented pseudocount smoother.

## Data Provenance
- source page: `bundled_repository_fixture`
- source archive: `workflow_queue_funnel_q1_2026.json`
- domain: operational workflow queues
- bundled fixture: repository-curated stage-transition counts used only as reproducible non-navigation application evidence

## Stage Slice
- `Intake`
- `Triage`
- `Execution`
- `Closure`

## Parameter Sets
- `reference`: stable queue with persistent intake-versus-execution structure
- `negative_detour`: rework-heavy queue pattern retained as an explicit rejection case

## Cross-Domain Application Claim
- This benchmark extends application evidence beyond mobility and digital navigation without claiming a public-data theorem.
- The `reference` case is accepted only as a bounded transport-style workflow slice.
- The `negative_detour` case is expected to remain rejection-labeled because rework loops collapse the singular gap and destroy the stable carrier geometry.

## Acceptance Layer Notes
- package acceptance uses benchmark-local workflow floors rather than the global taxonomy alone
- the negative detour case is rejected without a taxonomy-level `coupling_failure`; the blocking evidence is gap collapse plus carrier deformation

## Expected Failure Modes
- current negative fixture: `carrier_failure`
- the package overlay would also block `coupling_failure` or `numerical_artifact_failure` if later workflow variants triggered them

## Reference Commands
- `python benchmarks/BP_Workflow_Queue_Funnel/generate.py`
- `python benchmarks/BP_Workflow_Queue_Funnel/run_reference.py`
- `python benchmarks/BP_Workflow_Queue_Funnel/run_negative_detour.py`
- `python benchmarks/BP_Workflow_Queue_Funnel/figure_recipe.py`
