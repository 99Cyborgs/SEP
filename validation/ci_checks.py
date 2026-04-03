"""Continuous-integration style structural checks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from subsystem_emergence.io.registry import benchmark_definitions, claim_definitions, load_registry
from subsystem_emergence.io.schema import load_catalog, load_schema
from subsystem_emergence.policy import load_acceptance_policy

REQUIRED_PATHS = [
    ".github/workflows/ci.yml",
    "docs/theorem_notes/T1_linear_autonomous.tex",
    "docs/theorem_notes/T5_stochastic.tex",
    "benchmarks/registry.yaml",
    "validation/acceptance_profiles.yaml",
    "validation/schemas/benchmark_registry.schema.json",
    "validation/schemas/benchmark_case.schema.json",
    "validation/schemas/acceptance_profile.schema.json",
    "validation/schemas/run_artifact_bundle.schema.json",
    "validation/schemas/failure_record.schema.json",
    "validation/schemas/claim_traceability.schema.json",
    "docs/generated/benchmark_catalog.md",
    "reports/archive/README.md",
    "reports/archive/benchmark_scripts/generate_paper_e_package.py",
    "reports/archive/figures/scripts/common.py",
    "observables/schema.json",
    "observables/catalog.json",
    "validation/gate_G1.py",
    "validation/gate_G6.py",
]

FORBIDDEN_DIR_NAMES = {"__pycache__", ".pytest_cache", "build", "dist"}
FORBIDDEN_TMP_ARCHIVE_SUFFIXES = {".zip", ".whl", ".tar", ".gz", ".bz2", ".7z"}
ABSOLUTE_PATH_PATTERN = re.compile(r"([A-Za-z]:\\\\|/Users/|/home/)")
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".tex"}
FORBIDDEN_CANONICAL_DOC_PATTERNS = ("Paper E", "figure_recipe.py", "generate_paper_e_package.py")


def main() -> None:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")
    registry = load_registry("benchmarks/registry.yaml")
    policy = load_acceptance_policy("validation/acceptance_profiles.yaml")
    schema = load_schema("observables/schema.json")
    catalog = load_catalog("observables/catalog.json")
    benchmarks = benchmark_definitions("benchmarks/registry.yaml")
    claims = claim_definitions("benchmarks/registry.yaml")
    acceptance_profiles = policy["acceptance_profiles"]
    missing_acceptance_profiles = sorted(
        {
            case.acceptance_profile
            for benchmark in benchmarks
            for case in benchmark.cases
            if case.acceptance_profile not in acceptance_profiles
        }
    )
    if missing_acceptance_profiles:
        raise SystemExit(f"Registry references undefined acceptance profiles: {missing_acceptance_profiles}")
    orphan_claim_refs = sorted(
        {
            claim_ref
            for benchmark in benchmarks
            for claim_ref in benchmark.claim_refs
            if claim_ref not in {claim.claim_id for claim in claims}
        }
    )
    if orphan_claim_refs:
        raise SystemExit(f"Registry references undefined claims: {orphan_claim_refs}")
    forbidden_dirs = sorted(
        str(path)
        for path in Path(".").rglob("*")
        if path.is_dir() and path.name in FORBIDDEN_DIR_NAMES
    )
    forbidden_egg_info = sorted(
        str(path) for path in Path(".").rglob("*.egg-info") if path.is_dir()
    )
    forbidden_generated_dirs = forbidden_dirs + forbidden_egg_info
    if forbidden_generated_dirs:
        raise SystemExit(
            "Forbidden generated directories present in snapshot: "
            f"{forbidden_generated_dirs}"
        )
    tmp_archives = sorted(
        str(path)
        for path in Path("tmp").rglob("*")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_TMP_ARCHIVE_SUFFIXES
    ) if Path("tmp").exists() else []
    if tmp_archives:
        raise SystemExit(f"Raw archives remain under tmp/: {tmp_archives}")
    portability_hits = []
    canonical_doc_hits = []
    for path in [Path("README.md"), *sorted(Path("benchmarks").rglob("README.md")), *sorted(Path("docs").rglob("*"))]:
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        contents = path.read_text()
        if ABSOLUTE_PATH_PATTERN.search(contents):
            portability_hits.append(str(path))
        if path.suffix.lower() == ".md":
            for pattern in FORBIDDEN_CANONICAL_DOC_PATTERNS:
                if pattern in contents:
                    canonical_doc_hits.append(f"{path}:{pattern}")
    if portability_hits:
        raise SystemExit(f"Absolute local filesystem paths remain in text docs: {portability_hits}")
    if canonical_doc_hits:
        raise SystemExit(f"Canonical docs still reference demoted paper workflows: {canonical_doc_hits}")
    if Path("docs/papers").exists():
        raise SystemExit("docs/papers should be archived under reports/archive/")
    if Path("figures").exists():
        raise SystemExit("figures/ should be archived under reports/archive/figures/")
    if Path("results/application").exists():
        raise SystemExit("results/application/ should be archived under reports/archive/generated/application/")
    summary = {
        "registry_count": len(registry["benchmarks"]),
        "claim_count": len(registry["claims"]),
        "acceptance_profile_count": len(policy["acceptance_profiles"]),
        "schema_required": len(schema["properties"]["observables"]["required"]),
        "catalog_count": len(catalog),
        "benchmark_case_count": sum(len(benchmark.cases) for benchmark in benchmarks),
        "forbidden_generated_dir_count": len(forbidden_generated_dirs),
        "tmp_archive_count": len(tmp_archives),
        "absolute_path_doc_count": len(portability_hits),
        "canonical_doc_paper_reference_count": len(canonical_doc_hits),
        "deprecated_top_level_roots_present": int(Path("figures").exists()) + int(Path("results/application").exists()),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
