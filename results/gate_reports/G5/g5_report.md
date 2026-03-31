# G5 Report

- Passed: `True`
- Summary: Stochastic robustness gate completed.
- Failure labels: none

## Criteria
```json
{
  "gate": "G5",
  "benchmark_ids": [
    "BP_Noisy_Metastable_Network",
    "BP_T5_Stochastic_Stress_Pair"
  ],
  "max_leakage_variance": 0.25,
  "max_bootstrap_width": 0.2,
  "min_autonomy_horizon": 1.0
}
```

## Metrics
```json
{
  "record_count": 1,
  "reported_record_count": 3,
  "leakage_variance": 0.197593984962406,
  "bootstrap_width": 0.08756249999999999,
  "autonomy_horizon": 11.0,
  "confidence_bounded_horizon": 6.0,
  "estimation_error_proxy": 0.036311180985872424,
  "stochastic_pair_count": 2,
  "stress_bootstrap_width": 0.275,
  "stress_confidence_bounded_horizon": 0.0,
  "stochastic_pair_width_delta": 0.18743750000000003
}
```