# G3 Report

- Passed: `True`
- Summary: Finite-time transport gate completed.
- Failure labels: carrier_failure

## Criteria
```json
{
  "gate": "G3",
  "benchmark_ids": [
    "BP_Windowed_Transport_Flow",
    "BP_T3_Window_Sensitivity_Pair"
  ],
  "min_singular_gap": 0.01,
  "min_horizon_gain": 0.0,
  "min_autonomy_horizon": 2
}
```

## Metrics
```json
{
  "record_count": 1,
  "reported_record_count": 3,
  "singular_gap": 0.03224704530410183,
  "horizon_gain": 3.0,
  "autonomy_horizon": 6.0,
  "window_sensitivity_autonomy_span": 0.3333333333333333,
  "window_sensitivity_horizon_gain_span": 0.3333333333333333,
  "window_sensitivity_regrouped_horizon_gain": 2.0,
  "window_sensitivity_regrouped_carrier_mean_deformation": 0.48548832264152547,
  "mixed_transport_pair_count": 2,
  "mixed_transport_horizon_gain": 0.0,
  "mixed_transport_carrier_deformation": 0.582583182308787,
  "mixed_transport_regrouped_horizon_gain": 0.0,
  "mixed_transport_pair_horizon_delta": 3.0,
  "mixed_transport_pair_carrier_delta": 0.27397347469965927
}
```