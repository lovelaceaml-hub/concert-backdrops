#!/usr/bin/env python3
"""Start the pinned MCP server over stdio, without starting Blender."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

from common import MCP_PYTHON, MCP_SERVER, ROOT, environment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check the installed server and exit.")
    args = parser.parse_args()
    if not MCP_SERVER.is_file() or not MCP_PYTHON.is_file():
        parser.error("Run python3 scripts/install-integrations.py in the repository first.")
    if args.check:
        result = subprocess.run(
            [str(MCP_PYTHON), "-c", "import importlib.metadata; print(importlib.metadata.version('mcp-for-blender'))"],
            capture_output=True, text=True, check=True,
        )
        version = result.stdout.strip()
        expected = json.loads((ROOT / "integrations/versions.json").read_text())["blender_mcp"]["version"]
        if version != expected:
            parser.error(f"Installed MCP version {version} does not match pinned {expected}.")
        print(json.dumps({"package": "mcp-for-blender", "version": version, "transport": "stdio", "blender_endpoint": "localhost:9876", "safe_mode": True, "telemetry": False}))
        return 0
    os.chdir(ROOT)
    os.execve(str(MCP_SERVER), [str(MCP_SERVER)], environment())
    return 0


if __name__ == "__main__":
    sys.exit(main())
