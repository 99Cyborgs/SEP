# Benchmark Registry

Each benchmark family in this repository is executable and comes with:

- `spec.yaml`: formal system definition, parameter ranges, theorem tier, and failure modes.
- `README.md`: benchmark notes, ground truth, and protocol-level interpretation.
- `generate.py`: prints the reference parameter set used by the code path.
- `run_reference.py`: executes the small reference run and writes a ledger.
- `expected_metrics.json`: machine-readable metric expectations for positive and negative cases.
- `figure_recipe.py`: lists the figure scripts relevant to the benchmark family.

The registry lives in [registry.yaml](/G:/GitHub/incubate/Subsystem%20Emergence%20Program/benchmarks/registry.yaml).

The intentionally deferred benchmark is `BP_Delay_Coupled_Pair`: the code path uses a finite-dimensional lifted surrogate and the README/spec explicitly document the completion contract for true delay support.
