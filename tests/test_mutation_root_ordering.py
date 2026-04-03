from __future__ import annotations

import pytest

from subsystem_emergence.reports.archive.cross_domain import generate_cross_domain_application_package
from subsystem_emergence.reports.archive.paper_e import generate_paper_e_package
from subsystem_emergence.reports.archive.runtime import ArchiveBypassError, refresh_driver_context
from subsystem_emergence.reports.archive import runtime as archive_runtime
from subsystem_emergence.reports.archive import cross_domain, paper_e


@pytest.mark.parametrize(
    ("module", "generator"),
    (
        (cross_domain, generate_cross_domain_application_package),
        (paper_e, generate_paper_e_package),
    ),
)
def test_mismatched_context_root_fails_before_mutation_root_resolution(monkeypatch, tmp_path, module, generator) -> None:
    resolve_called = False

    def fail_if_called(*args, **kwargs):
        nonlocal resolve_called
        resolve_called = True
        raise AssertionError("resolve_mutation_root should not be invoked before root/context validation completes")

    monkeypatch.setattr(archive_runtime, "_called_from_refresh_driver", lambda: True)
    monkeypatch.setattr(module, "resolve_mutation_root", fail_if_called)

    execution_context = refresh_driver_context(tmp_path / "expected_scratch")

    with pytest.raises(ArchiveBypassError, match="to match requested root"):
        generator(root=tmp_path / "mismatched_root", context=execution_context)

    assert not resolve_called
