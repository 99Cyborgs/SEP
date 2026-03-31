# G2 Report

- Passed: `True`
- Summary: Nonnormal correction gate completed, including delay semigroup correspondence evidence for the fixed-lag sampled-history path.
- Failure labels: coupling_failure, horizon_failure, transient_growth_failure

## Criteria
```json
{
  "gate": "G2",
  "benchmark_ids": [
    "BP_Non_Normal_Shear",
    "BP_Random_Gap_Ensemble",
    "BP_Delay_Coupled_Pair",
    "BP_T2_Same_Spectrum_Pair"
  ],
  "min_transient_amplification": 1.5,
  "required_best_law": "L3",
  "min_improvement_over_l1": 0.0,
  "max_delay_horizon_span": 0.05,
  "max_delay_transient_span": 0.05,
  "max_delay_residual_span": 0.05,
  "max_delay_surrogate_variation": 0.3
}
```

## Metrics
```json
{
  "record_count": 4,
  "reported_record_count": 5,
  "transient_ok": true,
  "law_ok": true,
  "improvement_ok": true,
  "delay_record_count": 1,
  "delay_refinement_ok": true,
  "delay_horizon_span_max": 0.0,
  "delay_transient_span_max": 0.001968326019924121,
  "delay_residual_span_max": 0.003010262354229746,
  "delay_surrogate_span_max": 0.26960680145567595,
  "delay_correspondence_deformation_max": 0.20454773525404954,
  "delay_adjacent_stability_max": 2.236950511288751e-16,
  "pseudospectral_proxy_mean": 7324.915169438522,
  "pseudospectral_proxy_max": 32000.31249694833,
  "same_spectrum_counterexample_count": 1,
  "same_spectrum_gap_difference": 0.0,
  "same_spectrum_transient_amplification_ratio": 11.471747584031247,
  "same_spectrum_l3_minus_l1_rmse": 0.07273397395012299
}
```