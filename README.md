# Subsystem Emergence Program

## Current State

- SEP is a Python 3.11 validation engine for subsystem-emergence claims.
- The current registry defines 6 claims, 18 benchmark families, and 30 named cases in `benchmarks/registry.yaml`.
- The active architecture is evidence-first: canonical inputs and outputs are `benchmarks/registry.yaml`, `validation/acceptance_profiles.yaml`, `results/evidence/`, `results/indexes/`, and `results/validation_gates/`.
- The implemented benchmark surface spans linear, nonnormal, transport, nonlinear, stochastic, delay-surrogate, and application families under `src/subsystem_emergence/`.
- Generated benchmark documentation lives in `docs/generated/benchmark_catalog.md`. Compatibility ledgers remain in `results/ledgers/` for legacy consumers.
- Archive and paper-packaging code remains available under `src/subsystem_emergence/reports/archive/`, but it is downstream support rather than the primary product.

## Goal

- Produce machine-auditable numerical evidence for subsystem-emergence claims instead of relying on narrative-only reports.
- Keep supported cases, negative controls, failure modes, and application identifiability limits explicit and reproducible.
- Preserve an executable path from benchmark definition through evidence generation to G1-G6 validation outcomes.

## Forward Direction

- Finish converging the repository on the evidence/index/validation-gate pipeline and continue retiring report-first and ledger-first legacy paths.
- Keep generated benchmark docs and per-benchmark summaries synchronized with the canonical registry and acceptance profiles.
- Strengthen coverage around application benchmarks, delay-family qualifications, and archive-write safety without relaxing reproducibility or negative-result traceability.
