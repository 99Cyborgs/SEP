"""Shared helpers for figure scripts."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from subsystem_emergence.io.ledgers import load_ledgers


def records() -> list[dict]:
    return load_ledgers(ROOT)


def ensure_output(relative_path: str) -> Path:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def dump_recipe(output_relative_path: str, payload: dict) -> None:
    output = ensure_output(output_relative_path)
    output.write_text(json.dumps(payload, indent=2))
