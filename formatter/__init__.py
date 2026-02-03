from __future__ import annotations

from pathlib import Path
import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)

_ROOT = Path(__file__).resolve().parents[1]
_REAL_FORMATTER = _ROOT / "apps" / "formatter" / "formatter"
if _REAL_FORMATTER.exists():
    __path__.append(str(_REAL_FORMATTER))
