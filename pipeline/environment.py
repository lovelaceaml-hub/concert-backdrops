"""The effective worker environment, fixed before a Python process starts."""
from __future__ import annotations

import os
from pathlib import Path
import sys


def worker_environment(renderer: str, threads: int = 1) -> dict[str, str]:
    env = dict(os.environ)
    # Historical preparation invokes `python` for one nested analyzer. Keep it
    # on this locked interpreter instead of the host's unrelated executable.
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env.update(PYTHONHASHSEED="0", OPENBLAS_NUM_THREADS="1", LIBGL_ALWAYS_SOFTWARE="1")
    env["OMP_NUM_THREADS"] = "1" if renderer.startswith("p3d") else str(threads)
    if renderer.startswith("p3d"):
        env["LP_NUM_THREADS"] = "1"
    return env
