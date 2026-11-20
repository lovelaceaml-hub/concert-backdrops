# Concert Backdrops (engine code)

Code for the video backdrops of "The Words of Mother's Love Healing Concert" (LV Zion, Sunday December 6, 2026). The concert's message: the Words of Mother's Love bring peace.

**The project's official home is Anthony's Google Drive folder "Concert Backdrops - Songs"** (lovelace.aml account). The designs, rules, status, songs, lyrics, storyboards and finished videos all live there. This repo holds only the graphics engine, so cloud machines can clone it and render.

## Quick links
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

Rendering runs in the cloud only (about 6 minutes of rendering per minute of video). Setup and method: docs/ENGINE-HANDOFF-2026-11-13.md.
