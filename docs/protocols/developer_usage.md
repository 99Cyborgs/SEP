# Developer Usage

## Setup

```bash
python -m pip install -e .[dev]
```

## Run A Reference Benchmark

```bash
python benchmarks/BP_Linear_Two_Block/run_reference.py
python benchmarks/BP_Clickstream_Docs_Funnel/run_reference.py
python -m subsystem_emergence.benchmarking run-case BP_Linear_Two_Block --root tmp/linear_probe
python -m subsystem_emergence.reports.archive.refresh --target cross_domain --scratch-root tmp/archive_cross_domain
```

## Run Gate Checks

```bash
python validation/gate_G1.py
python validation/gate_G2.py
python validation/gate_G3.py
python validation/gate_G4.py
python validation/gate_G5.py
python validation/gate_G6.py
```

## Run Tests

```bash
python validation/ci_checks.py
pytest
```

## Important Constraints

- preserve benchmark ids because canonical manifests, indexes, and gates key off them
- do not promote conjectural notes to theorem status without updating the theorem-note confidence level
- keep failure signatures and gate criteria in sync
- treat `results/ledgers/` as compatibility-only; new code should read `results/evidence/` or `results/indexes/`
- benchmark and application runs must target an ignored scratch root; direct repo-root writes are rejected unless the dangerous override is set explicitly
- archive refreshes must go through `python -m subsystem_emergence.reports.archive.refresh`; direct archive generation into the tracked checkout is non-default and blocked

## Hygiene

- cache artifacts belong under `.gitignore`, not in durable evidence
- keep scratch reruns under `tmp/`
- `python -m subsystem_emergence.benchmarking run-case ...` auto-creates an ignored scratch root when `--root` is omitted
- prefer `--root tmp/<name>` when you want a stable scratch location you can inspect after the run
- pass `--emit-compatibility-ledgers` only when intentionally generating legacy shims for archived consumers
