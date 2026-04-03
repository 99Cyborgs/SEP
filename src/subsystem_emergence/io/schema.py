"""Observable schema loading."""

from __future__ import annotations

import json
from pathlib import Path

from subsystem_emergence.core.observables import observable_catalog
from subsystem_emergence.io.paths import repository_root


def load_schema(path: str | Path | None = None) -> dict:
    """Load the canonical run-record schema."""

    schema_path = Path(path) if path is not None else repository_root() / "observables" / "schema.json"
    return json.loads(schema_path.read_text())


def load_catalog(path: str | Path | None = None) -> list[dict]:
    """Load or synthesize the observable catalog."""

    if path is None:
        catalog_path = repository_root() / "observables" / "catalog.json"
        if catalog_path.exists():
            return json.loads(catalog_path.read_text())
        return [definition.to_dict() for definition in observable_catalog()]
    return json.loads(Path(path).read_text())


def validate_record(record: dict) -> list[str]:
    """Perform lightweight schema validation without extra dependencies."""

    errors: list[str] = []
    required_top_level = [
        "benchmark_id",
        "branch",
        "theorem_tier",
        "parameter_id",
        "seed",
        "parameters",
        "metadata",
        "observables",
    ]
    for key in required_top_level:
        if key not in record:
            errors.append(f"missing required key: {key}")
    if "observables" in record:
        for definition in observable_catalog():
            if definition.key not in record["observables"]:
                errors.append(f"missing observable: {definition.key}")
    return errors
