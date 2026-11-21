#!/usr/bin/env python3
"""Verify MCP stdio and safe mode; optionally inspect a running Blender GUI."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys

from common import MCP_ENV, MCP_PYTHON, ROOT, environment


def text_content(result) -> str:
    return "\n".join(item.text for item in result.content if item.type == "text")


async def smoke(live: bool) -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=str(MCP_PYTHON),
        args=[str(ROOT / "integrations/blender/launch_mcp.py")],
        cwd=str(ROOT),
        env=environment(),
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            names = sorted(tool.name for tool in tools.tools)
            required = {"execute_blender_code", "get_scene_info", "get_addon_status", "look"}
            if not required.issubset(names):
                raise RuntimeError(f"MCP server is missing expected tools: {sorted(required - set(names))}")
            rejection = await session.call_tool("execute_blender_code", {
                "code": "import os",
                "user_prompt": "Set all of this up except for the cloud GPU provider",
            })
            if "Rejected by safe mode" not in text_content(rejection):
                raise RuntimeError("Expected the server to reject a non-allowlisted import.")
            report = {
                "mcp_stdio_handshake": "passed",
                "server_name": initialized.serverInfo.name,
                "tool_count": len(names),
                "required_tools_present": True,
                "safe_mode_rejection": "passed",
                "live_blender_connection": "not_tested",
            }
            if live:
                result = await session.call_tool("execute_blender_code", {
                    "code": "import bpy\nprint('PIPELINE_MCP_CONNECTED', bpy.app.version_string)",
                    "user_prompt": "Set all of this up except for the cloud GPU provider",
                })
                message = text_content(result)
                if result.isError or "PIPELINE_MCP_CONNECTED" not in message:
                    raise RuntimeError(f"Live Blender check failed: {message}")
                report["live_blender_connection"] = "passed"
                report["live_blender_result"] = message
            return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Also read the version from an already-running isolated Blender GUI.")
    parser.add_argument("--report", type=Path, default=ROOT / ".tools/mcp-smoke.json")
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != MCP_ENV.resolve():
        if not MCP_PYTHON.is_file():
            parser.error("Install the project integrations first.")
        os.execv(str(MCP_PYTHON), [str(MCP_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])
    report = asyncio.run(asyncio.wait_for(smoke(args.live), timeout=45))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
