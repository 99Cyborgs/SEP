"""Shared helpers for named windowed flow application fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from subsystem_emergence.io.paths import repository_root


def named_flow_fixture(
    benchmark_id: str,
    *,
    fixture_paths: Mapping[str, str],
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load one bundled named-flow fixture."""

    fixture_path = Path(path) if path is not None else repository_root() / fixture_paths[benchmark_id]
    return json.loads(fixture_path.read_text())


def _entity_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    if "states" in fixture:
        return list(fixture["states"])
    if "stations" in fixture:
        return list(fixture["stations"])
    raise KeyError("fixture must define either 'states' or 'stations'")


def _entity_id_key(entities: list[dict[str, Any]]) -> str:
    if not entities:
        return "state_id"
    sample = entities[0]
    if "state_id" in sample:
        return "state_id"
    if "station_id" in sample:
        return "station_id"
    if "id" in sample:
        return "id"
    raise KeyError("entity records must define a stable id field")


def combine_window_counts(raw_window_counts: list[list[list[float]]], window_groups: list[list[int]]) -> list[list[list[float]]]:
    """Aggregate raw count matrices into a coarser ordered partition."""

    combined: list[list[list[float]]] = []
    arrays = [np.asarray(counts, dtype=float) for counts in raw_window_counts]
    for group in window_groups:
        merged = np.zeros_like(arrays[0], dtype=float)
        for index in group:
            merged += arrays[index]
        combined.append(merged.tolist())
    return combined


def window_group_labels(base_labels: list[str], window_groups: list[list[int]]) -> list[str]:
    """Construct readable labels for grouped windows."""

    labels: list[str] = []
    for group in window_groups:
        group_labels = [base_labels[index] for index in group]
        labels.append(group_labels[0] if len(group_labels) == 1 else f"{group_labels[0]} + {group_labels[-1]}")
    return labels


def named_flow_parameter_set(
    parameter_id: str = "reference",
    overrides: dict[str, Any] | None = None,
    *,
    benchmark_id: str,
    fixture_paths: Mapping[str, str],
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Return one parameterization from a bundled named-flow fixture."""

    fixture = named_flow_fixture(benchmark_id, fixture_paths=fixture_paths, path=path)
    if parameter_id not in fixture["parameter_sets"]:
        raise KeyError(f"unknown parameter_id: {parameter_id}")
    parameter_set = fixture["parameter_sets"][parameter_id]
    entities = _entity_records(fixture)
    id_key = _entity_id_key(entities)
    effective_overrides = dict(overrides or {})
    entity_subset = list(effective_overrides.get("entity_subset_indices", range(len(entities))))
    raw_window_counts = parameter_set["raw_window_counts"]
    if "window_groups" in effective_overrides:
        raw_window_counts = combine_window_counts(raw_window_counts, effective_overrides["window_groups"])
    selected_counts: list[list[list[float]]] = []
    for raw_counts in raw_window_counts:
        matrix = np.asarray(raw_counts, dtype=float)[np.ix_(entity_subset, entity_subset)]
        selected_counts.append(matrix.tolist())
    window_labels = parameter_set["window_labels"]
    if "window_groups" in effective_overrides:
        window_labels = effective_overrides.get("window_labels") or window_group_labels(parameter_set["window_labels"], effective_overrides["window_groups"])
    return {
        "parameter_id": effective_overrides.get("parameter_id", parameter_id),
        "base_parameter_id": parameter_id,
        "case_label": effective_overrides.get("case_label", parameter_set["case_label"]),
        "window_labels": window_labels,
        "window_groups": effective_overrides.get("window_groups"),
        "raw_window_counts": selected_counts,
        "total_flow": int(sum(np.asarray(counts, dtype=float).sum() for counts in selected_counts)),
        "eta": float(effective_overrides.get("eta", parameter_set["eta"])),
        "pseudocount": float(effective_overrides.get("pseudocount", parameter_set["pseudocount"])),
        "refined_pseudocount": float(effective_overrides.get("refined_pseudocount", parameter_set["refined_pseudocount"])),
        "coherent_rank": int(effective_overrides.get("coherent_rank", parameter_set["coherent_rank"])),
        "block_sizes": list(effective_overrides.get("block_sizes", parameter_set["block_sizes"])),
        "entity_subset_indices": entity_subset,
        "entity_names": [entities[index]["name"] for index in entity_subset],
        "entity_ids": [entities[index][id_key] for index in entity_subset],
        "benchmark_id": benchmark_id,
    }


def build_windowed_named_flow_operators(
    parameter_id: str | dict[str, Any] = "reference",
    *,
    benchmark_id: str,
    fixture_paths: Mapping[str, str],
    pseudocount: float | None = None,
    path: str | Path | None = None,
) -> tuple[list[np.ndarray], dict[str, object]]:
    """Construct row-stochastic operators from a bundled named-flow fixture."""

    fixture = named_flow_fixture(benchmark_id, fixture_paths=fixture_paths, path=path)
    parameter_set = (
        parameter_id
        if isinstance(parameter_id, dict)
        else named_flow_parameter_set(parameter_id, benchmark_id=benchmark_id, fixture_paths=fixture_paths, path=path)
    )
    smoothing = float(parameter_set["pseudocount"] if pseudocount is None else pseudocount)
    operators: list[np.ndarray] = []
    for raw_counts in parameter_set["raw_window_counts"]:
        counts = np.asarray(raw_counts, dtype=float) + smoothing
        operators.append(counts / counts.sum(axis=1, keepdims=True))
    return operators, {
        "entity_names": parameter_set["entity_names"],
        "entity_ids": parameter_set["entity_ids"],
        "source_page": fixture["source_page"],
        "source_archive": fixture["source_archive"],
        "derivation_summary": fixture["derivation"]["window_rule"],
        "entity_subset_indices": parameter_set["entity_subset_indices"],
        "window_groups": parameter_set.get("window_groups"),
        "window_labels": parameter_set["window_labels"],
        "benchmark_id": benchmark_id,
        "dataset_name": fixture["dataset_name"],
    }
