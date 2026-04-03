# Benchmark Registry

The canonical source of benchmark truth is `benchmarks/registry.yaml`.
Per-benchmark `README.md` and `spec.yaml` files are generated summaries and must not carry independent thresholds or paper workflows.

Canonical execution uses benchmark case ids and writes evidence bundles under `results/evidence/`.
Legacy ledger snapshots under `results/ledgers/` are compatibility-only and should not be used as the primary read path.

Use `python -m subsystem_emergence.benchmarking list` to enumerate families and `python -m subsystem_emergence.benchmarking run-case <benchmark_id>` to execute the default case.