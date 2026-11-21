# Blender MCP and Video Shotcraft

These integrations are installed in this checkout. They add interactive scene editing and a reusable motion library to the render pipeline. Production rendering can run through Blender's background Python scripts without the live MCP connection.

## Installed versions

| Component | Pin | Location |
| --- | --- | --- |
| MCP for Blender | `2.3.1`, including hashes for all Python dependencies | `.tools/blender-mcp-env` |
| Blender add-on | Bundled with that same MCP package | `.tools/blender-profile/scripts/addons/blender_mcp.py` |
| Video Shotcraft | `075b548c2405a07b77129eb448b0b504fc60dea3` | `.tools/video-shotcraft` |
| Workbench Remotion | `4.0.484`, matching `apps/editor` | Shotcraft's own locked Node environment |

The Blender add-on was enabled and saved using the project's official Blender 5.2.4 LTS runtime. Its preferences and startup scene live in `.tools/blender-profile`, separate from any other Blender installation. All eight external asset and AI generation integrations are off. Telemetry and update checks are off. The listener is restricted to `localhost:9876`.

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

The project symlinks under `.agents/skills/video-shotcraft` and `.claude/skills/video-shotcraft` expose the unchanged upstream skill to supported CLI clients. They do not register a plugin in this ChatGPT conversation. The project instructions, creative approvals, cloud-only execution rule, and restrictions on generated or third-party media continue to govern how the library is used.

## Open and reuse Shotcraft

```bash
node scripts/launch-workbench.mjs --check
node scripts/launch-workbench.mjs
```

The wrapper links `apps/editor/src` into Workbench, builds its card index, and serves `http://localhost:5198/?import=project`. Use the cloud workspace's port forwarding to view it. It stays in the foreground so the workspace keeps the process alive. Press Ctrl-C to stop it, or run `node scripts/launch-workbench.mjs --stop` in the same runtime. A persistent terminal can opt into `--background`. `--project` and `--port` select another compatible editor and port.

`apps/editor/src/workbench.ts` exports the manifest. It shares the exact frame timings with the editor composition, uses the same Remotion version, and declares editable fields using Shotcraft's `PropField[]` schema. When adding a scene, keep its absolute start frame, duration, component, and props in this shared manifest. Workbench edits do not automatically rewrite the source composition. Export the Workbench project JSON to preserve edits, then deliberately incorporate the approved timing or style changes into source before the next frozen render. Reference cards and bundled demo media are examples, not approved concert assets.

## Verification and current limit

See [STATUS.md](STATUS.md) for the checks performed in this workspace. MCP's stdio handshake and safe-mode rejection passed. The isolated add-on was enabled successfully. Workbench compiled, served the linked project modules over HTTP, and shut down cleanly.

This managed workspace refuses the local Unix sockets required by Xvfb, so the live Blender GUI connection could not be tested here. The ordinary Xvfb startup failed with `Cannot establish any listening sockets`. A workspace with desktop support is required for that optional interactive connection. Browser-rendered Workbench playback was not tested in this integration check. The setup does not imply that a cloud GPU or Mac GPU is active.

## Upstream references and licenses

- [MCP for Blender](https://github.com/ahujasid/mcp-for-blender): MIT; the installed server includes the matching add-on. A retained copy is in `licenses/mcp-for-blender-MIT.txt`.
- [Video Shotcraft at the pinned commit](https://github.com/Vincentwei1021/video-shotcraft/tree/075b548c2405a07b77129eb448b0b504fc60dea3): Apache 2.0 for its code and documentation. A retained copy is in `licenses/video-shotcraft-Apache-2.0.txt`. Its bundled media has separate notices that remain in the upstream checkout.
- [Shotcraft Workbench integration](https://github.com/Vincentwei1021/video-shotcraft/blob/075b548c2405a07b77129eb448b0b504fc60dea3/references/workbench.md): authoritative manifest and reimport behavior.
- [Codex MCP configuration](https://developers.openai.com/codex/mcp/): project configuration, stdio transport, and tool selection.
- [Remotion license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md): applies separately to the video framework. Shotcraft's Apache license does not replace it.

Third-party runtimes, generated media, and dependency trees are excluded from this repository. The bootstrap retrieves them at their recorded versions instead of redistributing binary environments.
