"""Helpers for bundled mobility application benchmarks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .named_flows import (
    build_windowed_named_flow_operators,
    named_flow_fixture,
    named_flow_parameter_set,
)


MOBILITY_FIXTURE_PATHS = {
    "BP_Mobility_Chicago_Corridors": "benchmarks/BP_Mobility_Chicago_Corridors/data/divvy_hyde_park_jan2024.json",
    "BP_Mobility_Downtown_Routing_Instability": "benchmarks/BP_Mobility_Downtown_Routing_Instability/data/divvy_downtown_commute_jan2024.json",
    "BP_Mobility_NYC_East_Corridor": "benchmarks/BP_Mobility_NYC_East_Corridor/data/citibike_east_corridor_jan2024.json",
}


MOBILITY_EVALUATION_CASES: tuple[dict[str, Any], ...] = (
    {
        "case_id": "weekday_reference",
        "base_parameter_id": "reference",
        "profile": "accepted",
        "description": "Baseline weekday commute slice on the full four-station Hyde Park corridor.",
        "overrides": {
            "parameter_id": "weekday_reference",
        },
    },
    {
        "case_id": "weekday_pseudocount_tight",
        "base_parameter_id": "reference",
        "profile": "accepted",
        "description": "Tighter pseudocount smoothing on the weekday slice.",
        "overrides": {
            "parameter_id": "weekday_pseudocount_tight",
            "pseudocount": 0.1,
            "refined_pseudocount": 0.5,
            "case_label": "weekday_commute_tight_smoothing",
        },
    },
    {
        "case_id": "weekday_pseudocount_loose",
        "base_parameter_id": "reference",
        "profile": "accepted",
        "description": "Looser pseudocount smoothing on the weekday slice.",
        "overrides": {
            "parameter_id": "weekday_pseudocount_loose",
            "pseudocount": 0.5,
            "refined_pseudocount": 1.0,
            "case_label": "weekday_commute_loose_smoothing",
        },
    },
    {
        "case_id": "weekday_three_station_corridor",
        "base_parameter_id": "reference",
        "profile": "accepted",
        "description": "Corridor-preserving three-station weekday subset.",
        "overrides": {
            "parameter_id": "weekday_three_station_corridor",
            "station_subset_indices": [0, 1, 2],
            "block_sizes": [2, 1],
            "coherent_rank": 2,
            "case_label": "weekday_commute_three_station_corridor",
        },
    },
    {
        "case_id": "weekday_window_coarsened",
        "base_parameter_id": "reference",
        "profile": "accepted",
        "description": "Weekday slice with the mid-day windows merged into one coarser partition.",
        "overrides": {
            "parameter_id": "weekday_window_coarsened",
            "window_groups": [[0], [1, 2], [3]],
            "window_labels": ["06:00-09:00", "09:00-18:00", "18:00-21:00"],
            "pseudocount": 0.1,
            "refined_pseudocount": 0.2,
            "case_label": "weekday_commute_coarsened_windows",
        },
    },
    {
        "case_id": "weekend_negative",
        "base_parameter_id": "negative_weekend",
        "profile": "failure",
        "description": "Sparse weekend-night slice kept as the instructive negative application case.",
        "overrides": {
            "parameter_id": "weekend_negative",
            "case_label": "weekend_night_negative",
        },
    },
)


def mobility_fixture(
    benchmark_id: str = "BP_Mobility_Chicago_Corridors",
    path: str | Path | None = None,
) -> dict:
    """Load the bundled mobility fixture."""

    return named_flow_fixture(benchmark_id, fixture_paths=MOBILITY_FIXTURE_PATHS, path=path)


def mobility_parameter_set(
    parameter_id: str = "reference",
    overrides: dict[str, Any] | None = None,
    *,
    benchmark_id: str = "BP_Mobility_Chicago_Corridors",
) -> dict:
    """Return one parameterization from the bundled mobility fixture."""

    effective_overrides = dict(overrides or {})
    if "station_subset_indices" in effective_overrides:
        effective_overrides["entity_subset_indices"] = effective_overrides.pop("station_subset_indices")
    parameter_set = named_flow_parameter_set(
        parameter_id,
        effective_overrides,
        benchmark_id=benchmark_id,
        fixture_paths=MOBILITY_FIXTURE_PATHS,
    )
    return {
        **parameter_set,
        "station_subset_indices": list(parameter_set["entity_subset_indices"]),
        "station_names": list(parameter_set["entity_names"]),
        "station_ids": list(parameter_set["entity_ids"]),
        "total_trips": int(parameter_set["total_flow"]),
    }


def build_windowed_mobility_operators(
    parameter_id: str | dict[str, Any] = "reference",
    *,
    pseudocount: float | None = None,
    benchmark_id: str = "BP_Mobility_Chicago_Corridors",
) -> tuple[list[np.ndarray], dict[str, object]]:
    """Construct row-stochastic mobility operators from bundled counts."""

    operators, metadata = build_windowed_named_flow_operators(
        parameter_id,
        benchmark_id=benchmark_id,
        fixture_paths=MOBILITY_FIXTURE_PATHS,
        pseudocount=pseudocount,
    )
    return operators, {
        **metadata,
        "station_names": metadata["entity_names"],
        "station_ids": metadata["entity_ids"],
        "station_subset_indices": metadata["entity_subset_indices"],
    }


def mobility_evaluation_cases() -> list[dict[str, Any]]:
    """Return the fixed Paper E robustness sweep cases."""

    return [dict(case) for case in MOBILITY_EVALUATION_CASES]
