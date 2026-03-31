# External Application Evidence

## Current Cross-Domain Posture
The repository now carries four bounded application domains:
- bike-share mobility case studies for Paper E
- a bundled documentation clickstream benchmark as non-mobility operator evidence
- a bundled support-portal navigation benchmark as a second non-mobility operator evidence family
- a bundled workflow-queue benchmark as non-navigation operational evidence

## Policy
- keep application claims case-study-only unless a theorem note explicitly upgrades them
- preserve at least one negative or mixed case in each domain
- reuse the same ledger, gate, and refinement conventions used by transport-style synthetic benchmarks
- separate three layers explicitly:
  - global failure taxonomy labels
  - benchmark-local package acceptance overlays
  - gate-level publication-readiness enforcement

## Current Non-Mobility Benchmark
- `BP_Clickstream_Docs_Funnel`
- accepted slice: `reference`
- rejection slice: `negative_detour`
- `BP_Support_Portal_Funnel`
- accepted slice: `reference`
- rejection slice: `negative_detour`
- `BP_Workflow_Queue_Funnel`
- accepted slice: `reference`
- rejection slice: `negative_detour`

## Acceptance Interpretation
- non-mobility acceptance is benchmark-local and uses stricter package floors on singular gap, carrier deformation, horizon, and refinement than the global failure taxonomy
- G6 now enforces the declared application case matrix using that real acceptance logic rather than treating `parameter_id == "reference"` as acceptance
- a case can be rejection-labeled for package purposes without triggering every possible taxonomy label mentioned in older prose; the executable package criteria and rejection reasons are the source of truth

## Interpretation
The non-mobility benchmarks are not meant to prove a universal workflow or navigation theorem. Their role is narrower: show that the coherent transport machinery is not structurally tied to bike-share flows, a single curated digital-navigation fixture, or page-navigation semantics alone.
