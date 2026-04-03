# Archive Write Invariant

`refresh_archive_outputs()` is the sole orchestration authority for tracked archive writes.

Archive generators are enforcement boundaries, not reusable write utilities.

Any archive writer must:

- accept `ArchiveGenerationContext`
- call `require_refresh_driver_context(...)`
- call `assert_context_matches_root(...)` before mutation-root resolution
- call `assert_archive_write_allowed(...)` at the final archive write boundary

Legacy `reports/archive/figures/scripts/*` helpers are historical only and must not mutate tracked archive outputs directly.

The repository-level archive boundary checks scan repository Python sources outside `tests/` for unauthorized `reports/archive` write behavior and helper-mediated bypasses.

Violations must fail CI through `tests/test_archive_write_invariant.py`, `tests/test_mutation_root_ordering.py`, `tests/test_archive_bypass_detection.py`, `tests/test_safe_execution.py`, and `tests/test_archive_reports.py`.
