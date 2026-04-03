"""Plot projector deformation against reduced coupling."""

from __future__ import annotations

import matplotlib.pyplot as plt

from common import ensure_output, records, save_figure


if __name__ == "__main__":
    data = records()
    plt.figure(figsize=(6, 4))
    for record in data:
        deformation = record["observables"]["projector_deformation"]
        if deformation is None:
            deformation = record["observables"]["coherent_projector_deformation"]
        if deformation is None:
            continue
        rho = record["observables"]["block_residual_norm"] or 0.0
        plt.scatter(float(deformation), float(rho), label=record["benchmark_id"])
    plt.xlabel("projector deformation")
    plt.ylabel("block residual norm")
    plt.title("Projector Deformation Scaling")
    plt.legend(fontsize=7)
    save_figure(ensure_output("reports/archive/figures/paper_A/projector_deformation_scaling.png"))

