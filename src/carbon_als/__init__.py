"""CarbonALS shared computational biology, dataset loader, structural, allostery/PKPD, and verification library."""
from __future__ import annotations

import importlib
from types import ModuleType

__version__ = "0.5.9"
__all__ = [
    "accessions",
    "allostery_pkpd",
    "alphagenome_polarity",
    "io_guards",
    "loaders",
    "mmcif_parser",
    "skill_cli",
    "splice_design",
]


def __getattr__(name: str) -> ModuleType:
    """PEP 562 lazy submodule loader so lightweight modules (e.g. alphagenome_polarity) import cleanly without statsmodels/pandas."""
    if name in __all__:
        mod = importlib.import_module(f".{name}", __name__)
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
