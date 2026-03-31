"""Generate the Paper E figure and table package for the mobility benchmark."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from subsystem_emergence.application.paper_e import generate_paper_e_package


if __name__ == "__main__":
    print(json.dumps(generate_paper_e_package(), indent=2))
