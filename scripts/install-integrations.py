#!/usr/bin/env python3
"""Install pinned Blender MCP and Shotcraft inside this repository only."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations/blender"))
from common import MCP_ENV, MCP_PYTHON, MCP_SERVER, PROFILE, blender_executable, environment

VERSIONS = json.loads((ROOT / "integrations/versions.json").read_text())
SHOTCRAFT = ROOT / ".tools/video-shotcraft"


def run(args: list[str | Path], cwd: Path = ROOT, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run([str(x) for x in args], cwd=cwd, check=True, **kwargs)


def output(args: list[str | Path], cwd: Path = ROOT) -> str:
    return run(args, cwd, capture_output=True, text=True).stdout.strip()


def require(command: str) -> str:
    executable = shutil.which(command)
    if not executable:
        raise RuntimeError(f"{command} is missing. Run the main bootstrap prerequisites first.")
    return executable


def install_mcp(offline: bool) -> None:
    uv = require("uv")
    if not MCP_PYTHON.exists():
        run([uv, "venv", "--python", sys.executable, MCP_ENV])
    args = [uv, "pip", "sync", "--python", MCP_PYTHON, "--require-hashes", ROOT / "integrations/blender/requirements.lock"]
    if offline:
        args.append("--offline")
    run(args)
    run([sys.executable, ROOT / "integrations/blender/launch_mcp.py", "--check"])


def install_addon(explicit_blender: str | None) -> None:
    addon_dir = PROFILE / "scripts/addons"
    addon_dir.mkdir(parents=True, exist_ok=True)
    (PROFILE / "config").mkdir(parents=True, exist_ok=True)
    env = environment()
    run([MCP_SERVER, "install-addon", "--addons-dir", addon_dir], env=env)
    blender = blender_executable(explicit_blender)
    run([blender, "--background", "--factory-startup", "--disable-autoexec", "--python-exit-code", "1", "--python", ROOT / "integrations/blender/configure_addon.py"], env=env)


def project_skill_links() -> None:
    """Expose the unchanged upstream skill to CLI clients in this project."""
    for client in (".agents", ".claude"):
        link = ROOT / client / "skills/video-shotcraft"
        target = os.path.relpath(SHOTCRAFT, link.parent)
        if link.is_symlink():
            if link.resolve() == SHOTCRAFT.resolve():
                continue
            raise RuntimeError(f"Existing skill symlink points elsewhere; preserved: {link}")
        if link.exists():
            raise RuntimeError(f"Existing skill directory is preserved: {link}")
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target, target_is_directory=True)


def install_shotcraft(offline: bool) -> None:
    require("git")
    require("node")
    require("npm")
    pin = VERSIONS["video_shotcraft"]
    if not SHOTCRAFT.exists():
        if offline:
            raise RuntimeError("Shotcraft is not installed; initial checkout requires network access.")
        run(["git", "clone", "--filter=blob:none", "--no-checkout", pin["repository"], SHOTCRAFT])
        run(["git", "checkout", "--detach", pin["commit"]], SHOTCRAFT)
    if not (SHOTCRAFT / ".git").exists():
        raise RuntimeError(f"Refusing to replace a non-git directory: {SHOTCRAFT}")
    origin = output(["git", "remote", "get-url", "origin"], SHOTCRAFT)
    if origin.removesuffix(".git") != pin["repository"].removesuffix(".git"):
        raise RuntimeError(f"Unexpected Shotcraft origin; preserved: {origin}")
    head = output(["git", "rev-parse", "HEAD"], SHOTCRAFT)
    if head != pin["commit"]:
        if output(["git", "status", "--porcelain", "--untracked-files=no"], SHOTCRAFT):
            raise RuntimeError("Shotcraft has edited tracked files; preserve them before changing its version.")
        present = subprocess.run(["git", "cat-file", "-e", pin["commit"] + "^{commit}"], cwd=SHOTCRAFT, capture_output=True).returncode == 0
        if not present:
            if offline:
                raise RuntimeError("The pinned Shotcraft commit is absent from the local checkout.")
            run(["git", "fetch", "origin", pin["commit"]], SHOTCRAFT)
        run(["git", "checkout", "--detach", pin["commit"]], SHOTCRAFT)
    workbench = SHOTCRAFT / "workbench"
    run(["npm", "ci", "--ignore-scripts", *(["--offline"] if offline else [])], workbench)
    run(["node", "scripts/gen-index.mjs"], workbench)
    project_skill_links()


def check(skip_workbench: bool, skip_addon: bool) -> None:
    run([sys.executable, ROOT / "integrations/blender/launch_mcp.py", "--check"])
    if not skip_addon:
        report_file = PROFILE / "installed.json"
        if not report_file.exists():
            raise RuntimeError("The isolated Blender add-on has not been enabled.")
        report = json.loads(report_file.read_text())
        if not report.get("addon_enabled") or report.get("telemetry") or report.get("remote_connections"):
            raise RuntimeError("The isolated Blender add-on configuration is incomplete.")
        print(f"Blender add-on enabled for {report['blender_version']}; live MCP is checked separately.")
    if not skip_workbench:
        run(["node", ROOT / "scripts/launch-workbench.mjs", "--check"])
        for client in (".agents", ".claude"):
            skill = ROOT / client / "skills/video-shotcraft"
            if not skill.is_symlink() or skill.resolve() != SHOTCRAFT.resolve():
                raise RuntimeError(f"Project skill symlink is missing: {skill}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Inspect installation without installing or starting services.")
    parser.add_argument("--offline", action="store_true", help="Use local clones and package caches only.")
    parser.add_argument("--skip-workbench", action="store_true", help="Install only Blender MCP and its isolated add-on.")
    parser.add_argument("--skip-blender-addon", action="store_true", help="Install the MCP server without configuring Blender.")
    parser.add_argument("--blender", help="Blender binary for enabling the isolated add-on.")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Use Python 3.11 or newer for the pinned integration dependencies.")
    try:
        if not args.check:
            (ROOT / ".tools").mkdir(exist_ok=True)
            install_mcp(args.offline)
            if not args.skip_blender_addon:
                install_addon(args.blender)
            if not args.skip_workbench:
                install_shotcraft(args.offline)
        check(args.skip_workbench, args.skip_blender_addon)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Integration setup failed: {exc}", file=sys.stderr)
        return 1
    print("Project integrations are installed. No render or background service was started.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
