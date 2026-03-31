"""Generate a cross-domain non-mobility application evidence package."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from subsystem_emergence.application.acceptance import evaluate_application_acceptance
from subsystem_emergence.io.ledgers import repo_relative_path, repository_root


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _ensure_output(root: Path, relative_path: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _save_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def generate_cross_domain_application_package(root: str | Path | None = None) -> dict:
    """Generate a compact cross-domain non-mobility application package."""

    repo_root = repository_root(Path(root) if root is not None else None)
    cases = {
        "docs_reference": repo_root / "results" / "ledgers" / "BP_Clickstream_Docs_Funnel" / "reference_seed0.json",
        "docs_negative": repo_root / "results" / "ledgers" / "BP_Clickstream_Docs_Funnel" / "negative_detour_seed0.json",
        "support_reference": repo_root / "results" / "ledgers" / "BP_Support_Portal_Funnel" / "reference_seed0.json",
        "support_negative": repo_root / "results" / "ledgers" / "BP_Support_Portal_Funnel" / "negative_detour_seed0.json",
        "workflow_reference": repo_root / "results" / "ledgers" / "BP_Workflow_Queue_Funnel" / "reference_seed0.json",
        "workflow_negative": repo_root / "results" / "ledgers" / "BP_Workflow_Queue_Funnel" / "negative_detour_seed0.json",
    }
    records = {case_id: _load_json(path) for case_id, path in cases.items()}
    statuses = {case_id: evaluate_application_acceptance(record) for case_id, record in records.items()}

    clickstream_path = _ensure_output(repo_root, "figures/cross_domain_navigation/clickstream_cases.png")
    support_path = _ensure_output(repo_root, "figures/cross_domain_navigation/support_cases.png")
    workflow_path = _ensure_output(repo_root, "figures/cross_domain_navigation/workflow_cases.png")
    comparison_path = _ensure_output(repo_root, "figures/cross_domain_navigation/cross_domain_comparison.png")
    summary_json_path = _ensure_output(repo_root, "results/application/cross_domain_navigation/cross_domain_navigation_summary.json")
    summary_md_path = _ensure_output(repo_root, "results/application/cross_domain_navigation/cross_domain_navigation_summary.md")
    manifest_path = _ensure_output(repo_root, "figures/cross_domain_navigation/package_manifest.json")

    metric_names = ["singular_gap", "deformation", "refinement_span"]
    docs_reference = statuses["docs_reference"]["metrics"]
    docs_negative = statuses["docs_negative"]["metrics"]
    support_reference = statuses["support_reference"]["metrics"]
    support_negative = statuses["support_negative"]["metrics"]
    workflow_reference = statuses["workflow_reference"]["metrics"]
    workflow_negative = statuses["workflow_negative"]["metrics"]

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
    _save_figure(clickstream_path)

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
    _save_figure(support_path)

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
    _save_figure(workflow_path)

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
    _save_figure(comparison_path)

    summary = {
        "summary_kind": "cross_domain_navigation_package",
        "acceptance_criteria": statuses["docs_reference"]["package_acceptance_thresholds"],
        "threshold_layers": {
            "clickstream_and_support": {
                "taxonomy_thresholds": statuses["docs_reference"]["taxonomy_thresholds"],
                "package_acceptance_thresholds": statuses["docs_reference"]["package_acceptance_thresholds"],
                "blocking_failure_labels": statuses["docs_reference"]["blocking_failure_labels"],
            },
            "workflow": {
                "taxonomy_thresholds": statuses["workflow_reference"]["taxonomy_thresholds"],
                "package_acceptance_thresholds": statuses["workflow_reference"]["package_acceptance_thresholds"],
                "blocking_failure_labels": statuses["workflow_reference"]["blocking_failure_labels"],
            },
        },
        "cases": [
            {
                "case_id": case_id,
                "benchmark_id": records[case_id]["benchmark_id"],
                "parameter_id": records[case_id]["parameter_id"],
                "accepted": status["accepted"],
                "acceptance_profile": status["acceptance_profile"],
                "metrics": status["metrics"],
                "failure_labels": status["failure_labels"],
                "blocking_failures_present": status["blocking_failures_present"],
                "advisory_failures_present": status["advisory_failures_present"],
                "rejection_reasons": status["rejection_reasons"],
                "ledger_json": repo_relative_path(cases[case_id], repo_root),
            }
            for case_id, status in statuses.items()
        ],
        "aggregate_summary": {
            "accepted_case_count": int(sum(status["accepted"] for status in statuses.values())),
            "rejected_case_count": int(sum(not status["accepted"] for status in statuses.values())),
            "benchmarks": sorted({record["benchmark_id"] for record in records.values()}),
        },
        "notes": [
            "The cross-domain package keeps Paper E mobility-only and treats non-mobility evidence as a separate bounded application track.",
            "Package acceptance is benchmark-local and stricter than the repository-wide failure taxonomy on singular-gap, deformation, horizon, and refinement bounds.",
            "The supported claim is structural only: the coherent transport machinery is not tied to a single mobility, navigation, or workflow fixture.",
        ],
    }
    summary_json_path.write_text(json.dumps(summary, indent=2))
    summary_md_path.write_text(
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
                f"reasons=`{', '.join(case['rejection_reasons']) if case['rejection_reasons'] else 'none'}`, ledger=`{case['ledger_json']}`"
                for case in summary["cases"]
            ]
        )
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
            "clickstream_reference_case": repo_relative_path(cases["docs_reference"], repo_root),
            "clickstream_negative_case": repo_relative_path(cases["docs_negative"], repo_root),
            "support_reference_case": repo_relative_path(cases["support_reference"], repo_root),
            "support_negative_case": repo_relative_path(cases["support_negative"], repo_root),
            "workflow_reference_case": repo_relative_path(cases["workflow_reference"], repo_root),
            "workflow_negative_case": repo_relative_path(cases["workflow_negative"], repo_root),
            "accepted_case_count": summary["aggregate_summary"]["accepted_case_count"],
            "rejected_case_count": summary["aggregate_summary"]["rejected_case_count"],
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    manifest["manifest_json"] = repo_relative_path(manifest_path, repo_root)
    return manifest
