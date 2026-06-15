"""Proxy that exposes the installed ``mcp`` package alongside local modules.

``src`` is prepended to ``sys.path`` by ``tests/conftest.py``, so the local
``mcp`` package would otherwise shadow the ``mcp`` library installed from PyPI.
This module locates the installed package, loads it, and appends the local
``src/mcp`` directory to its ``__path__`` so project modules such as
``methodist_mcp_server`` remain importable as ``mcp.methodist_mcp_server``.
"""

import importlib.util
import sys
from pathlib import Path

_local_dir = Path(__file__).parent.resolve()

_installed_dir: Path | None = None
for _entry in sys.path:
    _candidate = Path(_entry).resolve() / "mcp"
    if _candidate == _local_dir:
        continue
    if (_candidate / "__init__.py").is_file():
        _installed_dir = _candidate
        break

if _installed_dir is None:
    raise RuntimeError("Installed 'mcp' package not found on sys.path")

_spec = importlib.util.spec_from_file_location(
    "mcp",
    _installed_dir / "__init__.py",
    submodule_search_locations=[str(_installed_dir)],
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load installed 'mcp' package from {_installed_dir}")

_installed = importlib.util.module_from_spec(_spec)
sys.modules["mcp"] = _installed
_spec.loader.exec_module(_installed)
_installed.__path__.append(str(_local_dir))
