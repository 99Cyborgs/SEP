"""Generate a cross-domain non-mobility application evidence package."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from subsystem_emergence.application.acceptance import evaluate_application_acceptance
from subsystem_emergence.evidence import find_evidence_record
from subsystem_emergence.io.paths import repo_relative_path, resolve_mutation_root
from subsystem_emergence.policy import acceptance_profile, failure_taxonomy_thresholds
from subsystem_emergence.reports.archive.validation import validate_archive_evidence

from .runtime import (
    ArchiveGenerationContext,
    assert_archive_write_allowed,
    assert_context_matches_root,
    require_refresh_driver_context,
)


def _ensure_output(root: Path, relative_path: str, *, context: ArchiveGenerationContext) -> Path:
    path = root / relative_path
    assert_archive_write_allowed(context, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _save_figure(path: Path, *, context: ArchiveGenerationContext) -> None:
    assert_archive_write_allowed(context, path)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def _write_output_text(path: Path, payload: str, *, context: ArchiveGenerationContext) -> None:
    assert_archive_write_allowed(context, path)
    path.write_text(payload)


def _comparison_metrics(record: dict) -> dict[str, float]:
    observables = record["observables"]
    refinement = observables.get("numerical_refinement_metrics") or {}
    return {
        "singular_gap": float(observables.get("singular_gap") or 0.0),
        "coherent_projector_deformation": float(observables.get("coherent_projector_deformation") or 0.0),
        "max_relative_span": float(refinement.get("max_relative_span") or 0.0),
    }


def generate_cross_domain_application_package(
    root: str | Path | None = None,
    *,
    registry_path: str | Path | None = None,
    policy_path: str | Path | None = None,
    context: ArchiveGenerationContext | None = None,
    dangerously_allow_repo_root: bool = False,
) -> dict:
    """Generate a compact cross-domain non-mobility application package."""

    execution_context = require_refresh_driver_context(context, target="cross_domain")
    generation_root = root if root is not None else execution_context.scratch_root
    assert_context_matches_root(execution_context, root=generation_root, target="cross_domain")
    repo_root = resolve_mutation_root(
        generation_root,
        purpose="cross-domain archive package outputs",
        scratch_label="archive_cross_domain",
        allow_repository_root=dangerously_allow_repo_root,
        require_explicit_root=True,
        recommended_action="Use `python -m subsystem_emergence.reports.archive.refresh` or pass a scratch `root` with materialized evidence.",
    )
    resolved_registry_path = (
        Path(registry_path).resolve()
        if registry_path is not None
        else (repo_root / "benchmarks" / "registry.yaml" if (repo_root / "benchmarks" / "registry.yaml").exists() else None)
    )
    resolved_policy_path = (
        Path(policy_path).resolve()
        if policy_path is not None
        else (
            repo_root / "validation" / "acceptance_profiles.yaml"
            if (repo_root / "validation" / "acceptance_profiles.yaml").exists()
            else None
        )
    )
    validate_archive_evidence(repo_root, targets=["cross_domain"])
    cases = {
        "docs_reference": find_evidence_record(repo_root, "BP_Clickstream_Docs_Funnel", "reference"),
        "docs_negative": find_evidence_record(repo_root, "BP_Clickstream_Docs_Funnel", "negative_detour"),
        "support_reference": find_evidence_record(repo_root, "BP_Support_Portal_Funnel", "reference"),
        "support_negative": find_evidence_record(repo_root, "BP_Support_Portal_Funnel", "negative_detour"),
        "workflow_reference": find_evidence_record(repo_root, "BP_Workflow_Queue_Funnel", "reference"),
        "workflow_negative": find_evidence_record(repo_root, "BP_Workflow_Queue_Funnel", "negative_detour"),
    }
    statuses = {
        case_id: evaluate_application_acceptance(
            record,
            registry_path=resolved_registry_path,
            policy_path=resolved_policy_path,
        )
        for case_id, record in cases.items()
    }
    taxonomy = failure_taxonomy_thresholds(path=resolved_policy_path)
    navigation_profile = acceptance_profile(statuses["docs_reference"]["acceptance_profile"], path=resolved_policy_path).to_dict()
    workflow_profile = acceptance_profile(statuses["workflow_reference"]["acceptance_profile"], path=resolved_policy_path).to_dict()

    clickstream_path = _ensure_output(
        repo_root,
        "reports/archive/figures/cross_domain_navigation/clickstream_cases.png",
        context=execution_context,
    )
    support_path = _ensure_output(
        repo_root,
        "reports/archive/figures/cross_domain_navigation/support_cases.png",
        context=execution_context,
    )
    workflow_path = _ensure_output(
        repo_root,
        "reports/archive/figures/cross_domain_navigation/workflow_cases.png",
        context=execution_context,
    )
    comparison_path = _ensure_output(
        repo_root,
        "reports/archive/figures/cross_domain_navigation/cross_domain_comparison.png",
        context=execution_context,
    )
    summary_json_path = _ensure_output(
        repo_root,
        "reports/archive/generated/application/cross_domain_navigation/cross_domain_navigation_summary.json",
        context=execution_context,
    )
    summary_md_path = _ensure_output(
        repo_root,
        "reports/archive/generated/application/cross_domain_navigation/cross_domain_navigation_summary.md",
        context=execution_context,
    )
    manifest_path = _ensure_output(
        repo_root,
        "reports/archive/figures/cross_domain_navigation/package_manifest.json",
        context=execution_context,
    )

    metric_names = ["singular_gap", "deformation", "refinement_span"]
    docs_reference = _comparison_metrics(cases["docs_reference"])
    docs_negative = _comparison_metrics(cases["docs_negative"])
    support_reference = _comparison_metrics(cases["support_reference"])
    support_negative = _comparison_metrics(cases["support_negative"])
    workflow_reference = _comparison_metrics(cases["workflow_reference"])
    workflow_negative = _comparison_metrics(cases["workflow_negative"])

    plt.figure(figsize=(7, 4))
    plt.bar(
        [0, 1, 2],
        [docs_reference["singular_gap"], docs_reference["coherent_projector_deformation"], docs_reference["max_relative_span"]],
        width=0.35,
        label="accepted",
    )
    plt.bar(
        [0.4, 1.4, 2.4],
        [docs_negative["singular_gap"], docs_negative["coherent_projector_deformation"], docs_negative["max_relative_span"]],
        width=0.35,
        label="rejected",
    )
    plt.xticks([0.2, 1.2, 2.2], metric_names)
    plt.ylabel("value")
    plt.title("Clickstream Accepted vs Rejected")
    plt.legend()
    _save_figure(clickstream_path, context=execution_context)

    plt.figure(figsize=(7, 4))
    plt.bar(
        [0, 1, 2],
        [support_reference["singular_gap"], support_reference["coherent_projector_deformation"], support_reference["max_relative_span"]],
        width=0.35,
        label="accepted",
    )
    plt.bar(
        [0.4, 1.4, 2.4],
        [support_negative["singular_gap"], support_negative["coherent_projector_deformation"], support_negative["max_relative_span"]],
        width=0.35,
        label="rejected",
    )
    plt.xticks([0.2, 1.2, 2.2], metric_names)
    plt.ylabel("value")
    plt.title("Support Navigation Accepted vs Rejected")
    plt.legend()
    _save_figure(support_path, context=execution_context)

    plt.figure(figsize=(7, 4))
    plt.bar(
        [0, 1, 2],
        [workflow_reference["singular_gap"], workflow_reference["coherent_projector_deformation"], workflow_reference["max_relative_span"]],
        width=0.35,
        label="accepted",
    )
    plt.bar(
        [0.4, 1.4, 2.4],
        [workflow_negative["singular_gap"], workflow_negative["coherent_projector_deformation"], workflow_negative["max_relative_span"]],
        width=0.35,
        label="rejected",
    )
    plt.xticks([0.2, 1.2, 2.2], metric_names)
    plt.ylabel("value")
    plt.title("Workflow Queue Accepted vs Rejected")
    plt.legend()
    _save_figure(workflow_path, context=execution_context)

    plt.figure(figsize=(8, 4.2))
    labels = ["docs accepted", "docs rejected", "support accepted", "support rejected", "workflow accepted", "workflow rejected"]
    values = [
        docs_reference["singular_gap"],
        docs_negative["singular_gap"],
        support_reference["singular_gap"],
        support_negative["singular_gap"],
        workflow_reference["singular_gap"],
        workflow_negative["singular_gap"],
    ]
    plt.bar(range(len(labels)), values)
    plt.xticks(range(len(labels)), labels, rotation=15)
    plt.ylabel("singular gap")
    plt.title("Cross-Domain Application Comparison")
    _save_figure(comparison_path, context=execution_context)

    summary = {
        "summary_kind": "cross_domain_navigation_package",
        "canonical_source": "results/evidence run manifests plus centralized acceptance profiles",
        "acceptance_profile": statuses["docs_reference"]["acceptance_profile"],
        "threshold_layers": {
            "clickstream_and_support": {
                "failure_taxonomy_thresholds": taxonomy,
                "acceptance_profile": navigation_profile,
            },
            "workflow": {
                "failure_taxonomy_thresholds": taxonomy,
                "acceptance_profile": workflow_profile,
            },
        },
        "cases": [
            {
                "case_id": case_id,
                "benchmark_id": cases[case_id]["benchmark_id"],
                "parameter_id": cases[case_id]["parameter_id"],
                "decision_status": status["decision_status"],
                "accepted": status["accepted"],
                "acceptance_profile": status["acceptance_profile"],
                "metrics": _comparison_metrics(cases[case_id]),
                "failure_labels": status["failure_labels"],
                "blocking_failures_present": status["blocking_failures_present"],
                "advisory_failures_present": status["advisory_failures_present"],
                "rejection_reasons": status["rejection_reasons"],
                "run_manifest": cases[case_id]["metadata"]["artifact_paths"]["run_manifest"],
                "acceptance_decision": cases[case_id]["metadata"]["artifact_paths"]["acceptance_decision"],
                "observables_summary": cases[case_id]["metadata"]["artifact_paths"]["observables_summary"],
            }
            for case_id, status in statuses.items()
        ],
        "aggregate_summary": {
            "accepted_case_count": int(sum(status["accepted"] for status in statuses.values())),
            "rejected_case_count": int(sum(not status["accepted"] for status in statuses.values())),
            "benchmarks": sorted({record["benchmark_id"] for record in cases.values()}),
        },
        "notes": [
            "The cross-domain package keeps Paper E mobility-only and treats non-mobility evidence as a separate bounded application track.",
            "Package acceptance is benchmark-local and stricter than the repository-wide failure taxonomy on singular-gap, deformation, horizon, and refinement bounds.",
            "Archive summaries now read canonical evidence manifests and centralized acceptance decisions instead of raw ledgers.",
            "The supported claim is structural only: the coherent transport machinery is not tied to a single mobility, navigation, or workflow fixture.",
        ],
    }
    _write_output_text(summary_json_path, json.dumps(summary, indent=2), context=execution_context)
    _write_output_text(
        summary_md_path,
        "\n".join(
            [
                "# Cross-Domain Application Summary",
                "",
                f"- Accepted cases: `{summary['aggregate_summary']['accepted_case_count']}`",
                f"- Rejected cases: `{summary['aggregate_summary']['rejected_case_count']}`",
                f"- Benchmarks: `{', '.join(summary['aggregate_summary']['benchmarks'])}`",
                "",
                "## Cases",
            ]
            + [
                f"- `{case['case_id']}`: accepted=`{case['accepted']}`, benchmark=`{case['benchmark_id']}`, "
                f"reasons=`{', '.join(case['rejection_reasons']) if case['rejection_reasons'] else 'none'}`, manifest=`{case['run_manifest']}`"
                for case in summary["cases"]
            ]
        ),
        context=execution_context,
    )

    manifest = {
        "summary_json": repo_relative_path(summary_json_path, repo_root),
        "summary_markdown": repo_relative_path(summary_md_path, repo_root),
        "outputs": {
            "clickstream_cases_png": repo_relative_path(clickstream_path, repo_root),
            "support_cases_png": repo_relative_path(support_path, repo_root),
            "workflow_cases_png": repo_relative_path(workflow_path, repo_root),
            "cross_domain_comparison_png": repo_relative_path(comparison_path, repo_root),
        },
        "evidence_inventory": {
            "clickstream_reference_case": cases["docs_reference"]["metadata"]["artifact_paths"]["run_manifest"],
            "clickstream_negative_case": cases["docs_negative"]["metadata"]["artifact_paths"]["run_manifest"],
            "support_reference_case": cases["support_reference"]["metadata"]["artifact_paths"]["run_manifest"],
            "support_negative_case": cases["support_negative"]["metadata"]["artifact_paths"]["run_manifest"],
            "workflow_reference_case": cases["workflow_reference"]["metadata"]["artifact_paths"]["run_manifest"],
            "workflow_negative_case": cases["workflow_negative"]["metadata"]["artifact_paths"]["run_manifest"],
            "accepted_case_count": summary["aggregate_summary"]["accepted_case_count"],
            "rejected_case_count": summary["aggregate_summary"]["rejected_case_count"],
        },
    }
    _write_output_text(manifest_path, json.dumps(manifest, indent=2), context=execution_context)
    manifest["manifest_json"] = repo_relative_path(manifest_path, repo_root)
    return manifest
