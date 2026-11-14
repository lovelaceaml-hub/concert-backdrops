# Handoff: Concert Backdrops engine

Current status, decisions and next steps live in the project's home folder on Google Drive: "Concert Backdrops - Songs", file VIDEO-HANDOFF.md (status) and DESIGN-SYSTEM.md (rules and decisions waiting for Anthony). Read those first.

## State of this repo (2026-11-14)
- engine/songs/ holds a 60 second promo file for each of the 11 songs (s01_stars_of_zion.py to s11_finale.py), plus s03_original.py (the first full song 03 video) and t_short_test.py (an 8 second pipeline test). audio/promo/ holds each promo's 60 second clip (02 and 10 are silence: no recording yet).
- All 11 promos were rendered with the Render workflow, checked (60 s, 1920x1080, sound) and saved in the Drive folder's Videos/.
- Engine features: any song (engine/songs/, SONG setting), lyric fragments, relit lights, the shared arch (engine/arch.py), per-song colors (PETAL_COLORS, MOTE_COLORS, LANTERN_COLORS, AURORA_WARM, AURORA_COOL, MOTE_Y), safe silent clips, encoder and full-length checks.
- Engine upgrade (branch engine-scenes-figures, 2026-11-13): scene plates (SCENES), people of light (FIGURES), effect layers (SNOW, ICE, SHARDS, SHARDS_MEND, GOLDEN_FIELD, NET, BEAM, FLASH), fragment styles (write, reflection, petals, engrave), PHRASES y=, SKYLINE_LANTERN. All optional: songs that do not use them render as before. How to use them: engine/UPGRADE-HOWTO.md. Code: engine/upgrade.py (Python side), engine/upgrade_shaders.py (light layers), the composite pass in engine/shaders.py (plates, ice, shards, field). Demo: engine/songs/demo_upgrade.py.
- Astra round 1 shared fixes (2026-11-14, same branch, merged with pull request 15): text protection behind all text (a soft neutral veil plus dimming of every light behind the words), BOTTOM_CALM (on by default for song files with SCENES or FIGURES), arch lines only after both lights are visible, a thin persistent ring per relight plus RINGS_AT_START, the shared strict Track (engine/track.py; song.py refuses unsorted keys in any song file, so songs 09 and 11 must put their keys in order), the three-line end card, thinner shards, a gentler beam, brighter people of light. Details: engine/UPGRADE-HOWTO.md section E.
- The Render workflow's video run also uploads a share copy: artifact "<name> (share)", 1280x720, under 25 MB (checked; the run fails if larger).
- assets/plates/ (painted scene plates, 1920x1080 JPEG, per song folder) and assets/figures/ (the shared people-of-light library, list in assets/figures/README.md) are in the repo so the cloud render has them. tools/prepare_figure.py prepares a new pose picture.
- Not built yet: full-length concert videos timed to the live versions, an endless closing hold and live section cues.

## How to render (cloud only)
- Each song has its own file in engine/songs/ (copy s03_original.py to start). Choose it with the SONG environment variable.
- Short lyric fragments go in FRAGMENTS in the song file (text, t0, t1, out, dy, size, and optional style).
- Scenes, people of light and effect layers: engine/UPGRADE-HOWTO.md.
- Render with the GitHub Actions workflow "Render" (manual): gh workflow run render.yml -f song=<file> -f audio=<path> -f mode=stills|video -f name=<name>. Stills first, then video. The video job splits the frames over 4 cloud machines, joins them and adds the music. Results are workflow artifacts (gh run download).

## Rules
- Never commit full songs, lyrics, videos, frames or any personal data. Media stays in the Drive folder. Exception: short audio clips in audio/ (for example the 60 second promo clips) that cloud renders need; this repo is private.
- Rendering only in the cloud. No em dash or en dash anywhere.
