# BP Mobility NYC East Corridor

## Formal System Definition
A bundled real-data mobility benchmark derived from Citi Bike January 2024 weekday trip history on a four-station Manhattan east-side slice. Trips are aggregated into ordered commute windows and converted into row-stochastic station-to-station operators with a documented pseudocount smoother.

## Data Provenance
- source page: `https://citibikenyc.com/system-data`
- source archive: `202401-citibike-tripdata.zip`
- domain: public bike-share trip history in New York City
- bundled fixture: derived counts for four Manhattan stations so the benchmark is reproducible without a download step

## Station Slice
- `1 Ave & E 68 St`
- `1 Ave & E 62 St`
- `E 44 St & Lexington Ave`
- `E 47 St & Park Ave`

## Parameter Set
- `reference`: weekday commute windows `06:00-09:00`, `09:00-12:00`, `15:00-18:00`, `18:00-21:00`

## Mixed External Application Claim
- This benchmark is intended as a mixed external case, not a clean positive and not a pure sparse failure.
- The station slice has enough weekday traffic and stable numerical refinement, but its carrier deformation and coupling remain too large for acceptance under the Hyde Park Paper E criteria.
- The point of this benchmark is to show bounded cross-dataset evidence rather than another Chicago-only negative.

## Expected Failure Modes
- `carrier_failure`
- `coupling_failure`

## Reference Commands
- `python benchmarks/BP_Mobility_NYC_East_Corridor/generate.py`
- `python benchmarks/BP_Mobility_NYC_East_Corridor/run_reference.py`
- `python benchmarks/BP_Mobility_NYC_East_Corridor/figure_recipe.py`
