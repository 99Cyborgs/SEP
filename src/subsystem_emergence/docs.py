"""Derived benchmark-document generators sourced from the canonical registry."""

from __future__ import annotations

from pathlib import Path

import yaml

from subsystem_emergence.io.paths import repository_root
from subsystem_emergence.io.registry import benchmark_definitions, claim_definitions


def _benchmark_readme(definition, claims_by_id: dict[str, dict]) -> str:
    claim_lines = [
        f"- `{claim_id}`: `{claims_by_id[claim_id]['claim_document_path']}` via gate `{claims_by_id[claim_id]['gate']}`"
        for claim_id in definition.claim_refs
    ]
    case_lines = [
        f"- `{case.case_id}`: role=`{case.role}`, claim_status=`{case.claim_status}`, acceptance_profile=`{case.acceptance_profile}`, "
        f"expected_failure_modes=`{', '.join(case.expected_failure_modes) if case.expected_failure_modes else 'none'}`"
        for case in definition.cases
    ]
    fixture_lines = [
        f"- `{fixture.get('kind', 'fixture')}`: `{fixture.get('path', '')}`"
        + (f", source_archive=`{fixture['source_archive']}`" if fixture.get("source_archive") else "")
        for fixture in definition.fixtures
    ] or ["- `synthetic_generator`: runtime-generated benchmark fixture"]
    return "\n".join(
        [
            f"# {definition.title}",
            "",
            "This document is generated from `benchmarks/registry.yaml`. The registry is authoritative; this README is a derived view.",
            "",
            "## Family Contract",
            f"- benchmark_id: `{definition.family_id}`",
            f"- branch: `{definition.branch}`",
            f"- tier: `{definition.theorem_tier}`",
            f"- implementation_status: `{definition.implementation_status}`",
            f"- evidence_class: `{definition.evidence_class}`",
            f"- run_modes: `{', '.join(definition.run_modes)}`",
            "",
            "## Formal System",
            definition.formal_system,
            "",
            "## Claim Links",
            *claim_lines,
            "",
            "## Primary Observables",
            *[f"- `{observable}`" for observable in definition.observables],
            "",
            "## Fixtures",
            *fixture_lines,
            "",
            "## Cases",
            *case_lines,
            "",
            "## Ground Truth Notes",
            *[f"- {note}" for note in definition.ground_truth_notes],
            "",
            "## Canonical Commands",
            f"- `python -m subsystem_emergence.benchmarking run-case {definition.family_id}`",
            f"- `python -m subsystem_emergence.benchmarking sample-parameters {definition.family_id}`",
        ]
    )


def _benchmark_spec(definition) -> dict:
    return {
        "registry_source": "benchmarks/registry.yaml",
        "family_id": definition.family_id,
        "title": definition.title,
        "branch": definition.branch,
        "tier": definition.theorem_tier,
        "phase": definition.phase,
        "description": definition.description,
        "system_class": definition.system_class,
        "state_dimension": definition.state_dimension,
        "formal_system": definition.formal_system,
        "implementation_status": definition.implementation_status,
        "evidence_class": definition.evidence_class,
        "claim_refs": definition.claim_refs,
        "observables": definition.observables,
        "fixtures": definition.fixtures,
        "expected_failure_modes": definition.expected_failure_modes,
        "cases": [case.to_dict() for case in definition.cases],
    }


def _benchmark_catalog(definitions, claims_by_id: dict[str, dict]) -> str:
    lines = [
        "# Benchmark Catalog",
        "",
        "Generated from `benchmarks/registry.yaml`.",
        "",
    ]
    for definition in definitions:
        lines.extend(
            [
                f"## {definition.family_id}",
                f"- title: `{definition.title}`",
                f"- branch: `{definition.branch}`",
                f"- tier: `{definition.theorem_tier}`",
                f"- implementation_status: `{definition.implementation_status}`",
                f"- claims: `{', '.join(definition.claim_refs)}`",
                f"- cases: `{', '.join(case.case_id for case in definition.cases)}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Claims",
            *[
                f"- `{claim_id}`: `{payload['claim_document_path']}` via gate `{payload['gate']}`"
                for claim_id, payload in sorted(claims_by_id.items())
            ],
        ]
    )
    return "\n".join(lines)


def sync_generated_docs(root: str | Path | None = None) -> dict[str, str]:
    """Regenerate derived benchmark docs from the canonical registry."""

    repo_root = repository_root(Path(root) if root is not None else None)
    definitions = benchmark_definitions()
    claims_by_id = {claim.claim_id: claim.to_dict() for claim in claim_definitions()}
    generated: dict[str, str] = {}

    benchmarks_readme = repo_root / "benchmarks" / "README.md"
    benchmarks_readme.write_text(
        "\n".join(
            [
                "# Benchmark Registry",
                "",
                "The canonical source of benchmark truth is `benchmarks/registry.yaml`.",
                "Per-benchmark `README.md` and `spec.yaml` files are generated summaries and must not carry independent thresholds or paper workflows.",
                "",
                "Canonical execution uses benchmark case ids and writes evidence bundles under `results/evidence/`.",
                "Legacy ledger snapshots under `results/ledgers/` are compatibility-only and should not be used as the primary read path.",
                "",
                "Use `python -m subsystem_emergence.benchmarking list` to enumerate families and `python -m subsystem_emergence.benchmarking run-case <benchmark_id>` to execute the default case.",
            ]
        )
    )
    generated["benchmarks_readme"] = "benchmarks/README.md"

    for definition in definitions:
        readme_path = repo_root / definition.readme_path
        readme_path.write_text(_benchmark_readme(definition, claims_by_id))
        spec_path = repo_root / definition.spec_path
        spec_path.write_text(yaml.safe_dump(_benchmark_spec(definition), sort_keys=False, width=120))
        generated[f"{definition.family_id}_readme"] = definition.readme_path
        generated[f"{definition.family_id}_spec"] = definition.spec_path

    generated_dir = repo_root / "docs" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = generated_dir / "benchmark_catalog.md"
    catalog_path.write_text(_benchmark_catalog(definitions, claims_by_id))
    generated["benchmark_catalog"] = "docs/generated/benchmark_catalog.md"
    return generated
