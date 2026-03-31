"""Benchmark registry IO helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from subsystem_emergence.core.types import BenchmarkDefinition
from subsystem_emergence.io.ledgers import repository_root


def load_registry(path: str | Path | None = None) -> dict:
    """Load the benchmark registry YAML file."""

    registry_path = Path(path) if path is not None else repository_root() / "benchmarks" / "registry.yaml"
    return yaml.safe_load(registry_path.read_text())


def benchmark_definitions(path: str | Path | None = None) -> list[BenchmarkDefinition]:
    """Return typed benchmark definitions from the registry."""

    data = load_registry(path)
    return [
        BenchmarkDefinition(
            benchmark_id=item["id"],
            branch=item["branch"],
            theorem_tier=item["tier"],
            description=item["description"],
            spec_path=item["spec_path"],
            readme_path=item["readme_path"],
            reference_script=item["reference_script"],
            expected_metrics_path=item["expected_metrics_path"],
            figure_recipe_path=item["figure_recipe_path"],
        )
        for item in data["benchmarks"]
    ]
