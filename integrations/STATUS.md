# Integration verification

The latest owner priorities ([PR #114](https://github.com/lovelaceaml-hub/concert-backdrops/pull/114)) authorize: make the retained tools work and be reusable for every song; integrate proven quality gains into the existing engine; then simplify status, stale PRs and distributed rendering. Try permitted cloud routes first for browser/Remotion/live-Blender sandbox limits. Use the owner's Mac only if no cloud route works and explain why; retain the separate GPU/load/priority conditions. The current deliverable is the complete Claude handoff; these priorities guide continuation.

## Current status, November 23, 2026 UTC

The retained tools now run in cloud environments. Current evidence:

**GitHub Actions cloud runner.** The Video tool proofs workflow ([run 45125796332](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45125796332), on branch `claude/video-tools-working`, since merged to `main`) passed these checks: setup, browser doctor, Three.js frame capture, pipeline preview render, Remotion assembly, Blender background render, the reusable song scene, and Blender MCP over stdio plus the live GUI under Xvfb. Pinned versions in use: Blender 5.2.4 LTS, Remotion 4.0.484, Video Shotcraft commit `075b548c2405a07b77129eb448b0b504fc60dea3`, and MCP for Blender 2.3.1.

**Claude Code cloud session (November 23).** This session's sandbox allowed browser sockets and Xvfb, so the following ran here:

1. Full setup with `python3 scripts/bootstrap.py` completed with no errors: Blender 5.2.4 LTS, the MCP add-on enabled, Shotcraft at the pinned commit, and the apps built.
2. A Workbench bug was found and fixed. The Workbench page failed to open with a Vite error, `Failed to resolve import ../../shared/motion.mjs from proj/Composition.tsx`. The Workbench links the editor's source in as `workbench/proj` and resolves links by that link path, so the editor's relative import pointed outside the link. Now `apps/editor/src/shared` is a link to `apps/shared`, and `Composition.tsx` imports `./shared/motion.mjs`. The editor type check and build pass. Earlier checks only confirmed that the server answered HTTP 200, so they missed this fault.
3. A new proof script, `node scripts/prove-workbench.mjs [--out work/proofs/workbench]`, opens the Workbench in headless Chromium, presses Play, and checks that the frame counter advances and the preview picture changes. It then presses the Workbench's own "Render the current project to MP4" button, follows its export API, and checks the MP4 with ffprobe. Result: the page opened with no errors; playback advanced from 00:00.00 to 00:04.00; the export produced an H.264 1280x720 MP4 with 180 frames. Separately, Shotcraft's own card checker (`node scripts/check-demo.mjs <card>.tsx` inside `.tools/video-shotcraft/workbench`) rendered the SplitFlapFlip card to a 150-frame MP4. This closes the "Workbench browser playback or video export: not tested" item.
4. Two faults in `scripts/cloud-session-setup.sh` were fixed. First, it installed the EGL graphics libraries only when FFmpeg was missing, so a machine with FFmpeg but no EGL could not render ("libEGL.so not loaded"). Second, it did not retry when the Ubuntu package mirror timed out. The automatic setup runs only when a cloud session starts inside the repository folder. In a session that starts one folder above it (several repositories attached), run `bash scripts/cloud-session-setup.sh` by hand from the repository.

**How to rerun these checks:**

- Setup: `python3 scripts/bootstrap.py`
- Workbench playback and export: `node scripts/prove-workbench.mjs`
- Blender stdio: `python3 integrations/blender/smoke.py`; add `--live` only with the Blender GUI running on a desktop-capable host
- Full cloud proof: push to a `claude/video-tools-*` branch, or dispatch **Video tool proofs (cloud CPU)** by hand (`.github/workflows/tool-proofs.yml`). The workflow also runs the Workbench proof and a Song 5 draft fetched from Drive.

The owner requires retaining and making these tools reusable. These are engineering proofs, not creative deliveries. They do not approve any film. CPU work remains in the cloud; needed GPU work uses the owner's Mac under [the current rules](../AGENTS.md).

## Historical setup verification, November 20, 2026

Historical record. The table below records checks in the cloud Linux workspace during setup on 2026-11-20. "Installed," "saved" and "this workspace" refer to that earlier environment, not to the present handoff checkout. The rows marked superseded were later verified by the current status section above.

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
| Live MCP call into a Blender GUI | Superseded: not tested in that workspace (Xvfb could not open local Unix sockets). Passed on the GitHub runner under Xvfb (November 23 run). Not rerun in the November 23 Claude Code session. |
| Pinned Shotcraft checkout | Verified exact commit `075b548c2405a07b77129eb448b0b504fc60dea3` |
| Shotcraft dependencies | Installed with `npm ci --ignore-scripts` |
| Project skill links | Created for project-scoped Claude Code and Codex clients |
| Workbench and editor version agreement | Passed: Remotion `4.0.484` |
| Workbench production build | Passed: TypeScript and Vite, 307 modules |
| Workbench card index | 150 demo cards, linked editor project recognized |
| Workbench HTTP smoke check | Passed: `/`, `/proj/workbench.ts`, `/src/cards/projectCards.ts` each returned 200. Superseded: this check did not catch the November 23 import fault. |
| Workbench foreground lifecycle | Passed: startup, HTTP responses, SIGTERM shutdown, exit 0 |
| Workbench browser playback or video export | Superseded: passed on November 23 (see the current status section) |
| Automatic client activation | Configuration prepared; current chat was not converted into an MCP client |

Generated evidence is available after running the checks in `.tools/blender-profile/installed.json`, `.tools/mcp-smoke.json`, `.tools/workbench-smoke.json`, and their adjacent logs. These machine-generated files are excluded from version control. No Workbench, MCP server, Blender GUI, Xvfb process, or render job was left running by these checks.

The normal Xvfb attempt in the November 20 workspace exited with `Unable to open socket for local`, `Unable to open socket for unix`, and `Cannot establish any listening sockets`. That limitation applied to that workspace only. Later cloud runs under Xvfb passed, as recorded above. No attempt was made to change sandbox permissions. Background Blender scripting remains separate from this GUI limitation.
