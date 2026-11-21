# Current instructions for every AI

Current system handoff: November 20, 2026, America/Los_Angeles.

Start with `project-docs/production-system/START-HERE.md` and `AI-HANDOFF.md` in the same folder. The owner approved the Song 11 beauty study and explicitly requested setup, saving, documentation, uploads, push and merge, followed by continued model and animation improvements for the concert songs. Use the current user's authorization; do not repeat permission questions for work already authorized.

The main message is that Mother's Words of Love bring peace. The approved 66-second Film10 Nine Colours Revision3 is the creative reference. The approved 30-second native1080p60 Song11 beauty study is the clarity and production reference. Exact media hashes, source pins and durable links are in `project-docs/production-system/catalogs/references.json`.

The project home remains the Drive folder Concert Backdrops - Songs, ID `1xyNZn4ZA6bjPcvKjGfgSWQIs9aAp2PPd`. Read its current rules, handoff, per-song status and later lessons addenda. The repository holds code, repeatable workflows, catalogs and instructions. Full source audio stays in the private Drive home; finished media uses the exact private archive links in the delivery catalog, with pending shared copies identified explicitly. Ignored work directories hold reacquirable working inputs and render frames. The catalog records eleven verified full recordings. Older missing-recording notes for 02 and 10 are historical.

- Use `./scripts/concert status`, `song`, `verify-audio` and `plan` to begin. Use `./scripts/video produce` for explicitly registered scenes. A catalog proposal is not a completed full-song scene.
- New visuals use native code-drawn models and effects. The legacy generated raster folders `assets/figures`, `assets/plates` and `assets/song_figures` are historical and ineligible for this workflow. Preserve them for provenance.
- Keep approved source snapshots immutable. Improve in new modules and reviewable examples. Exact campaign wording and color come from `engine/p3d/words.py`.
- Use cloud CPU rendering by default. The user can make a Mac GPU available but prefers not to use it; do not use it for this workflow. The cloud GPU provider remains unconfigured and paid rendering is not authorized by this setup request.
- Use a branch and isolated worktree. One writer per area. Freeze shared lighting and scene source for each render round. Use explicit staging and never `git add -A`.
- Inspect native-size keyframes, a moving contact/performance proof and the final output. Keep technical checks, visual review and exact-output owner approval distinct.
- Save media, QA, fingerprints and shared handoff links. Append to `project-docs/production-log.jsonl`; preserve historical records. Merge through a normal PR using current authorization and required checks.
- Never commit full songs, copied lyrics, finished videos, frames, derived caches, credentials or personal data. Existing short test/promo clips are historical exceptions, not permission to add full audio.
- No em dash or en dash in new code, docs, PR text or records.

## Historical November 15 instructions

The following text is retained as history. Its old current-project description and workflow-only render instruction are superseded by the current entry point above. Specific source/visual rules remain applicable unless later owner directions replace them.

# Instructions for AIs

This repo is only the engine code. The project's home, rules and status are in Anthony's Google Drive folder "Concert Backdrops - Songs": read its AGENTS.md, DESIGN-SYSTEM.md, VIDEO-HANDOFF.md and AUTONOMOUS-RUN.md before any work.

Current work (the 62 second promo "masterpiece", from 2026-11-15): read project-docs/promo/PROJECT-HANDBOOK.md first. It is the shared instructions for Claude and Codex: what the project is, where everything is saved, branches, owner directions, who is working on which files, and how to check work.

- Never commit full songs, lyrics, finished videos, frames or any personal data. The one exception: short audio clips under audio/ (60 second promo clips, test clips) that the cloud render needs. This repo is private. Whether to keep clips here or move them to private storage is flagged for Anthony (Astra round 0, finding 6).
- Render only in the cloud (the "Render" workflow). Never on the Mac.
- Work on a branch in your own worktree; open a pull request; the coordinator merges.
- No em dash or en dash anywhere.
