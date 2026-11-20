"""Paths and defaults for the project-isolated Blender integration."""

from __future__ import annotations

import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".tools"
PROFILE = TOOLS / "blender-profile"
MCP_ENV = TOOLS / "blender-mcp-env"
BIN = "Scripts" if os.name == "nt" else "bin"
MCP_PYTHON = MCP_ENV / BIN / ("python.exe" if os.name == "nt" else "python")
MCP_SERVER = MCP_ENV / BIN / ("mcp-for-blender.exe" if os.name == "nt" else "mcp-for-blender")


def environment() -> dict[str, str]:
    """Scope the profile to this checkout and keep network services local."""
    env = os.environ.copy()
    env.update({
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876",
        "BLENDER_MCP_SAFE_MODE": "1",
        "DISABLE_TELEMETRY": "true",
        "BLENDERMCP_NO_UPDATE_CHECK": "1",
        "BLENDER_USER_CONFIG": str(PROFILE / "config"),
        "BLENDER_USER_SCRIPTS": str(PROFILE / "scripts"),
        "BLENDERMCP_ADDONS_DIR": str(PROFILE / "scripts" / "addons"),
    })
    return env


def blender_executable(explicit: str | None = None) -> Path:
    """Prefer the pinned runtime installed by this project's bootstrap."""
    requested = explicit or os.environ.get("BLENDER_BIN")
    if requested:
        executable = Path(requested).expanduser().resolve()
        if not executable.is_file():
            raise FileNotFoundError(f"Blender executable does not exist: {executable}")
        return executable
    pinned = TOOLS / "blender-5.2.4-linux-x64" / "blender"
    if pinned.is_file():
        return pinned
    detected = shutil.which("blender")
    if detected:
        return Path(detected)
    raise FileNotFoundError("Blender is missing. Run scripts/bootstrap.py or set BLENDER_BIN.")
