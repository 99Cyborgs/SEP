# Cross-Domain Application Summary

- Accepted cases: `3`
- Rejected cases: `3`
- Benchmarks: `BP_Clickstream_Docs_Funnel, BP_Support_Portal_Funnel, BP_Workflow_Queue_Funnel`

## Cases
- `docs_reference`: accepted=`True`, benchmark=`BP_Clickstream_Docs_Funnel`, reasons=`none`, ledger=`results/ledgers/BP_Clickstream_Docs_Funnel/reference_seed0.json`
- `docs_negative`: accepted=`False`, benchmark=`BP_Clickstream_Docs_Funnel`, reasons=`singular_gap_below_package_floor, carrier_deformation_above_package_ceiling, blocking_failure_label:carrier_failure, blocking_failure_label:coupling_failure`, ledger=`results/ledgers/BP_Clickstream_Docs_Funnel/negative_detour_seed0.json`
- `support_reference`: accepted=`True`, benchmark=`BP_Support_Portal_Funnel`, reasons=`none`, ledger=`results/ledgers/BP_Support_Portal_Funnel/reference_seed0.json`
- `support_negative`: accepted=`False`, benchmark=`BP_Support_Portal_Funnel`, reasons=`singular_gap_below_package_floor, carrier_deformation_above_package_ceiling, blocking_failure_label:carrier_failure`, ledger=`results/ledgers/BP_Support_Portal_Funnel/negative_detour_seed0.json`
- `workflow_reference`: accepted=`True`, benchmark=`BP_Workflow_Queue_Funnel`, reasons=`none`, ledger=`results/ledgers/BP_Workflow_Queue_Funnel/reference_seed0.json`
- `workflow_negative`: accepted=`False`, benchmark=`BP_Workflow_Queue_Funnel`, reasons=`singular_gap_below_package_floor, carrier_deformation_above_package_ceiling, blocking_failure_label:carrier_failure`, ledger=`results/ledgers/BP_Workflow_Queue_Funnel/negative_detour_seed0.json`