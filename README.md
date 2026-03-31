# Subsystem Emergence Research Suite

Subsystem Emergence is a falsification-first scientific software repository for testing one claim:

1. slow modes are spectrally or singularly isolated,
2. their carrier subspace is stable under perturbation,
3. reduced slow dynamics is only weakly coupled,
4. and finite-horizon subsystem leakage follows a leading-order affine law.

The core autonomous target law is

```math
\ell(\tau) \lesssim \varepsilon_s + \rho \tau,
\qquad
\tau_\eta \approx \frac{\eta - \varepsilon_s}{\rho}
\quad \text{when } \eta > \varepsilon_s.
```

Finite-time transport, weakly nonlinear, and stochastic modules extend this doctrine without blurring theorem candidates, conjectural extensions, numerical protocols, and validation gates.

## Source Of Truth Audit

- The release snapshot is expected to ship without cache directories or raw provenance archives under `tmp/`; source archive names in ledgers refer to upstream datasets, not bundled zip payloads.
- The live tree already contained the intended scaffold: `benchmarks/`, `docs/`, `observables/`, `src/`, `validation/`, `results/`, `figures/`, and `failures/`.
- The live scaffold was preserved where useful and its placeholders were superseded in place by runnable implementations, explicit benchmark specs, and validation artifacts.
- Because the archive itself was missing, archive-vs-live byte-level reconciliation was not possible; that limitation is recorded in run metadata.

## What Is Implemented

- `src/subsystem_emergence/`: typed core utilities, linear/nonnormal analysis, finite-time transport tools, weakly nonlinear local analysis, stochastic propagator and bootstrap support, and a benchmark runner.
- `benchmarks/`: eight benchmark families with specs, metric templates, reference runners, and figure recipes.
- `benchmarks/`: synthetic theorem-tier families plus a bundled real-data mobility case study for Paper E.
- `benchmarks/`: synthetic theorem-tier families plus bundled real-data mobility case studies for Paper E, including one accepted slice, two negative slices, and one mixed non-Chicago slice.
- `benchmarks/`: synthetic theorem-tier families plus a bundled non-mobility clickstream application benchmark for cross-domain transport evidence.
- `benchmarks/`: includes a bundled workflow-queue application benchmark that extends cross-domain evidence beyond digital navigation while preserving an explicit rejected rework case.
- `benchmarks/`: includes a same-spectrum T2 counterexample family for Paper C failure geometry.
- `observables/`: machine-readable ledger schema plus a catalog defining the core observable set.
- `validation/`: gate scripts and criteria for G1 through G6.
- generated manifests and ledgers serialize repository-relative POSIX paths so the snapshot stays portable across Windows, macOS, and Linux.
- `docs/theorem_notes/`: theorem notes for T1 through T5 with explicit assumptions, obstruction lists, and proof gaps.
- `figures/scripts/`: reproducible figure scripts for spectra, leakage, transport, curvature, uncertainty bands, and failure atlases.
- `failures/`: archive directories and formal failure signatures.
- `tests/`: unit tests and end-to-end smoke tests.

## Quickstart

```bash
python -m pip install -e .[dev]
python benchmarks/BP_Linear_Two_Block/run_reference.py
python benchmarks/BP_Non_Normal_Shear/run_reference.py
python benchmarks/BP_T2_Same_Spectrum_Pair/run_reference.py
python benchmarks/BP_Windowed_Transport_Flow/run_reference.py
python benchmarks/BP_Weakly_Nonlinear_Slow_Manifold/run_reference.py
python benchmarks/BP_Noisy_Metastable_Network/run_reference.py
python benchmarks/BP_Mobility_Chicago_Corridors/run_reference.py
python benchmarks/BP_Mobility_Downtown_Routing_Instability/run_reference.py
python benchmarks/BP_Mobility_NYC_East_Corridor/run_reference.py
python benchmarks/BP_Clickstream_Docs_Funnel/run_reference.py
python benchmarks/BP_Support_Portal_Funnel/run_reference.py
python benchmarks/BP_Workflow_Queue_Funnel/run_reference.py
python -c "from subsystem_emergence.benchmarking import run_mobility_application_evaluation; print(run_mobility_application_evaluation(seed=0))"
python -c "from subsystem_emergence.application.cross_domain import generate_cross_domain_application_package; print(generate_cross_domain_application_package())"
python validation/ci_checks.py
python validation/gate_G1.py
python validation/gate_G2.py
python validation/gate_G6.py
pytest
```

## Layout

- `docs/theorem_notes/`: theorem notes, confidence levels, obstruction lists.
- `docs/protocols/`: norms, observables, validation, reproducibility, identifiability, and developer usage.
- `docs/protocols/`: includes delay semigroup correspondence, external application evidence, and repository hygiene notes.
- `docs/protocols/`: includes a T2 failure-geometry interpretation note for the same-spectrum counterexample family.
- `docs/protocols/`: includes a support-navigation evidence note for the second non-mobility application track.
- `docs/protocols/`: includes a workflow-queue evidence note for the non-navigation operational application track.
- `benchmarks/`: benchmark registry and family-specific assets.
- `src/subsystem_emergence/`: executable analysis code.
- `results/`: ledgers, fits, gate reports, and reference outputs.
- `failures/`: archived failures and negative-result registry.
- `figures/scripts/`: reusable plotting entry points.
- `validation/`: machine-readable gate criteria and executable gate scripts.

## Build Principles

- No theorem claim is upgraded past its current proof status.
- Nonnormality is treated as a first-class threat, not a footnote.
- Every benchmark declares observables and failure criteria.
- Negative results are preserved, serialized, and archived.
- Coordinate sensitivity and numerical refinement are explicit diagnostics, not optional cleanup.
