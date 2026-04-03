# Reproducibility Policy

1. Every executed case writes a canonical run manifest plus structured evidence files under `results/evidence/`.
2. The canonical evidence bundle records benchmark id, branch, theorem tier, seed, parameters, observables, law fits, acceptance status, failure labels, and source-of-truth audit metadata.
3. If a git hash is unavailable, the environment fingerprint records `null` rather than inventing one.
4. Generated manifest, index, and gate-report paths are serialized as repository-relative POSIX paths so archive-mode snapshots remain platform neutral.
5. Compatibility ledgers under `results/ledgers/` are opt-in legacy archive shims and must not be treated as the authoritative read surface.
6. Discovery and validation are split conceptually:
   carrier choices used for evaluation must be derivable from the benchmark specification or the documented analysis rule.
7. Numerical refinement is mandatory:
   no positive claim survives without at least one refinement diagnostic.
8. Coordinate robustness is mandatory:
   admissible basis changes must not materially change the claim.
9. Negative results are first-class outputs and are archived under `failures/`.
10. Benchmark execution and archive generation must not write into the tracked repository root by default; safe scratch roots are the standard execution surface.
11. Archive refreshes must validate canonical evidence completeness before generation and may promote tracked outputs only through the explicit scratch-root refresh driver.
