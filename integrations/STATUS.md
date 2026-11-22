# Integration verification

Checked in the cloud Linux workspace during setup on 2026-11-20.

| Check | Result |
| --- | --- |
| MCP package import and version | Passed: `mcp-for-blender 2.3.1` |
| Python dependency hash lock | Passed: `uv pip sync --require-hashes`, 30 packages |
| Add-on installation and enablement | Passed in official Blender `5.2.4 LTS` |
| Isolated Blender startup and preferences | Saved under this checkout's `.tools/blender-profile` |
| External asset and AI generation integrations | All 8 disabled |
| Telemetry | Disabled in both server environment and add-on preferences |
| Listener configuration | `localhost:9876`, remote connections disabled |
| MCP initialize and tool catalog | Passed: 10 advertised tools, expected core tools present |
| Safe-mode enforcement | Passed: `import os` rejected before execution |
| Live MCP call into a Blender GUI | Not tested; Xvfb cannot open local Unix sockets in this workspace |
| Pinned Shotcraft checkout | Verified exact commit `075b548c2405a07b77129eb448b0b504fc60dea3` |
| Shotcraft dependencies | Installed with `npm ci --ignore-scripts` |
| Project skill links | Created for project-scoped Claude Code and Codex clients |
| Workbench and editor version agreement | Passed: Remotion `4.0.484` |
| Workbench production build | Passed: TypeScript and Vite, 307 modules |
| Workbench card index | 150 demo cards, linked editor project recognized |
| Workbench HTTP smoke check | Passed: `/`, `/proj/workbench.ts`, `/src/cards/projectCards.ts` each returned 200 |
| Workbench foreground lifecycle | Passed: startup, HTTP responses, SIGTERM shutdown, exit 0 |
| Workbench browser playback or video export | Not tested by the integration check |
| Automatic client activation | Configuration prepared; current chat was not converted into an MCP client |

Generated evidence is available after running the checks in `.tools/blender-profile/installed.json`, `.tools/mcp-smoke.json`, `.tools/workbench-smoke.json`, and their adjacent logs. These machine-generated files are excluded from version control. No Workbench, MCP server, Blender GUI, Xvfb process, or render job was left running by these checks.

The normal Xvfb attempt exited with `Unable to open socket for local`, `Unable to open socket for unix`, and `Cannot establish any listening sockets`. No attempt was made to change sandbox permissions. Background Blender scripting remains separate from this GUI limitation.
