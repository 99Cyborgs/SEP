from __future__ import annotations

import numpy as np

from subsystem_emergence.core.leakage import autonomous_leakage, reduced_block_leakage


def test_autonomous_leakage_nonnegative() -> None:
    generator = np.diag([-0.1, -1.0])
    projector = np.array([[1.0, 0.0], [0.0, 0.0]])
    assert autonomous_leakage(generator, projector, 1.0) >= 0.0


def test_reduced_block_leakage_nonnegative() -> None:
    reduced = np.array([[-0.1, 0.05], [0.0, -0.2]])
    assert reduced_block_leakage(reduced, [1, 1], 1.0) >= 0.0
