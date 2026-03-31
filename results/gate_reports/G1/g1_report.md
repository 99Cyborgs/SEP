# G1 Report

- Passed: `True`
- Summary: Linear validity gate completed.
- Failure labels: none

## Criteria
```json
{
  "gate": "G1",
  "benchmark_ids": [
    "BP_Linear_Two_Block",
    "BP_Nearly_Decomposable_Chain"
  ],
  "min_gap": 0.03,
  "max_projector_deformation": 0.35,
  "max_block_residual": 0.35,
  "max_l1_test_rmse": 0.35,
  "min_horizon_ratio": 0.45
}
```

## Metrics
```json
{
  "record_count": 5,
  "gap_ok": true,
  "deformation_ok": true,
  "residual_ok": true,
  "l1_ok": true,
  "horizon_ok": true
}
```