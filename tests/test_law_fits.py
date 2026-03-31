from __future__ import annotations

import numpy as np

from subsystem_emergence.core.law_fits import fit_all_laws


def test_fit_all_laws_returns_three_models() -> None:
    times = np.linspace(0.0, 1.0, 8)
    epsilon = np.full(times.shape, 0.1)
    rho_tau = 0.2 * times
    leakage = epsilon + rho_tau
    results = fit_all_laws(epsilon, rho_tau, leakage)
    assert set(results) == {"L1", "L2", "L3"}
