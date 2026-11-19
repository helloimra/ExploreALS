"""Public CLI entrypoint for deterministic ExploreALS v1.2 registry, SHA-256, and epistemic verification."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from verify_carbon_als import main  # noqa: E402

if __name__ == "__main__":
    main()
