# BP Mobility Downtown Routing Instability

## Formal System Definition
A bundled real-data mobility benchmark derived from Divvy January 2024 weekday trip history on a four-station downtown Chicago slice. Trips are aggregated into ordered commute windows and converted into row-stochastic station-to-station operators with a documented pseudocount smoother.

## Data Provenance
- source page: `https://divvybikes.com/system-data`
- source archive: `202401-divvy-tripdata.zip`
- domain: public bike-share trip history in Chicago
- bundled fixture: derived counts for four downtown stations so the benchmark is reproducible without a download step

## Station Slice
- `Clinton St & Washington Blvd`
- `Kingsbury St & Kinzie St`
- `Wells St & Elm St`
- `State St & Chicago Ave`

## Parameter Set
- `reference`: weekday commute windows `06:00-09:00`, `09:00-12:00`, `15:00-18:00`, `18:00-21:00`

## Negative Application Claim
- This benchmark is intentionally negative.
- The failure mode is routing and geometry instability under a dense downtown coarse graining, not low-count sparsity.
- The selected station set has a few hundred weekday trips, but its coherent carriers drift enough to keep the case rejection-labeled.

## Expected Failure Modes
- `carrier_failure`
- `coupling_failure`

## Reference Commands
- `python benchmarks/BP_Mobility_Downtown_Routing_Instability/generate.py`
- `python benchmarks/BP_Mobility_Downtown_Routing_Instability/run_reference.py`
- `python benchmarks/BP_Mobility_Downtown_Routing_Instability/figure_recipe.py`
