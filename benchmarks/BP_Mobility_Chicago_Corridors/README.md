# BP Mobility Chicago Corridors

## Formal System Definition
A bundled real-data mobility benchmark derived from Divvy January 2024 trip history on a four-station Hyde Park slice in Chicago. Trips are aggregated into ordered local-time windows and converted into row-stochastic station-to-station operators with a documented pseudocount smoother.

## Data Provenance
- source page: `https://divvybikes.com/system-data`
- source archive: `202401-divvy-tripdata.zip`
- domain: public bike-share trip history in Chicago
- bundled fixture: derived counts for four Hyde Park stations so reference runs stay reproducible without a download step

## Station Slice
- `University Ave & 57th St`
- `Ellis Ave & 60th St`
- `Ellis Ave & 55th St`
- `Kimbark Ave & 53rd St`

## Parameter Sets
- `reference`: weekday commute windows `06:00-09:00`, `09:00-12:00`, `15:00-18:00`, `18:00-21:00`
- `negative_weekend`: weekend night windows `19:00-22:00`, `22:00-24:00`, `00:00-03:00`, `03:00-07:00`

## Paper E Evaluation Sweep
- weekday accepted profile: the full weekday commute slice plus four fixed local perturbations
- perturbations:
  - tighter smoothing: pseudocount `0.1`, refined pseudocount `0.5`
  - looser smoothing: pseudocount `0.5`, refined pseudocount `1.0`
  - corridor-preserving station subset: `University Ave & 57th St`, `Ellis Ave & 60th St`, `Ellis Ave & 55th St`
  - coarsened weekday windows: `06:00-09:00`, `09:00-18:00`, `18:00-21:00`
- negative profile: the bundled `negative_weekend` slice, retained as a rejection case

## Application Acceptance Criteria
- usable weekday profile requires all weekday sweep cases to satisfy:
  - singular gap `>= 0.4`
  - coherent projector deformation `<= 0.4`
  - autonomy horizon `>= 3`
  - numerical refinement span `<= 0.2`
  - no `carrier_failure`
  - no `numerical_artifact_failure`
- repository-wide failure taxonomy still records `coupling_failure` when block residual exceeds the global cutoff, but that label remains advisory for this bounded Paper E package.
- weekend-night rejection is expected and should remain explicit in the ledgers and application summary.

## Ground Truth Notes
- This is a real case study, not a theorem-grade planted benchmark.
- The `reference` case is intended as a usable application slice with interpretable corridor structure, not as a claim that all diagnostics are as clean as the synthetic positive families.
- The `negative_weekend` case is intentionally sparse and less coherent; failure labels are expected to remain visible rather than being tuned away.
- Coordinate-rotation robustness is not interpreted literally here because the coordinates are named stations, not anonymous latent basis vectors.

## Expected Failure Modes
- `carrier_failure`
- `coupling_failure`
- `numerical_artifact_failure`

## Reference Commands
- `python benchmarks/BP_Mobility_Chicago_Corridors/generate.py`
- `python benchmarks/BP_Mobility_Chicago_Corridors/run_reference.py`
- `python benchmarks/BP_Mobility_Chicago_Corridors/run_negative_weekend.py`
- `python benchmarks/BP_Mobility_Chicago_Corridors/evaluate_application.py`
- `python benchmarks/BP_Mobility_Chicago_Corridors/generate_paper_e_package.py`
- `python benchmarks/BP_Mobility_Chicago_Corridors/figure_recipe.py`

## Paper E Regeneration
- Run the benchmark outputs in this order:
  - `python benchmarks/BP_Mobility_Chicago_Corridors/run_reference.py`
  - `python benchmarks/BP_Mobility_Chicago_Corridors/run_negative_weekend.py`
  - `python benchmarks/BP_Mobility_Downtown_Routing_Instability/run_reference.py`
  - `python benchmarks/BP_Mobility_Chicago_Corridors/evaluate_application.py`
  - `python benchmarks/BP_Mobility_Chicago_Corridors/generate_paper_e_package.py`
- Generated Paper E artifacts are written to:
  - `figures/paper_E/weekday_leakage.png`
  - `figures/paper_E/weekday_horizon.png`
  - `figures/paper_E/weekend_failure_comparison.png`
  - `figures/paper_E/robustness_summary.md`
