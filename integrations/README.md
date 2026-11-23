# Blender MCP and Video Shotcraft

The latest owner priorities ([PR #114](https://github.com/lovelaceaml-hub/concert-backdrops/pull/114)) authorize: make the retained tools work and be reusable for every song; integrate proven quality gains into the existing engine; then simplify status, stale PRs and distributed rendering. Try permitted cloud routes first for browser/Remotion/live-Blender sandbox limits. Use the owner's Mac only if no cloud route works and explain why; retain the separate GPU/load/priority conditions. The current deliverable is the complete Claude handoff; these priorities guide continuation.

**The GitHub Actions CPU route is verified; this local handoff checkout still needs installation.** [PR #116](https://github.com/lovelaceaml-hub/concert-backdrops/pull/116), merged at `3812463e1196f4c47b468e05060dbc1c8154ff75`, adds the cloud proof workflow, reusable song scene and Drive helper. The completed [run 45125796332](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45125796332) tested `285df02e51cc68073fe17c8a06ae0d7f54737df7`: all three jobs and all eight per-tool summary outcomes succeeded. Actual Three.js capture, Remotion assembly, Blender rendering and the live Blender MCP connection under Xvfb passed. See [STATUS.md](STATUS.md) for exact scope and remaining checks.

The November 23 **local** resource audit found no `node_modules`, pinned `.tools/video-shotcraft` checkout or isolated Blender MCP environment/profile. The two tracked Shotcraft skill symlinks are present but dangling because their `../../.tools/video-shotcraft` target is absent. Preserve these links during source extraction. This host's Blender 4.3.2 is not the project's 5.2.4 LTS pin. Restore the intended versions before using this host; these local gaps do not invalidate the cloud proofs.

The historical November 20 verification remains in [STATUS.md](STATUS.md). Its browser/GUI restrictions describe that earlier chat workspace, not the working GitHub runner route. Background Blender rendering is independent of the live MCP connection. The completed full Song 11 used the established native p3d route and keeps its original producing identity. See [the complete project handoff](../project-docs/production-system/CLAUDE-HANDOFF.md).

The [current owner directions](../AGENTS.md) require keeping Blender, Three.js, Remotion, Video Shotcraft and Blender MCP and making them reusable. CPU work stays in the cloud. If GPU work is needed, use the owner's Mac under the documented load, priority and explicit local-render conditions; Linux installation does not prove a working Mac/Metal setup.

## Cloud workflow, reusable scenes and Drive

Run **Video tool proofs (cloud CPU)** through [the workflow](../.github/workflows/tool-proofs.yml), either by manual dispatch or a `claude/video-tools-*` branch push. Inspect every recorded outcome in `proofs/summary.txt` and the associated logs: individual proof steps use `continue-on-error`, so a green job alone is insufficient. The `tool-proofs` artifact lasts fourteen days. [The validation record](../docs/VIDEO-PIPELINE-VALIDATION.md) documents the route.

[The reusable scene instructions](../docs/VIDEO-PIPELINE.md#reusable-scenes-for-any-song-november-22-2026) describe [pipeline/kit.py](../pipeline/kit.py), [scenes/p3d/song_scene.py](../scenes/p3d/song_scene.py) and [song-scene-demo](../projects/song-scene-demo/project.json). The adapter supplies frame recovery, worker chunks, temporal samples and QA for configurable scenes. Existing approved registrations remain frozen. The new route proved a four-second 1080p60 Song 11 example; it does not automatically migrate the renewed film's garment/performance changes into every legacy song. Review each song's content and motion before reuse.

[`tools/drive_sync.py`](../tools/drive_sync.py) lists, downloads and uploads within the existing project Drive tree. GitHub jobs use the Actions secret **`GOOGLE_DRIVE_OAUTH`**; **`GOOGLE_DRIVE_SA_KEY`** is the documented read-only fallback. Never copy secret values into source, logs or handoff material. The cloud access proof read the folder and created then removed a unique test file. Future downloaded recordings and uploaded renders still need their own identity/hash checks. `put` updates a same-name file in the chosen folder or creates one, so use deliberate filenames and keep verification receipts.

## Pinned versions and intended restored locations

| Component | Pin | Location |
| --- | --- | --- |
| MCP for Blender | `2.3.1`, including hashes for all Python dependencies | `.tools/blender-mcp-env` |
| Blender add-on | Bundled with that same MCP package | `.tools/blender-profile/scripts/addons/blender_mcp.py` |
| Video Shotcraft | `075b548c2405a07b77129eb448b0b504fc60dea3` | `.tools/video-shotcraft` |
| Workbench Remotion | `4.0.484`, matching `apps/editor` | Shotcraft's own locked Node environment |

During the recorded setup, the Blender add-on was enabled and saved using the project's official Blender 5.2.4 LTS runtime. The intended preferences/startup location is `.tools/blender-profile`, separate from other Blender installations. The configuration disables all eight external asset and AI generation integrations, telemetry and update checks, and restricts the listener to `localhost:9876`. Verify those settings again after restoring the missing environment/profile.

## Install or verify

Run these commands from the repository root in the cloud Linux workspace:

```bash
python3 scripts/install-integrations.py
python3 scripts/install-integrations.py --check
python3 integrations/blender/smoke.py
```

The main bootstrap also calls the installer. It uses the committed Python hash lock, the exact Shotcraft commit, and Shotcraft's committed `package-lock.json`. It preserves the upstream source and licenses, creates project skill symlinks, and starts no services. It does not edit global Claude, Codex, or Blender settings.

Optional installer flags are `--offline`, `--skip-workbench`, `--skip-blender-addon`, and `--blender /path/to/blender`. Offline installation requires the clone and package caches to exist already. `--check` performs no installation. The normal bootstrap supplies Blender and the command prerequisites `uv`, Python, Git, Node, and npm.

## Connect an assistant to Blender

Claude Code uses the project `.mcp.json`; Codex uses `.codex/config.toml` when the project is trusted. Open the client at the repository root after installation and reload its MCP connections. The configuration launches the installed Python environment through a relative-path wrapper, with no workspace-specific absolute paths. Codex's tool list exposes scene inspection, scene code, viewport inspection, add-on status, and telemetry disabling.

Start Blender on a cloud desktop:

```bash
python3 integrations/blender/launch_blender.py
```

On a cloud machine with Xvfb and normal desktop socket support, an invisible GUI session is also supported:

```bash
xvfb-run -a python3 integrations/blender/launch_blender.py
```

With that session running, verify the actual connection:

```bash
python3 integrations/blender/smoke.py --live
```

MCP for Blender needs Blender's GUI event loop. `blender --background` can enable the add-on and render scenes, but it cannot service this add-on's live commands. Safe mode is enabled for code sent through MCP. No cloud GPU service or remote Blender socket is configured.

After installation, the project symlinks under `.agents/skills/video-shotcraft` and `.claude/skills/video-shotcraft` expose the unchanged upstream skill to supported CLI clients. They do not register a plugin in an existing ChatGPT conversation. The current owner directions, creative approval boundaries, cloud CPU/Mac GPU rule and restrictions on generated or third-party media govern how the library is used.

## Open and reuse Shotcraft

```bash
node scripts/launch-workbench.mjs --check
node scripts/launch-workbench.mjs
```

The wrapper links `apps/editor/src` into Workbench, builds its card index, and serves `http://localhost:5198/?import=project`. Use the cloud workspace's port forwarding to view it. It stays in the foreground so the workspace keeps the process alive. Press Ctrl-C to stop it, or run `node scripts/launch-workbench.mjs --stop` in the same runtime. A persistent terminal can opt into `--background`. `--project` and `--port` select another compatible editor and port.

`apps/editor/src/workbench.ts` exports the manifest. It shares the exact frame timings with the editor composition, uses the same Remotion version, and declares editable fields using Shotcraft's `PropField[]` schema. When adding a scene, keep its absolute start frame, duration, component, and props in this shared manifest. Workbench edits do not automatically rewrite the source composition. Export the Workbench project JSON to preserve edits, then deliberately incorporate the approved timing or style changes into source before the next frozen render. Reference cards and bundled demo media are examples, not approved concert assets.

## Verification and remaining limits

The new cloud proof confirms live Blender MCP 5.2.4 LTS under Xvfb and browser-based Three.js/Remotion operation; the historical chat workspace's Unix-socket restriction was not bypassed. Pipeline preview and Remotion each encoded four seconds at 320×180/30 fps; Blender encoded two seconds at the same resolution/rate. The reusable scene encoded four seconds at 1920×1080/60 fps. Their QA passed with creative approval `not_assessed` and no audio stream. The proof runner used Python 3.12.16, Node 24.22.3 and FFmpeg 6.1.1. That environment is separate from the completed Song 11's frozen Python 3.12.14 render contract.

Workbench interactive browser playback and video export remain unverified: the new check reports `server_started=false`. Historical Workbench build, HTTP and foreground lifecycle checks are preserved separately. The CPU Docker image built successfully, but no container execution/production proof follows from that build. Short demos do not establish all-song correctness, full-concert quality or approved 4K production. No active cloud GPU or validated Mac GPU route is established. These results also do not install the dependencies missing from this local checkout or automatically activate an assistant's MCP client.

## Upstream references and licenses

- [MCP for Blender](https://github.com/ahujasid/mcp-for-blender): MIT; the installed server includes the matching add-on. A retained copy is in `licenses/mcp-for-blender-MIT.txt`.
- [Video Shotcraft at the pinned commit](https://github.com/Vincentwei1021/video-shotcraft/tree/075b548c2405a07b77129eb448b0b504fc60dea3): Apache 2.0 for its code and documentation. A retained copy is in `licenses/video-shotcraft-Apache-2.0.txt`. Its bundled media has separate notices that remain in the upstream checkout.
- [Shotcraft Workbench integration](https://github.com/Vincentwei1021/video-shotcraft/blob/075b548c2405a07b77129eb448b0b504fc60dea3/references/workbench.md): authoritative manifest and reimport behavior.
- [Codex MCP configuration](https://developers.openai.com/codex/mcp/): project configuration, stdio transport, and tool selection.
- [Remotion license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md): applies separately to the video framework. Shotcraft's Apache license does not replace it.

Third-party runtimes, generated media, and dependency trees are excluded from this repository. The bootstrap retrieves them at their recorded versions instead of redistributing binary environments.
