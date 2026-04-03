"""Generate the Paper E figure and table package for the mobility benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from subsystem_emergence.reports.archive.refresh import refresh_archive_outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch-root", default=None)
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            refresh_archive_outputs(
                scratch_root=args.scratch_root,
                targets=["paper_e"],
                promote=args.promote,
                force=args.force,
            ),
            indent=2,
        )
    )

