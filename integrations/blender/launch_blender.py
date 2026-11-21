#!/usr/bin/env python3
"""Launch the isolated Blender GUI for MCP, optionally under an existing Xvfb."""

from __future__ import annotations

import argparse
import os
import platform
import sys

from common import PROFILE, ROOT, blender_executable, environment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", help="Explicit Blender executable; otherwise BLENDER_BIN or bootstrap runtime.")
    parser.add_argument("--check", action="store_true", help="Validate installation without opening the GUI.")
    args = parser.parse_args()
    executable = blender_executable(args.blender)
    if not (PROFILE / "installed.json").exists():
        parser.error("Run python3 scripts/install-integrations.py to enable the isolated add-on first.")
    if args.check:
        print(f"Blender: {executable}\nProfile: {PROFILE}\nMCP: localhost:9876")
        return 0
    if platform.system() == "Darwin":
        parser.error("This workflow runs in the cloud. Start it in the Linux workspace, not on the Mac.")
    if platform.system() == "Linux" and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        parser.error("MCP needs Blender's GUI event loop. Use a Linux desktop or xvfb-run -a python3 integrations/blender/launch_blender.py. Background rendering uses the separate render pipeline.")
    os.chdir(ROOT)
    env = environment()
    env["LIBGL_ALWAYS_SOFTWARE"] = "1"
    os.execve(str(executable), [str(executable), "--disable-autoexec"], env)
    return 0


if __name__ == "__main__":
    sys.exit(main())
