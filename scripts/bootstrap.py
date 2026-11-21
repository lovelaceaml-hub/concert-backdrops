#!/usr/bin/env python3
"""Recreate the production environment from lockfiles, without starting renders."""
import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(*command):
    print("+ " + " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-blender", action="store_true", help="Use an already installed Blender instead of downloading the pinned runtime.")
    parser.add_argument("--skip-integrations", action="store_true")
    parser.add_argument("--skip-browser-install", action="store_true")
    args = parser.parse_args()
    if not (3, 11) <= sys.version_info[:2] < (3, 14):
        raise SystemExit("Use Python 3.11, 3.12, or 3.13")
    missing = [tool for tool in ("git", "uv", "node", "npm", "ffmpeg", "ffprobe") if not shutil.which(tool)]
    if missing:
        raise SystemExit("Install these host tools first: " + ", ".join(missing) + ". See docs/VIDEO-PIPELINE.md or use the supplied CPU container recipe.")
    run("uv", "sync", "--frozen", "--extra", "legacy")
    run("npm", "ci", "--no-audit", "--no-fund")
    if not args.skip_blender and platform.system() == "Linux":
        run(sys.executable, "scripts/install-blender.py")
    if not args.skip_browser_install and not os.environ.get("CHROMIUM_PATH"):
        run("npx", "--no-install", "playwright", "install", "chromium", "--only-shell")
    run("uv", "run", "--frozen", "--extra", "legacy", "python", "tools/setup_fonts.py", "node_modules/@fontsource", "fonts")
    if not args.skip_integrations:
        run(sys.executable, "scripts/install-integrations.py")
    run("npm", "run", "typecheck")
    run("npm", "run", "build")
    run("uv", "run", "--frozen", "--extra", "legacy", "video", "doctor")
    print("Dependency setup complete. Run the documented runtime checks before rendering a full film.")
    print("No render jobs, GPU services, publishing, or Mac rendering were started.")


if __name__ == "__main__":
    main()
