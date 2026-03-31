from __future__ import annotations

import numpy as np

from subsystem_emergence.core.projectors import orth_projector, projector_deformation


def test_orth_projector_is_idempotent() -> None:
    basis = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    projector = orth_projector(basis)
    assert np.allclose(projector @ projector, projector)


def test_projector_deformation_zero_on_self() -> None:
    basis = np.eye(2)
    projector = orth_projector(basis)
    assert projector_deformation(projector, projector) == 0.0
