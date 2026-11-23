# Integration verification

The latest owner priorities ([PR #114](https://github.com/lovelaceaml-hub/concert-backdrops/pull/114)) authorize: make the retained tools work and be reusable for every song; integrate proven quality gains into the existing engine; then simplify status, stale PRs and distributed rendering. Try permitted cloud routes first for browser/Remotion/live-Blender sandbox limits. Use the owner's Mac only if no cloud route works and explain why; retain the separate GPU/load/priority conditions. The current deliverable is the complete Claude handoff; these priorities guide continuation.

## Current cloud verification, November 23, 2026 UTC

[PR #116](https://github.com/lovelaceaml-hub/concert-backdrops/pull/116) merged the cloud proof workflow and reusable scene/Drive helpers at `3812463e1196f4c47b468e05060dbc1c8154ff75`. The completed [run 45125796332](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45125796332) tested source `285df02e51cc68073fe17c8a06ae0d7f54737df7`. All three jobs succeeded; all eight actual tool-summary outcomes were success. Per-tool logs and summary are authoritative because the workflow uses `continue-on-error` for individual proof steps.

| Cloud proof | Observed result and scope |
| --- | --- |
| Setup and browser doctor | Passed on Ubuntu 24.04 GitHub CPU runner; Python 3.12.16, Blender 5.2.4 LTS, Node 24.22.3, FFmpeg 6.1.1 |
| Three.js capture | Actual SwiftShader WebGL2 animated frames and out-of-order frame checks passed |
| Pipeline preview | Encoded 4 seconds, 120 frames, 320×180/30 fps; QA passed |
| Remotion assembly | Encoded 4 seconds, 120 frames, 320×180/30 fps; QA passed |
| Blender background render | Encoded 2 seconds, 60 frames, 320×180/30 fps; QA passed |
| Reusable song scene | Encoded 4 seconds, 240 frames, 1920×1080/60 fps through `p3d-kit` with project params; QA passed |
| Blender MCP | Stdio and live GUI under Xvfb passed; `live_blender_connection=passed`, response `PIPELINE_MCP_CONNECTED 5.2.4 LTS` |
| CPU Docker image | Separate job built successfully; container execution/production was not proved |
| Drive access | Separate job read the project folder and saved then removed a unique test file |

All four encoded demo QA records have `creative_approval=not_assessed` and `audio_streams=0`. They prove the specified short runtime paths, not every song, a full concert or approved 4K production. Shotcraft Workbench interactive browser playback/export remains unverified; the new check's `server_started=false` does not supersede that limitation. Its historical build/HTTP/lifecycle evidence is retained below. No production Mac/Metal run is established.

Use [the workflow](../.github/workflows/tool-proofs.yml), [validation record](../docs/VIDEO-PIPELINE-VALIDATION.md), [reusable-scene instructions](../docs/VIDEO-PIPELINE.md#reusable-scenes-for-any-song-november-22-2026), [kit adapter](../pipeline/kit.py) and [example project](../projects/song-scene-demo/project.json). [`tools/drive_sync.py`](../tools/drive_sync.py) uses the Actions secret `GOOGLE_DRIVE_OAUTH` for project Drive list/get/put operations; the documented `GOOGLE_DRIVE_SA_KEY` fallback is read-only. Record secret names only. Future media transfers still require their own byte checks.

## This local handoff checkout

Source, pins and configuration are preserved, but this host does not contain installed Node dependencies, the pinned `.tools/video-shotcraft` checkout or an isolated Blender MCP environment/profile. The two tracked Shotcraft skill symlinks are present but dangling because their `../../.tools/video-shotcraft` target is absent. Preserve these links during source extraction. This host's Blender 4.3.2 differs from the project's 5.2.4 LTS pin. Restore the intended versions before using this host. These are local installation gaps, not a current blanket cloud blocker. See [setup instructions](README.md) and [the complete handoff](../project-docs/production-system/CLAUDE-HANDOFF.md).

The completed full Song 11 p3d production retains its original producing source and Python 3.12.14 runtime contract; the newer tool-proof environment does not replace those pins. It has no unfinished render queue. CPU work remains in the cloud; needed GPU work uses the owner's Mac under [the current rules](../AGENTS.md).

## Historical setup verification, November 20, 2026

The table below records checks in the chat-hosted Linux workspace during setup on 2026-11-20. “Installed,” “saved” and “this workspace” refer to that earlier environment, not to the present handoff checkout or the newer GitHub runner. The current cloud section above supersedes the historical live-GUI blocker; Workbench browser playback/export remains a separate unverified operation.

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
