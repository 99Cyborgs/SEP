# Repository Hygiene

## Committed Versus Regenerated
- commit canonical benchmark specs, protocol docs, gate criteria, and published archive manifests
- treat `results/evidence/`, `results/indexes/`, and `results/validation_gates/` as canonical generated outputs that can be regenerated for validation
- treat `results/ledgers/` as opt-in compatibility-only historical snapshots, not the primary evidence layer
- do not treat `__pycache__/`, `.pytest_cache/`, or scratch reruns under `tmp/` as durable evidence
- do not ship raw upstream zip archives inside the release snapshot; keep only derived fixtures plus source-archive names in metadata
- regenerate transient diagnostics locally instead of checking them in as required content

## Cache Policy
- Python cache artifacts belong under ignore rules only
- disposable reruns and exploratory outputs belong under `tmp/` or another ignored scratch location

## Git Working Tree Recovery
This repository is expected to be used inside a normal Git working tree with the project root as the authoritative checkout.

If the working tree becomes dirty during exploratory runs:
1. prefer `--root tmp/<run_name>` for stable scratch benchmark executions, or omit `--root` to let the runtime auto-create an ignored scratch root
2. remove transient caches and scratch outputs before concluding hygiene is broken
3. refresh tracked archive snapshots only through `python -m subsystem_emergence.reports.archive.refresh --promote --force`
4. emit compatibility ledgers only when intentionally generating legacy shims via `--emit-compatibility-ledgers`
