# Validation Protocol

Validation is gate based rather than narrative based.

## Steps

1. Run one or more reference benchmarks and write canonical evidence bundles.
2. Apply the appropriate gate script.
3. Serialize the gate result to JSON and Markdown.
4. Archive any triggered failures.
5. Record what was validated and what remains unvalidated.

## Required Evidence

- observables in the canonical evidence bundle
- selected law and held-out fit error
- predicted versus observed horizon comparison
- coordinate sensitivity and refinement diagnostics where implemented

## Threshold Layers

- global failure taxonomy: repository-wide thresholds decide when labels such as `gap_failure`, `coupling_failure`, or `numerical_artifact_failure` trigger
- benchmark-local package acceptance: application packages can use stricter singular-gap, deformation, horizon, or refinement bounds than the global taxonomy and can mark some taxonomy labels as advisory
- gate criteria: each gate decides which metrics are enforced for pass/fail and which metrics are merely reported

## Disallowed Shortcuts

- tuning the projection after seeing the gate result
- deleting negative evidence bundles or failure records
- claiming success from a single norm or a single time point
