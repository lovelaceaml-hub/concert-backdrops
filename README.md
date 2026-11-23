# Concert Backdrops (engine code)

The latest owner priorities ([PR #114](https://github.com/lovelaceaml-hub/concert-backdrops/pull/114)) authorize: make the retained tools work and be reusable for every song; integrate proven quality gains into the existing engine; then simplify status, stale PRs and distributed rendering. Try permitted cloud routes first for browser/Remotion/live-Blender sandbox limits. Use the owner's Mac only if no cloud route works and explain why; retain the separate GPU/load/priority conditions. The current deliverable is the complete Claude handoff; these priorities guide continuation.

Code for the video backdrops of "The Words of Mother's Love Healing Concert" (LV Zion, Sunday December 6, 2026). The concert's message: the Words of Mother's Love bring peace.

**The project's official home is the Google Drive folder "Concert Backdrops - Songs"**. The designs, rules, status, songs, lyrics, storyboards and finished videos live there. This repository holds the graphics engine, production workflow, catalogs and versioned instructions so cloud machines and new AI chats can reproduce the work.

## Current production system

Use [the plain project status](project-docs/production-system/PROJECT-STATUS.md) and [the Claude starting prompt](project-docs/production-system/CLAUDE-START-PROMPT.txt) for the handoff.

Start with the current [owner directions](AGENTS.md), the [complete Claude handoff](project-docs/production-system/CLAUDE-HANDOFF.md), [START-HERE](project-docs/production-system/START-HERE.md) and [current state](project-docs/production-system/STATE.json). Improve the existing engine and retain Blender, the Three.js preview, Remotion, Video Shotcraft and Blender MCP as reusable tools. Their source/configuration is preserved; [integration status](integrations/STATUS.md) distinguishes historical verification from current installation and unverified browser/GUI paths.

The complete **Almighty God Knows the Future** recreation is rendered, checked and saved: **275 seconds, native 1920×1080 at 60 fps, 16,500 frames**. [PR #112](https://github.com/lovelaceaml-hub/concert-backdrops/pull/112) merged at `93527bf5e2e43477073e361d22cfd6d4fa999da7`; the producing picture source remains `eec8d16519ea82309ef851975792e9dfc548da03`. This is the completed 1080p design/review delivery. Exact-output owner approval is not recorded. The final show target is **4K60 after design, timing and content approval**. There is no unfinished render queue, and no new phone versions should be made.

Recover finished media using [DELIVERIES](project-docs/production-system/DELIVERIES.md) and the [exact Song 11 identities](project-docs/production-system/evidence/s11-renewed-final-delivery.json) before rerendering. The shared [Production System folder](https://drive.google.com/drive/folders/1QDGGqqkJlbovBLCthX-QChqfD8zSmK8X) remains available; the [current Claude handoff folder](https://drive.google.com/drive/folders/1lxcic8BcSzNgPtEY_Yg_2TBAbNam72dZ) and its verified transfer inventory describe current source, resource and media coverage. Large files may be transferred as exact byte parts with a restoration helper; that is a transfer format, with no video re-encoding. A folder link alone does not establish completed upload coverage.

```bash
./scripts/concert status
python3 scripts/bootstrap.py --p3d-only --reference-fonts
./scripts/video doctor --backend p3d
./scripts/concert verify-catalogs
```

The approved 66-second promo supplies the creative language. The approved 30-second Song 11 study supplies the native 1080p60 clarity reference. All eleven full recording sources are indexed and byte-verified; this does not imply every historical full-song movie has been recovered. The [native model kit](tools/concert_kit/README.md), [dove, rose and wheat prototypes](tools/concert_addons/README.md), and [camera and response revision](tools/concert_motion_revision/README.md) preserve earlier reusable work. Apply the current generous-garment modesty correction to every reused figure. The [historical improvement backlog](project-docs/production-system/IMPROVEMENT-QUEUE.md) offers ideas, not an automatic next task.

## Quick links

- Native 4K and smoother animation: [docs/4K-AND-MOTION.md](docs/4K-AND-MOTION.md)
- 4K and motion verification: [docs/4K-MOTION-VALIDATION.md](docs/4K-MOTION-VALIDATION.md)
- Repeatable video workflow: [docs/VIDEO-PIPELINE.md](docs/VIDEO-PIPELINE.md)
- Setup verification and remaining environment limits: [docs/VIDEO-PIPELINE-VALIDATION.md](docs/VIDEO-PIPELINE-VALIDATION.md)
- Project home: Google Drive, My Drive / Concert Backdrops - Songs (README.md, DESIGN-SYSTEM.md, VIDEO-HANDOFF.md inside)
- Handoff: [docs/HANDOFF.md](docs/HANDOFF.md)
- How song 3 was made: [docs/PROCESS-AND-TOOLS.md](docs/PROCESS-AND-TOOLS.md)
- Original engine handoff and method: [docs/ENGINE-HANDOFF-2026-11-13.md](docs/ENGINE-HANDOFF-2026-11-13.md)

## What is here

- engine/song.py: timeline, palettes, the nine expressions and their times (currently set for song 3's first version)
- engine/text.py: words drawn as pictures
- engine/shaders.py: the GLSL drawing programs
- engine/render.py: renders frames to video
- engine/analyze.py, engine/analyze2.py: measure a recording
- engine/sheet.py: contact sheets for checking

CPU rendering runs in the cloud. GPU work, if needed, uses the owner's Mac under the load, priority and explicit local-render conditions in AGENTS.md. Cost varies substantially by resolution, geometry, temporal samples, clothing and cache warmup; measure representative frames before estimating a film. The original shader workflow is recorded in docs/ENGINE-HANDOFF-2026-11-13.md. Registered scene rendering is described in docs/PIPELINE-INTEGRATION.md; the completed full Song 11 has its dedicated [scene](tools/s11_renewed/README.md), [cloud](tools/s11_cloud/README.md) and [delivery](tools/s11_delivery/README.md) workflows.
