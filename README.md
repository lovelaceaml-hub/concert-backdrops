# Concert Backdrops (engine code)

Code for the video backdrops of "The Words of Mother's Love Healing Concert" (LV Zion, Sunday December 6, 2026). The concert's message: the Words of Mother's Love bring peace.

**The project's official home is Anthony's Google Drive folder "Concert Backdrops - Songs"** (lovelace.aml account). The designs, rules, status, songs, lyrics, storyboards and finished videos live there. This repository holds the graphics engine, production workflow, catalogs and versioned instructions so cloud machines and new AI chats can reproduce the work.

## Current production system

Start with [START-HERE](project-docs/production-system/START-HERE.md) and the [handoff for any AI](project-docs/production-system/AI-HANDOFF.md). The repository includes the graphics engine, registered production commands, catalogs, verification and repeatable instructions. The shared [Production System folder](https://drive.google.com/drive/folders/1QDGGqqkJlbovBLCthX-QChqfD8zSmK8X) is the portable handoff destination. Full audio and the approved study archive are in the existing Drive home. Check the [delivery catalog](project-docs/production-system/catalogs/deliveries.json) for the exact new media links and any pending shared copies.

```bash
./scripts/concert status
./scripts/concert song s07
python3 scripts/bootstrap.py --p3d-only --reference-fonts
./scripts/video doctor --project concert-kit-consideration-v2
./scripts/video produce concert-kit-consideration-v2 --quality review --plan
```

The approved 66-second promo supplies the creative language. The approved 30-second Song 11 study supplies the native 1080p60 clarity reference. All eleven full recording sources are indexed and byte-verified. The [native model kit](tools/concert_kit/README.md), [dove, rose and wheat prototypes](tools/concert_addons/README.md), and [camera and response revision](tools/concert_motion_revision/README.md) extend those references through small reviewable performances. The [improvement queue](project-docs/production-system/IMPROVEMENT-QUEUE.md) records the next concrete work.

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

Rendering runs in cloud CPU workers by default. Cost varies substantially by resolution, geometry, temporal samples, clothing and cache warmup; measure representative frames before estimating a film. The original shader workflow is recorded in docs/ENGINE-HANDOFF-2026-11-13.md. Current registered scene rendering is described in docs/PIPELINE-INTEGRATION.md.
