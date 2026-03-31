"""Generate the Paper E figure and table package for the mobility case study."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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


def generate_paper_e_package(root: str | Path | None = None) -> dict:
    """Generate manuscript-ready Paper E figures and summary table."""

    repo_root = repository_root(Path(root) if root is not None else None)
    summary_path = repo_root / "results" / "application" / "BP_Mobility_Chicago_Corridors" / "paper_e_application_summary.json"
    summary = _load_json(summary_path)
    weekday_case = next(case for case in summary["cases"] if case["case_id"] == "weekday_reference")
    weekend_case = next(case for case in summary["cases"] if case["case_id"] == "weekend_negative")
    weekday_record = _load_json(repo_root / Path(weekday_case["ledger_json"]))
    weekend_record = _load_json(repo_root / Path(weekend_case["ledger_json"]))
    external_negative_path = repo_root / "results" / "ledgers" / "BP_Mobility_Downtown_Routing_Instability" / "reference_seed0.json"
    external_negative_record = _load_json(external_negative_path)
    external_mixed_path = repo_root / "results" / "ledgers" / "BP_Mobility_NYC_East_Corridor" / "reference_seed0.json"
    external_mixed_record = _load_json(external_mixed_path)

    weekday_leakage_path = _ensure_output(repo_root, "figures/paper_E/weekday_leakage.png")
    weekday_horizon_path = _ensure_output(repo_root, "figures/paper_E/weekday_horizon.png")
    weekend_comparison_path = _ensure_output(repo_root, "figures/paper_E/weekend_failure_comparison.png")
    summary_table_path = _ensure_output(repo_root, "figures/paper_E/robustness_summary.md")
    manifest_path = _ensure_output(repo_root, "figures/paper_E/package_manifest.json")

    leakage = weekday_record["observables"]["leakage_trajectory"] or []
    windows = weekday_record["parameters"]["window_labels"][: len(leakage)]
    plt.figure(figsize=(7, 4))
    plt.plot(windows, leakage, marker="o", linewidth=2, color="#1f5a7a")
    plt.axhline(float(weekday_record["parameters"]["eta"]), linestyle="--", linewidth=1, color="#8a5c2a", label="eta threshold")
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("cumulative leakage")
    plt.title("Paper E: Accepted Weekday Leakage")
    plt.legend()
    _save_figure(weekday_leakage_path)

    observed = float(weekday_record["observables"]["autonomy_horizon"] or 0.0)
    predicted = float(weekday_record["observables"].get("predicted_autonomy_horizon") or 0.0)
    plt.figure(figsize=(5, 4))
    plt.bar(["predicted", "observed"], [predicted, observed], color=["#c98f2d", "#1f5a7a"])
    plt.ylabel("autonomy horizon")
    plt.title("Paper E: Accepted Weekday Horizon")
    _save_figure(weekday_horizon_path)

    metric_names = ["singular_gap", "deformation", "refinement_span"]
    weekday_values = [
        float(weekday_case["application_status"]["metrics"]["singular_gap"]),
        float(weekday_case["application_status"]["metrics"]["coherent_projector_deformation"]),
        float(weekday_case["application_status"]["metrics"]["max_relative_span"]),
    ]
    weekend_values = [
        float(weekend_case["application_status"]["metrics"]["singular_gap"]),
        float(weekend_case["application_status"]["metrics"]["coherent_projector_deformation"]),
        float(weekend_case["application_status"]["metrics"]["max_relative_span"]),
    ]
    external_negative_values = [
        float(external_negative_record["observables"]["singular_gap"]),
        float(external_negative_record["observables"]["coherent_projector_deformation"]),
        float(external_negative_record["observables"]["numerical_refinement_metrics"]["max_relative_span"]),
    ]
    external_mixed_values = [
        float(external_mixed_record["observables"]["singular_gap"]),
        float(external_mixed_record["observables"]["coherent_projector_deformation"]),
        float(external_mixed_record["observables"]["numerical_refinement_metrics"]["max_relative_span"]),
    ]
    indices = range(len(metric_names))
    plt.figure(figsize=(8, 4.2))
    plt.bar([index - 0.36 for index in indices], weekday_values, width=0.18, label="weekday accepted", color="#1f5a7a")
    plt.bar([index - 0.12 for index in indices], weekend_values, width=0.18, label="weekend rejected", color="#aa4c31")
    plt.bar([index + 0.12 for index in indices], external_negative_values, width=0.18, label="downtown rejected", color="#6b3f2b")
    plt.bar([index + 0.36 for index in indices], external_mixed_values, width=0.18, label="NYC mixed", color="#4f8c52")
    plt.xticks(list(indices), metric_names)
    plt.ylabel("value")
    plt.title("Paper E: Accepted, Rejected, and Mixed Mobility Profiles")
    plt.legend()
    _save_figure(weekend_comparison_path)

    aggregate = summary["aggregate_stability_summary"]
    summary_table_path.write_text(
        "\n".join(
            [
                "# Paper E Robustness Summary",
                "",
                "| Quantity | Value |",
                "| --- | --- |",
                f"| Weekday sweep accepted | `{aggregate['weekday_all_cases_accepted']}` |",
                f"| Negative case rejected | `{aggregate['negative_case_rejected']}` |",
                f"| Weekday minimum singular gap | `{aggregate['weekday_min_singular_gap']}` |",
                f"| Weekday maximum deformation | `{aggregate['weekday_max_coherent_projector_deformation']}` |",
                f"| Weekday minimum autonomy horizon | `{aggregate['weekday_min_autonomy_horizon']}` |",
                f"| Weekday maximum refinement span | `{aggregate['weekday_max_refinement_span']}` |",
                f"| Hyde Park weekend failure labels | `{', '.join(aggregate['negative_failure_labels'])}` |",
                f"| External downtown rejection labels | `{', '.join(external_negative_record['failure_labels'])}` |",
                f"| External downtown singular gap | `{external_negative_record['observables']['singular_gap']}` |",
                f"| External downtown deformation | `{external_negative_record['observables']['coherent_projector_deformation']}` |",
                f"| NYC mixed failure labels | `{', '.join(external_mixed_record['failure_labels'])}` |",
                f"| NYC mixed singular gap | `{external_mixed_record['observables']['singular_gap']}` |",
                f"| NYC mixed deformation | `{external_mixed_record['observables']['coherent_projector_deformation']}` |",
                f"| NYC mixed refinement span | `{external_mixed_record['observables']['numerical_refinement_metrics']['max_relative_span']}` |",
            ]
        )
    )

    manifest = {
        "benchmark_id": "BP_Mobility_Chicago_Corridors",
        "summary_json": repo_relative_path(summary_path, repo_root),
        "outputs": {
            "weekday_leakage_png": repo_relative_path(weekday_leakage_path, repo_root),
            "weekday_horizon_png": repo_relative_path(weekday_horizon_path, repo_root),
            "weekend_failure_comparison_png": repo_relative_path(weekend_comparison_path, repo_root),
            "robustness_summary_markdown": repo_relative_path(summary_table_path, repo_root),
        },
        "evidence_inventory": {
            "accepted_weekday_case": weekday_case["ledger_json"],
            "rejected_weekend_case": weekend_case["ledger_json"],
            "external_negative_case": repo_relative_path(external_negative_path, repo_root),
            "external_mixed_case": repo_relative_path(external_mixed_path, repo_root),
            "weekday_sweep_accepted": aggregate["weekday_all_cases_accepted"],
            "negative_case_rejected": aggregate["negative_case_rejected"],
            "external_negative_rejected": "carrier_failure" in external_negative_record["failure_labels"],
            "external_mixed_case_present": True,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    manifest["manifest_json"] = repo_relative_path(manifest_path, repo_root)
    return manifest
