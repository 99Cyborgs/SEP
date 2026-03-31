# Gate Criteria

Each gate has a machine-readable JSON criterion file in `validation/criteria/`. This document states the intent behind those thresholds.

## G1 Linear Validity Gate

- scope: `BP_Linear_Two_Block`, `BP_Nearly_Decomposable_Chain`
- pass condition: spectral gap remains admissible, projector deformation and block residual stay controlled, and `L1` is not grossly outperformed on the positive linear cases
- fail labels: `gap_failure`, `carrier_failure`, `coupling_failure`

## G2 Nonnormal Correction Gate

- scope: `BP_Non_Normal_Shear`, `BP_Random_Gap_Ensemble`, `BP_Delay_Coupled_Pair`
- pass condition: transient amplification is present and `L3` improves held-out error over `L1` on the nonnormal cases
- fail labels: `transient_growth_failure`, `horizon_failure`

## G3 Finite-Time Transport Gate

- scope: `BP_Windowed_Transport_Flow`
- pass condition: coherent-window analysis achieves a nonnegative horizon gain over the frozen surrogate and the singular gap remains admissible
- fail labels: `gap_failure`, `horizon_failure`

## G4 Nonlinear Extension Gate

- scope: `BP_Weakly_Nonlinear_Slow_Manifold`
- pass condition: local curvature is explicit, the horizon is nontrivial, and `L2` is selected over `L1`
- fail labels: `carrier_failure`, `horizon_failure`

## G5 Stochastic Robustness Gate

- scope: `BP_Noisy_Metastable_Network`
- pass condition: ensemble leakage variance and bootstrap interval width remain controlled while the horizon is nontrivial
- fail labels: `gap_failure`, `numerical_artifact_failure`

## G6 Application Transport Gate

- scope: primary identifiability diagnostics plus the declared bounded application evidence matrix
- enforced section 1: coordinate sensitivity and refinement spread remain controlled on the primary theorem-tier records
- enforced section 2: each required application case must match its declared benchmark-local package status; `reference` is not treated as a proxy for acceptance
- reporting rule: benchmark-local package acceptance may be stricter than the global failure taxonomy, and some labels can be advisory in specific application packages
- fail labels: `coordinate_artifact_failure`, `numerical_artifact_failure`
