from __future__ import annotations

from subsystem_emergence.core.observables import observable_catalog
from subsystem_emergence.io.schema import load_catalog, validate_record


def test_observable_catalog_has_expected_size() -> None:
    assert len(observable_catalog()) == 16
    assert len(load_catalog()) == 16


def test_validate_record_reports_missing_keys() -> None:
    errors = validate_record({"benchmark_id": "x"})
    assert errors
    assert any("missing required key" in error for error in errors)
