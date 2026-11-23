# Blender MCP and Video Shotcraft

The latest owner priorities ([PR #114](https://github.com/lovelaceaml-hub/concert-backdrops/pull/114)) authorize: make the retained tools work and be reusable for every song; integrate proven quality gains into the existing engine; then simplify status, stale PRs and distributed rendering. Try permitted cloud routes first for browser/Remotion/live-Blender sandbox limits. Use the owner's Mac only if no cloud route works and explain why; retain the separate GPU/load/priority conditions. The current deliverable is the complete Claude handoff; these priorities guide continuation.

These integration sources, pins and client configurations are preserved for reusable scene editing and motion work. **They are not currently installed in the handoff checkout.** The November 23 resource audit found no `node_modules`, pinned `.tools/video-shotcraft` checkout, isolated Blender MCP environment/profile. The two tracked Shotcraft skill symlinks are present but dangling because their `../../.tools/video-shotcraft` target is absent. Preserve these links during source extraction. The host Blender 4.3.2 is not the recorded project pin of 5.2.4 LTS. Restore and check the pinned resources before claiming the integrations are ready.

The historical November 20 verification in [STATUS.md](STATUS.md) establishes successful setup/build/stdio checks in that earlier environment; it does not establish present installation or working browser/GUI playback. Production rendering can run through Blender's background Python scripts independently of the live MCP connection. The completed full Song 11 used the established native p3d route. See [the complete project handoff](../project-docs/production-system/CLAUDE-HANDOFF.md).

The [current owner directions](../AGENTS.md) require keeping Blender, Three.js, Remotion, Video Shotcraft and Blender MCP and making them reusable. CPU work stays in the cloud. If GPU work is needed, use the owner's Mac under the documented load, priority and explicit local-render conditions; Linux installation does not prove a working Mac/Metal setup.

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

## Verification and current limit

See [STATUS.md](STATUS.md) for the dated setup checks. In that environment, MCP's stdio handshake and safe-mode rejection passed, the isolated add-on was enabled, and Workbench compiled, served the linked project modules over HTTP and shut down cleanly. These checks do not restore the dependencies missing from the current handoff checkout.

The recorded managed workspace refused the local Unix sockets required by Xvfb, so the live Blender GUI connection could not be tested there. The ordinary Xvfb startup failed with `Cannot establish any listening sockets`. A suitable permitted workspace with desktop support is required for that interactive connection. Browser-rendered Workbench playback and video export remain unverified. No active cloud GPU or validated Mac GPU route is established by this setup record.

## Upstream references and licenses

- [MCP for Blender](https://github.com/ahujasid/mcp-for-blender): MIT; the installed server includes the matching add-on. A retained copy is in `licenses/mcp-for-blender-MIT.txt`.
- [Video Shotcraft at the pinned commit](https://github.com/Vincentwei1021/video-shotcraft/tree/075b548c2405a07b77129eb448b0b504fc60dea3): Apache 2.0 for its code and documentation. A retained copy is in `licenses/video-shotcraft-Apache-2.0.txt`. Its bundled media has separate notices that remain in the upstream checkout.
- [Shotcraft Workbench integration](https://github.com/Vincentwei1021/video-shotcraft/blob/075b548c2405a07b77129eb448b0b504fc60dea3/references/workbench.md): authoritative manifest and reimport behavior.
- [Codex MCP configuration](https://developers.openai.com/codex/mcp/): project configuration, stdio transport, and tool selection.
- [Remotion license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md): applies separately to the video framework. Shotcraft's Apache license does not replace it.

Third-party runtimes, generated media, and dependency trees are excluded from this repository. The bootstrap retrieves them at their recorded versions instead of redistributing binary environments.
