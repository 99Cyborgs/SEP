# Benchmark Registry Protocol

The registry in `benchmarks/registry.yaml` is the executable directory of benchmark families. Every entry must provide:

- benchmark id
- branch
- theorem tier
- human-readable description
- spec path
- readme path
- reference runner
- expected metrics path
- figure recipe path

If a benchmark is partial, the partial status must appear in its README and spec rather than being hidden in code.

For application benchmarks, `expected_metrics.json` may carry benchmark-local package acceptance overlays in addition to global failure-taxonomy expectations. Those layers should not be collapsed into one unnamed threshold.
