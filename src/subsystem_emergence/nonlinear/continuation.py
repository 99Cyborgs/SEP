"""Continuation methods for parameter sweeps."""

from __future__ import annotations

from collections.abc import Callable, Iterable


def continue_family(
    parameter_values: Iterable[float],
    runner: Callable[[float], dict[str, object]],
) -> list[dict[str, object]]:
    """Evaluate a benchmark family along a one-parameter continuation."""

    return [runner(float(value)) for value in parameter_values]
