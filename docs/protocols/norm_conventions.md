# Norm Conventions

Every benchmark declares a primary norm, a companion norm, and a failure mode for norm dependence.

## Linear And Nonnormal ODE Benchmarks

- primary norm: operator `2`-norm on propagators and projectors
- companion norm: Frobenius norm on commutators or reduced residuals
- rejection rule: if the subsystem claim disappears when moving from operator norm to Frobenius diagnostics, label `coordinate_artifact_failure` or `numerical_artifact_failure` as appropriate

## Markov And Stochastic Benchmarks

- primary norm: total variation or `l1` leakage from a planted state set
- companion norm: `l2`-type spectral diagnostics on the generator or transition operator
- rejection rule: if leakage is low only because a single norm is hiding redistribution, do not accept the benchmark as positive

## Finite-Time Transport Benchmarks

- primary norm: operator `2`-norm on transfer operators and coherent projectors
- companion norm: row-stochastic consistency and coherent overlap diagnostics
- rejection rule: coherent claims fail if they depend on a frozen surrogate or an unstable basis choice

## Weakly Nonlinear Benchmarks

- primary norm: normalized state-energy leakage outside the instantaneous slow carrier
- companion norm: local Jacobian operator norm and curvature diagnostics
- rejection rule: local claims fail once curvature or fast-variable residuals dominate the affine term

## Cross-Benchmark Rule

No subsystem claim is accepted if it is visible only in one norm convention and not corroborated by its companion diagnostic.
