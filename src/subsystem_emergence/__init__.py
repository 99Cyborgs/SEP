"""Public package surface for the Subsystem Emergence research suite."""

from .benchmarking import list_benchmarks, run_reference_benchmark
from .core.observables import observable_catalog

__all__ = [
    "list_benchmarks",
    "observable_catalog",
    "run_reference_benchmark",
]

__version__ = "0.2.0"
