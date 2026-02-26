from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "apps" / "api"
PACKAGES_PATH = ROOT / "packages"

for path in (API_PATH, PACKAGES_PATH):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from app.workers.runner import run_once  # noqa: E402


def main() -> None:
    poll_seconds = int(os.getenv("WORKER_POLL_SECONDS", "5"))
    max_cycles = os.getenv("WORKER_MAX_CYCLES")
    cycles = 0

    while True:
        run_once()
        cycles += 1
        if max_cycles and cycles >= int(max_cycles):
            break
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
