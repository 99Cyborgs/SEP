# Report Archive

This directory holds downstream-only manuscript and report helpers that are not part of SEP's canonical numerical validation runtime.

- Benchmark execution, validation gates, acceptance decisions, and traceability now terminate under `results/evidence/`, `results/indexes/`, and `results/validation_gates/`.
- Archive generators are expected to read canonical run manifests, observables summaries, and canonical indexes rather than raw ledgers.
- `results/ledgers/` may still appear as opt-in compatibility-only historical snapshots while archive consumers migrate, but they are not canonical.
- Archived material remains here for historical reconstruction and manuscript support only.
- Legacy figure recipes now live under `reports/archive/benchmark_scripts/`.
- Historical figure outputs and helper scripts now live under `reports/archive/figures/`.
- Historical report summaries now live under `reports/archive/generated/`.
- Maintainers should not add new canonical validation logic under `reports/archive/`.
- Refresh tracked archive outputs through `python -m subsystem_emergence.reports.archive.refresh`; the driver materializes canonical evidence into scratch, validates completeness, renders archive outputs there, and only promotes tracked files when `--promote --force` is passed intentionally.
- Direct archive generation into the tracked repository root is blocked by default. Use a scratch root with a materialized evidence set if you call the package generators directly.
