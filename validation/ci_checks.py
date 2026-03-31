"""Continuous-integration style structural checks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from subsystem_emergence.io.registry import load_registry
from subsystem_emergence.io.schema import load_catalog, load_schema

REQUIRED_PATHS = [
    ".github/workflows/ci.yml",
    "docs/theorem_notes/T1_linear_autonomous.tex",
    "docs/theorem_notes/T5_stochastic.tex",
    "benchmarks/registry.yaml",
    "observables/schema.json",
    "observables/catalog.json",
    "validation/gate_G1.py",
    "validation/gate_G6.py",
]

FORBIDDEN_DIR_NAMES = {"__pycache__", ".pytest_cache", "build", "dist"}
FORBIDDEN_TMP_ARCHIVE_SUFFIXES = {".zip", ".whl", ".tar", ".gz", ".bz2", ".7z"}
ABSOLUTE_PATH_PATTERN = re.compile(r"([A-Za-z]:\\\\|/Users/|/home/)")
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".tex"}


def main() -> None:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")
    registry = load_registry("benchmarks/registry.yaml")
    schema = load_schema("observables/schema.json")
    catalog = load_catalog("observables/catalog.json")
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
    for path in [Path("README.md"), *sorted(Path("docs").rglob("*"))]:
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        contents = path.read_text()
        if ABSOLUTE_PATH_PATTERN.search(contents):
            portability_hits.append(str(path))
    if portability_hits:
        raise SystemExit(f"Absolute local filesystem paths remain in text docs: {portability_hits}")
    summary = {
        "registry_count": len(registry["benchmarks"]),
        "schema_required": len(schema["properties"]["observables"]["required"]),
        "catalog_count": len(catalog),
        "forbidden_generated_dir_count": len(forbidden_generated_dirs),
        "tmp_archive_count": len(tmp_archives),
        "absolute_path_doc_count": len(portability_hits),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
