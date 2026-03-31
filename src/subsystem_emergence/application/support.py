"""Helpers for bundled support-navigation application benchmarks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .named_flows import (
    build_windowed_named_flow_operators,
    named_flow_fixture,
    named_flow_parameter_set,
)


SUPPORT_FIXTURE_PATHS = {
    "BP_Support_Portal_Funnel": "benchmarks/BP_Support_Portal_Funnel/data/support_navigation_funnel_q1_2026.json",
}


def support_fixture(
    benchmark_id: str = "BP_Support_Portal_Funnel",
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load the bundled support-navigation fixture."""

    return named_flow_fixture(benchmark_id, fixture_paths=SUPPORT_FIXTURE_PATHS, path=path)


def support_parameter_set(
    parameter_id: str = "reference",
    overrides: dict[str, Any] | None = None,
    *,
    benchmark_id: str = "BP_Support_Portal_Funnel",
) -> dict[str, Any]:
    """Return one parameterization from the bundled support-navigation fixture."""

    parameter_set = named_flow_parameter_set(
        parameter_id,
        overrides,
        benchmark_id=benchmark_id,
        fixture_paths=SUPPORT_FIXTURE_PATHS,
    )
    return {
        **parameter_set,
        "page_names": list(parameter_set["entity_names"]),
        "page_ids": list(parameter_set["entity_ids"]),
        "page_subset_indices": list(parameter_set["entity_subset_indices"]),
        "total_sessions": int(parameter_set["total_flow"]),
    }


def build_windowed_support_operators(
    parameter_id: str | dict[str, Any] = "reference",
    *,
    pseudocount: float | None = None,
    benchmark_id: str = "BP_Support_Portal_Funnel",
) -> tuple[list[np.ndarray], dict[str, object]]:
    """Construct row-stochastic support-navigation operators from bundled counts."""

    operators, metadata = build_windowed_named_flow_operators(
        parameter_id,
        benchmark_id=benchmark_id,
        fixture_paths=SUPPORT_FIXTURE_PATHS,
        pseudocount=pseudocount,
    )
    return operators, {
        **metadata,
        "page_names": metadata["entity_names"],
        "page_ids": metadata["entity_ids"],
        "page_subset_indices": metadata["entity_subset_indices"],
    }
