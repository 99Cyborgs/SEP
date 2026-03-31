# G6 Report

- Passed: `True`
- Summary: Primary identifiability thresholds and the declared application evidence matrix were both enforced.
- Failure labels: carrier_failure, coupling_failure, gap_failure, horizon_failure, numerical_artifact_failure, transient_growth_failure

## Criteria
```json
{
  "gate": "G6",
  "benchmark_ids": [
    "BP_Linear_Two_Block",
    "BP_Nearly_Decomposable_Chain",
    "BP_Non_Normal_Shear",
    "BP_Windowed_Transport_Flow",
    "BP_Weakly_Nonlinear_Slow_Manifold",
    "BP_Noisy_Metastable_Network",
    "BP_Mobility_Chicago_Corridors",
    "BP_Mobility_Downtown_Routing_Instability",
    "BP_Mobility_NYC_East_Corridor",
    "BP_Clickstream_Docs_Funnel",
    "BP_Support_Portal_Funnel",
    "BP_Workflow_Queue_Funnel"
  ],
  "primary_benchmark_ids": [
    "BP_Linear_Two_Block",
    "BP_Nearly_Decomposable_Chain",
    "BP_Non_Normal_Shear",
    "BP_Windowed_Transport_Flow",
    "BP_Weakly_Nonlinear_Slow_Manifold",
    "BP_Noisy_Metastable_Network"
  ],
  "application_benchmark_ids": [
    "BP_Mobility_Chicago_Corridors",
    "BP_Mobility_Downtown_Routing_Instability",
    "BP_Mobility_NYC_East_Corridor",
    "BP_Clickstream_Docs_Funnel",
    "BP_Support_Portal_Funnel",
    "BP_Workflow_Queue_Funnel"
  ],
  "primary_identifiability_thresholds": {
    "max_coordinate_sensitivity": 0.5,
    "max_refinement_span": 0.3
  },
  "application_evidence": {
    "mode": "enforced",
    "min_accepted_cases": 8,
    "min_rejected_cases": 6,
    "required_cases": [
      {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "parameter_id": "weekday_reference",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "parameter_id": "weekday_pseudocount_tight",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "parameter_id": "weekday_pseudocount_loose",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "parameter_id": "weekday_three_station_corridor",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "parameter_id": "weekday_window_coarsened",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "parameter_id": "weekend_negative",
        "seed": 0,
        "expected_status": "rejected"
      },
      {
        "benchmark_id": "BP_Mobility_Downtown_Routing_Instability",
        "parameter_id": "reference",
        "seed": 0,
        "expected_status": "rejected"
      },
      {
        "benchmark_id": "BP_Mobility_NYC_East_Corridor",
        "parameter_id": "reference",
        "seed": 0,
        "expected_status": "rejected"
      },
      {
        "benchmark_id": "BP_Clickstream_Docs_Funnel",
        "parameter_id": "reference",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Clickstream_Docs_Funnel",
        "parameter_id": "negative_detour",
        "seed": 0,
        "expected_status": "rejected"
      },
      {
        "benchmark_id": "BP_Support_Portal_Funnel",
        "parameter_id": "reference",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Support_Portal_Funnel",
        "parameter_id": "negative_detour",
        "seed": 0,
        "expected_status": "rejected"
      },
      {
        "benchmark_id": "BP_Workflow_Queue_Funnel",
        "parameter_id": "reference",
        "seed": 0,
        "expected_status": "accepted"
      },
      {
        "benchmark_id": "BP_Workflow_Queue_Funnel",
        "parameter_id": "negative_detour",
        "seed": 0,
        "expected_status": "rejected"
      }
    ]
  }
}
```

## Metrics
```json
{
  "primary_record_count": 9,
  "primary_benchmark_coverage_count": 6,
  "primary_records_present": true,
  "reported_record_count": 25,
  "coordinate_ok": true,
  "refinement_ok": true,
  "primary_identifiability_enforced": true,
  "application_record_count": 16,
  "application_evidence_mode": "enforced",
  "application_enforced": true,
  "application_enforcement_ok": true,
  "required_application_case_count": 14,
  "matched_application_case_count": 14,
  "mismatched_application_case_count": 0,
  "missing_application_case_count": 0,
  "accepted_application_case_count": 9,
  "rejected_application_case_count": 7,
  "application_failure_label_count": 12,
  "accepted_application_max_refinement_span": 0.19688386694575188,
  "application_case_outcomes": [
    {
      "benchmark_id": "BP_Mobility_Chicago_Corridors",
      "parameter_id": "weekday_reference",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "paper_e_weekday_mobility",
      "rejection_reasons": [],
      "failure_labels": [
        "coupling_failure"
      ],
      "metrics": {
        "singular_gap": 0.4779579958537423,
        "coherent_projector_deformation": 0.3466350164017776,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.12305673252995981,
        "block_residual_norm": 0.812852990727208
      }
    },
    {
      "benchmark_id": "BP_Mobility_Chicago_Corridors",
      "parameter_id": "weekday_pseudocount_tight",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "paper_e_weekday_mobility",
      "rejection_reasons": [],
      "failure_labels": [
        "coupling_failure"
      ],
      "metrics": {
        "singular_gap": 0.4798788008259826,
        "coherent_projector_deformation": 0.34887951898700775,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.06866361017503321,
        "block_residual_norm": 0.755291218258212
      }
    },
    {
      "benchmark_id": "BP_Mobility_Chicago_Corridors",
      "parameter_id": "weekday_pseudocount_loose",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "paper_e_weekday_mobility",
      "rejection_reasons": [],
      "failure_labels": [
        "coupling_failure"
      ],
      "metrics": {
        "singular_gap": 0.47220681333092385,
        "coherent_projector_deformation": 0.3404450586734904,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.11831778506758314,
        "block_residual_norm": 0.8089960229234174
      }
    },
    {
      "benchmark_id": "BP_Mobility_Chicago_Corridors",
      "parameter_id": "weekday_three_station_corridor",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "paper_e_weekday_mobility",
      "rejection_reasons": [],
      "failure_labels": [],
      "metrics": {
        "singular_gap": 0.4971327279903158,
        "coherent_projector_deformation": 0.2746241823969779,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.01986434955425356,
        "block_residual_norm": 0.0
      }
    },
    {
      "benchmark_id": "BP_Mobility_Chicago_Corridors",
      "parameter_id": "weekday_window_coarsened",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "paper_e_weekday_mobility",
      "rejection_reasons": [],
      "failure_labels": [
        "coupling_failure"
      ],
      "metrics": {
        "singular_gap": 0.48504518666220936,
        "coherent_projector_deformation": 0.34965871332450343,
        "autonomy_horizon": 3.0,
        "max_relative_span": 0.01669625133753253,
        "block_residual_norm": 0.7141504432618757
      }
    },
    {
      "benchmark_id": "BP_Mobility_Chicago_Corridors",
      "parameter_id": "weekend_negative",
      "seed": 0,
      "expected_status": "rejected",
      "observed_status": "rejected",
      "accepted": false,
      "acceptance_profile": "paper_e_weekday_mobility",
      "rejection_reasons": [
        "carrier_deformation_above_package_ceiling",
        "refinement_span_above_package_ceiling",
        "blocking_failure_label:carrier_failure",
        "blocking_failure_label:numerical_artifact_failure"
      ],
      "failure_labels": [
        "carrier_failure",
        "coupling_failure",
        "numerical_artifact_failure"
      ],
      "metrics": {
        "singular_gap": 0.44557805565832304,
        "coherent_projector_deformation": 0.5716880737599902,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.4201152023319361,
        "block_residual_norm": 0.7757291927581186
      }
    },
    {
      "benchmark_id": "BP_Mobility_Downtown_Routing_Instability",
      "parameter_id": "reference",
      "seed": 0,
      "expected_status": "rejected",
      "observed_status": "rejected",
      "accepted": false,
      "acceptance_profile": "paper_e_external_mobility",
      "rejection_reasons": [
        "singular_gap_below_package_floor",
        "carrier_deformation_above_package_ceiling",
        "refinement_span_above_package_ceiling",
        "blocking_failure_label:carrier_failure"
      ],
      "failure_labels": [
        "carrier_failure",
        "coupling_failure"
      ],
      "metrics": {
        "singular_gap": 0.2205117224104946,
        "coherent_projector_deformation": 0.98424690113966,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.2051644286561137,
        "block_residual_norm": 0.45510199060917084
      }
    },
    {
      "benchmark_id": "BP_Mobility_NYC_East_Corridor",
      "parameter_id": "reference",
      "seed": 0,
      "expected_status": "rejected",
      "observed_status": "rejected",
      "accepted": false,
      "acceptance_profile": "paper_e_external_mobility",
      "rejection_reasons": [
        "singular_gap_below_package_floor",
        "carrier_deformation_above_package_ceiling",
        "blocking_failure_label:carrier_failure"
      ],
      "failure_labels": [
        "carrier_failure",
        "coupling_failure"
      ],
      "metrics": {
        "singular_gap": 0.32111225405252897,
        "coherent_projector_deformation": 0.4821915250900644,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.06749981753651947,
        "block_residual_norm": 0.9306149284827114
      }
    },
    {
      "benchmark_id": "BP_Clickstream_Docs_Funnel",
      "parameter_id": "reference",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "cross_domain_navigation",
      "rejection_reasons": [],
      "failure_labels": [],
      "metrics": {
        "singular_gap": 0.397374090450784,
        "coherent_projector_deformation": 0.06104729662141483,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.02944618218464895,
        "block_residual_norm": 0.09745792624210901
      }
    },
    {
      "benchmark_id": "BP_Clickstream_Docs_Funnel",
      "parameter_id": "negative_detour",
      "seed": 0,
      "expected_status": "rejected",
      "observed_status": "rejected",
      "accepted": false,
      "acceptance_profile": "cross_domain_navigation",
      "rejection_reasons": [
        "singular_gap_below_package_floor",
        "carrier_deformation_above_package_ceiling",
        "blocking_failure_label:carrier_failure",
        "blocking_failure_label:coupling_failure"
      ],
      "failure_labels": [
        "carrier_failure",
        "coupling_failure"
      ],
      "metrics": {
        "singular_gap": 0.06218421417966025,
        "coherent_projector_deformation": 0.5522009870293002,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.09926308376024906,
        "block_residual_norm": 0.38167769600252666
      }
    },
    {
      "benchmark_id": "BP_Support_Portal_Funnel",
      "parameter_id": "reference",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "cross_domain_navigation",
      "rejection_reasons": [],
      "failure_labels": [],
      "metrics": {
        "singular_gap": 0.3681338864017923,
        "coherent_projector_deformation": 0.05867497195884055,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.19688386694575188,
        "block_residual_norm": 0.09803188230664853
      }
    },
    {
      "benchmark_id": "BP_Support_Portal_Funnel",
      "parameter_id": "negative_detour",
      "seed": 0,
      "expected_status": "rejected",
      "observed_status": "rejected",
      "accepted": false,
      "acceptance_profile": "cross_domain_navigation",
      "rejection_reasons": [
        "singular_gap_below_package_floor",
        "carrier_deformation_above_package_ceiling",
        "blocking_failure_label:carrier_failure"
      ],
      "failure_labels": [
        "carrier_failure",
        "gap_failure"
      ],
      "metrics": {
        "singular_gap": 0.026166628171083138,
        "coherent_projector_deformation": 0.8404729723629586,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.0896284762978004,
        "block_residual_norm": 0.34303233375784103
      }
    },
    {
      "benchmark_id": "BP_Workflow_Queue_Funnel",
      "parameter_id": "reference",
      "seed": 0,
      "expected_status": "accepted",
      "observed_status": "accepted",
      "accepted": true,
      "acceptance_profile": "cross_domain_workflow",
      "rejection_reasons": [],
      "failure_labels": [],
      "metrics": {
        "singular_gap": 0.27845055699038207,
        "coherent_projector_deformation": 0.1380588849603833,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.08016203884909928,
        "block_residual_norm": 0.0528225656500068
      }
    },
    {
      "benchmark_id": "BP_Workflow_Queue_Funnel",
      "parameter_id": "negative_detour",
      "seed": 0,
      "expected_status": "rejected",
      "observed_status": "rejected",
      "accepted": false,
      "acceptance_profile": "cross_domain_workflow",
      "rejection_reasons": [
        "singular_gap_below_package_floor",
        "carrier_deformation_above_package_ceiling",
        "blocking_failure_label:carrier_failure"
      ],
      "failure_labels": [
        "carrier_failure"
      ],
      "metrics": {
        "singular_gap": 0.11700418285419555,
        "coherent_projector_deformation": 0.5847329133437102,
        "autonomy_horizon": 4.0,
        "max_relative_span": 0.11925099110861925,
        "block_residual_norm": 0.2728395482430482
      }
    }
  ],
  "missing_application_cases": []
}
```