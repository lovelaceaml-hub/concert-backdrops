#!/usr/bin/env python3
"""Record non-secret tool versions and lockfile hashes with a delivery."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def version(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, cwd=ROOT)
        return {"exit_code": result.returncode, "version": (result.stdout or result.stderr).splitlines()[0]}
    except (OSError, subprocess.TimeoutExpired, IndexError) as error:
        return {"available": False, "error": str(error)}


def main():
    blender = os.environ.get("BLENDER_BIN") or str(ROOT / ".tools/blender-5.2.4-linux-x64/blender")
    if not Path(blender).exists():
        blender = shutil.which("blender") or "blender"
    data = {"platform": platform.platform(), "python": platform.python_version(), "cloud_gpu_provider": None, "tools": {}}
    for name, command in {"blender": [blender, "--version"], "node": ["node", "--version"], "npm": ["npm", "--version"], "uv": ["uv", "--version"], "ffmpeg": ["ffmpeg", "-version"], "chromium": [os.environ.get("CHROMIUM_PATH") or "chromium", "--version"]}.items():
        data["tools"][name] = version(command)
    data["locks"] = {}
    for name in ["uv.lock", "package-lock.json", "infra/toolchain.lock.json"]:
        path = ROOT / name
        if path.exists():
            data["locks"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    data["source_commit"] = version(["git", "rev-parse", "HEAD"]).get("version")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
