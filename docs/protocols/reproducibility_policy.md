# Reproducibility Policy

1. Every reference run writes a per-run JSON ledger, a Markdown summary, and an aggregate JSONL line.
2. The ledger records benchmark id, branch, theorem tier, seed, parameters, observables, law fits, failure labels, and source-of-truth audit metadata.
3. If a git hash is unavailable, the ledger records `null` rather than inventing one.
4. Generated ledger, manifest, and gate-report paths are serialized as repository-relative POSIX paths so archive-mode snapshots remain platform neutral.
5. Discovery and validation are split conceptually:
   carrier choices used for evaluation must be derivable from the benchmark specification or the documented analysis rule.
6. Numerical refinement is mandatory:
   no positive claim survives without at least one refinement diagnostic.
7. Coordinate robustness is mandatory:
   admissible basis changes must not materially change the claim.
8. Negative results are first-class outputs and are archived under `failures/`.
