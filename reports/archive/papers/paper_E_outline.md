# Paper E. Application-Facing Case Study

## Claim
Across the bundled Chicago and New York mobility cases, the framework yields one bounded accepted Hyde Park weekday commute profile, two distinct Chicago rejection cases, and one mixed New York corridor case with stable refinement but unacceptable carrier and coupling error; no universal transport theorem is claimed beyond these case studies.

## Minimal Theorem Content
- no new universal theorem
- strict preregistered validation and falsification only

## Figure List
- application decomposition of the Hyde Park station slice
- accepted weekday leakage and horizon panels from `weekday_reference`
- fixed robustness sweep summary from `paper_e_application_summary.json`
- joint comparison panel covering the Hyde Park weekend negative, downtown negative, and NYC mixed corridor case

## Evidence Inventory
- `figures/paper_E/weekday_leakage.png`: accepted weekday leakage trajectory against the declared `eta` threshold
- `figures/paper_E/weekday_horizon.png`: predicted versus observed horizon for the accepted weekday reference
- `figures/paper_E/weekend_failure_comparison.png`: side-by-side comparison showing why the weekend and downtown slices are not accepted and why the NYC case remains mixed
- `figures/paper_E/robustness_summary.md`: weekday sweep acceptance plus the Chicago negative and NYC mixed-case summary metrics

## Supported Statement
- accepted weekday evidence:
  - weekday sweep accepted across all five declared perturbations
  - weekday minimum singular gap `0.47220681333092385`
  - weekday maximum coherent projector deformation `0.34965871332450343`
  - weekday maximum refinement span `0.12305673252995981`
- rejected weekend evidence:
  - negative case rejected with `carrier_failure` and `numerical_artifact_failure`
- rejected downtown evidence:
  - external downtown case rejected with `carrier_failure` and `coupling_failure`
- mixed NYC evidence:
  - external NYC case has `total_trips = 1045` and `max_relative_span = 0.06749981753651947`
  - but remains outside acceptance because `coherent_projector_deformation = 0.4821915250900644` and `block_residual_norm = 0.9306149284827114`

## Anticipated Criticism
The mobility evidence is still restricted to bike-share transition data and may not support broad claims outside this data modality.

## Response Strategy
Use the bundled Chicago and New York mobility benchmarks as fully reproducible case studies, keep the claim explicitly case-study-only, require the Hyde Park weekday commute slice to survive a fixed local robustness sweep, and pair it with two rejection cases and one mixed external case rather than smoothing away failure labels.
