# Repository Hygiene

## Committed Versus Regenerated
- commit canonical benchmark specs, protocol docs, gate criteria, reference ledgers, and published figure manifests
- do not treat `__pycache__/`, `.pytest_cache/`, or scratch reruns under `tmp/` as durable evidence
- do not ship raw upstream zip archives inside the release snapshot; keep only derived fixtures plus source-archive names in metadata
- regenerate transient diagnostics locally instead of checking them in as required content

## Cache Policy
- Python cache artifacts belong under ignore rules only
- disposable reruns and exploratory outputs belong under `tmp/` or another ignored scratch location

## Git Working Tree Recovery
This workspace does not currently expose a discoverable `.git` directory above the project root. That means repository history cannot be reconstructed from local files alone.

If Git tracking needs to be restored:
1. recover the authoritative upstream or original working tree containing `.git`
2. re-home this project directory into that working tree rather than running `git init` here
3. verify that `git status` resolves from the intended root and that `.gitignore` suppresses cache-only noise
