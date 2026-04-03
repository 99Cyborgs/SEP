"""Public package surface for the Subsystem Emergence validation engine."""

from .core.observables import observable_catalog
from .docs import sync_generated_docs


def list_benchmarks(*args, **kwargs):
    from .benchmarking import list_benchmarks as _list_benchmarks

    return _list_benchmarks(*args, **kwargs)


def run_benchmark_case(*args, **kwargs):
    from .benchmarking import run_benchmark_case as _run_benchmark_case

    return _run_benchmark_case(*args, **kwargs)


def run_reference_benchmark(*args, **kwargs):
    from .benchmarking import run_reference_benchmark as _run_reference_benchmark

    return _run_reference_benchmark(*args, **kwargs)

__all__ = [
    "list_benchmarks",
    "observable_catalog",
    "run_benchmark_case",
    "run_reference_benchmark",
    "sync_generated_docs",
]

__version__ = "0.3.0"
