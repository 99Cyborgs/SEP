# Developer Usage

## Setup

```bash
python -m pip install -e .[dev]
```

## Run A Reference Benchmark

```bash
python benchmarks/BP_Linear_Two_Block/run_reference.py
python benchmarks/BP_Clickstream_Docs_Funnel/run_reference.py
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

- preserve benchmark ids because ledgers and gates key off them
- do not promote conjectural notes to theorem status without updating the theorem-note confidence level
- keep failure signatures and gate criteria in sync

## Hygiene

- cache artifacts belong under `.gitignore`, not in durable evidence
- keep scratch reruns under `tmp/`
- if Git history is missing, re-home the project into the original working tree instead of creating a fresh repository here
