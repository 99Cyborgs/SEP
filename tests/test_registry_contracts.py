from __future__ import annotations

from pathlib import Path

from subsystem_emergence.io.registry import benchmark_case_definition, benchmark_definitions, claim_definitions
from subsystem_emergence.policy import load_acceptance_policy


def test_registry_exposes_claims_and_cases() -> None:
    claims = claim_definitions()
    benchmarks = benchmark_definitions()
    assert len(claims) >= 6
    assert len(benchmarks) == 18
    assert all(benchmark.cases for benchmark in benchmarks)


def test_every_case_references_a_defined_acceptance_profile() -> None:
    profiles = load_acceptance_policy()["acceptance_profiles"]
    for benchmark in benchmark_definitions():
        for case in benchmark.cases:
            assert case.acceptance_profile in profiles


def test_mobility_registry_contains_validation_matrix_cases() -> None:
    mobility = next(benchmark for benchmark in benchmark_definitions() if benchmark.family_id == "BP_Mobility_Chicago_Corridors")
    case_ids = {case.case_id for case in mobility.cases}
    assert "reference" in case_ids
    assert "negative_weekend" in case_ids
    assert "weekday_window_coarsened" in case_ids


def test_case_lookup_supports_registered_case_ids() -> None:
    case = benchmark_case_definition("BP_T4_Local_Validity_Pair", "reference")
    assert case.case_id == "reference"
    assert case.acceptance_profile == "local_validity_counterexample"
    assert case.claim_status == "counterexample"


def test_generated_catalog_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "docs" / "generated" / "benchmark_catalog.md").exists()
