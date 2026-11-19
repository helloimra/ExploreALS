"""Public CLI entrypoint for building the zero-CDN ExploreALS v1.2 interactive Explorer and 8 Monographs."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER_SCRIPT = ROOT / "work" / "phase4_final_synthesis" / "scripts" / "02_render_phase4_synthesis.py"

if __name__ == "__main__":
    if str(RENDER_SCRIPT.parent) not in sys.path:
        sys.path.insert(0, str(RENDER_SCRIPT.parent))
    runpy.run_path(str(RENDER_SCRIPT), run_name="__main__")
