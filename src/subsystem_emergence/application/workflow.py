"""Helpers for bundled workflow-queue application benchmarks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .named_flows import (
    build_windowed_named_flow_operators,
    named_flow_fixture,
    named_flow_parameter_set,
)


WORKFLOW_FIXTURE_PATHS = {
    "BP_Workflow_Queue_Funnel": "benchmarks/BP_Workflow_Queue_Funnel/data/workflow_queue_funnel_q1_2026.json",
}


def workflow_fixture(
    benchmark_id: str = "BP_Workflow_Queue_Funnel",
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load the bundled workflow-queue fixture."""

    return named_flow_fixture(benchmark_id, fixture_paths=WORKFLOW_FIXTURE_PATHS, path=path)


def workflow_parameter_set(
    parameter_id: str = "reference",
    overrides: dict[str, Any] | None = None,
    *,
    benchmark_id: str = "BP_Workflow_Queue_Funnel",
) -> dict[str, Any]:
    """Return one parameterization from the bundled workflow fixture."""

    parameter_set = named_flow_parameter_set(
        parameter_id,
        overrides,
        benchmark_id=benchmark_id,
        fixture_paths=WORKFLOW_FIXTURE_PATHS,
    )
    return {
        **parameter_set,
        "stage_names": list(parameter_set["entity_names"]),
        "stage_ids": list(parameter_set["entity_ids"]),
        "stage_subset_indices": list(parameter_set["entity_subset_indices"]),
        "total_cases": int(parameter_set["total_flow"]),
    }


def build_windowed_workflow_operators(
    parameter_id: str | dict[str, Any] = "reference",
    *,
    pseudocount: float | None = None,
    benchmark_id: str = "BP_Workflow_Queue_Funnel",
) -> tuple[list[np.ndarray], dict[str, object]]:
    """Construct row-stochastic workflow operators from bundled counts."""

    operators, metadata = build_windowed_named_flow_operators(
        parameter_id,
        benchmark_id=benchmark_id,
        fixture_paths=WORKFLOW_FIXTURE_PATHS,
        pseudocount=pseudocount,
    )
    return operators, {
        **metadata,
        "stage_names": metadata["entity_names"],
        "stage_ids": metadata["entity_ids"],
        "stage_subset_indices": metadata["entity_subset_indices"],
    }
