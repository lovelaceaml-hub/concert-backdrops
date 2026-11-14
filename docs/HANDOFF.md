# Handoff: Concert Backdrops engine

Current status, decisions and next steps live in the project's home folder on Google Drive: "Concert Backdrops - Songs", file VIDEO-HANDOFF.md (status) and DESIGN-SYSTEM.md (rules and decisions waiting for Anthony). Read those first.

## State of this repo (2026-11-13)
- Started from the first cloud session's engine (commit f292678 is identical to the zip "Concert Backdrops - engine and how to continue (2026-11-13).zip"). Since then: any song can be drawn (engine/songs/, chosen by SONG), lyric fragments, relit lights, a shared arch (engine/arch.py), safe features for silent clips, encoder and length checks, and the cloud Render workflow. See git log.
- engine/songs/s03_original.py still renders song 3's first version: all nine expressions in sequence, timed to the 4:11 recording (SONG_END 250.7, TOTAL 330.0), with a fade at the end.
- Not yet built: the 11 new song designs (Drive, Designs/), song-specific scenes, an endless closing hold, live section cues, timing to the live lengths.

## How to render (cloud only)
- Each song has its own file in engine/songs/ (copy s03_original.py to start). Choose it with the SONG environment variable.
- Short lyric fragments go in FRAGMENTS in the song file (text, t0, t1, out, dy, size).
- Render with the GitHub Actions workflow "Render" (manual): gh workflow run render.yml -f song=<file> -f audio=<path> -f mode=stills|video -f name=<name>. Stills first, then video. The video job splits the frames over 4 cloud machines, joins them and adds the music. Results are workflow artifacts (gh run download).

## Rules
- Never commit full songs, lyrics, videos, frames or any personal data. Media stays in the Drive folder. Exception: short audio clips in audio/ (for example the 60 second promo clips) that cloud renders need; this repo is private.
- Rendering only in the cloud. No em dash or en dash anywhere.
