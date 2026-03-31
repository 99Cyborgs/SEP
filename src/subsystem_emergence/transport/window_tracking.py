"""Carrier tracking across finite-time windows."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from subsystem_emergence.core.projectors import coherent_projector_deformation


def track_windows(projectors: Sequence[np.ndarray]) -> dict[str, object]:
    """Track coherent carrier deformation across windows."""

    if len(projectors) < 2:
        return {"mean_deformation": 0.0, "max_deformation": 0.0, "trajectory": []}
    trajectory = [
        coherent_projector_deformation(projectors[index + 1], projectors[index])
        for index in range(len(projectors) - 1)
    ]
    return {
        "mean_deformation": float(np.mean(trajectory)),
        "max_deformation": float(np.max(trajectory)),
        "trajectory": trajectory,
    }
