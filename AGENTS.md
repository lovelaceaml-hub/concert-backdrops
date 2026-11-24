# Project navigation

## Current Song 11 assignment, November 24, 2026

Continue the scene-by-scene interview for **Almighty God Who Knows the Future** using clickable questions. Start at the unanswered opening question. Record each answer. Complete the interview and confirm the edit before modifying scenes or launching new renders. The confirmed ending begins on the final chord, turns Earth into the globe of the official emblem, and settles into the promo’s pastel card for the schedule-free 15-second hold. [Song 11 plan and interview](project-docs/production-system/S11-NEXT-CUT.md) · [New-chat prompt](project-docs/production-system/S11-START-PROMPT.txt)

The latest 1080p60 review is complete as a comparison cut. The next creative revision is in planning. Keep the original score and procedural particle style. The owner approves the 1080p review before a 4K60 show render.

## Owner directions (Anthony, November 22, 2026)

These are standing rules for every agent (Claude, Codex, ChatGPT, Gemini). They govern over older records and reviews.

- **Improve the current system, do not replace it.** His words: "ChatGPT was used because it's free. I only used it to establish it and improve the current system ... The intention is to improve the current one; not replace the current one with ChatGPT." Build on the existing engine and render setup; keep what works.
- **The new tools stay.** Blender, the Three.js scene preview, Remotion, Video Shotcraft and the Blender MCP were added "for you to set up and use and make reusable." Get them working and reusable; do not delete or shelve them.
- **No phone versions.** "I don't need a 'phone version'." Do not build phone copies or phone-only review files.
- **Resolution.** The final show performance video is 4K at 60 fps (3840x2160, 60 fps). Work at 1080p until a video is completely figured out (design, timing and content approved); render 4K only after that. "No need to make it 4k until video is completely figured out."
- **GPU work runs on his Mac.** "If GPU is ever needed just use my local computer." His Mac is an Apple M1 Pro (16-core GPU, Metal 4). This is a project exception to the cloud-first rule for GPU work only; CPU work stays in the cloud. Before a heavy local run, check the 1-minute load (stop if above 50) and run with `nice -n 19`. `pipeline/render.py` refuses macOS by default; use its explicit local allowance only for GPU work.
- **Ask when unclear.** "Ask me clarification questions when needed." When a request is ambiguous or changes what he gets, ask him with short clickable options and a recommendation instead of guessing.

- **Chat sandbox limits and working cloud routes.** The earlier browser 3D preview, Remotion and live Blender restrictions applied to the chat sandbox. PR #116 subsequently verified the supported GitHub Actions cloud CPU route; see `docs/VIDEO-PIPELINE-VALIDATION.md`. The earlier sandbox limits did not establish a missing GPU. Anthony's choice: "Try the cloud first" (for example GitHub Actions runners or another cloud setup); use his Mac only if no cloud route works, and say why.
- **Current priorities, in order:** 1) get the new tools (Blender, Three.js preview, Remotion, Video Shotcraft, Blender MCP) working and reusable for any song; 2) build this week's proven quality gains into the current engine so every song gets them; 3) clean up and organize (one plain status page, stale pull requests, rendering spread across many cloud machines). Finished videos from ChatGPT's file library go into the Drive folder "Concert Backdrops - Songs", Videos.
- **Working mode:** Anthony said "Go ahead on your own" for these priorities. Stop only for real decisions or approvals.

- **Full-length songs (Anthony, 2026-11-23).** "Those 60 seconds were just tests. I want them to be made like the promo and song 11." The 60-second promo scenes in `engine/songs/` are tests, not the target. Later the same day he reset the plan: "Forget all of those previous plans. Starting new based on since almighty God knows the future." So the older full-length versions (branches `backdrop/sNN-full`, `backdrop2/sNN-full`) are not the starting point. Build a reusable kit from the Song 11 recreation (Almighty God Knows the Future: `tools/s11_full2`, `tools/s11_renewed`, `tools/s11_cloud`, `tools/s11_delivery`), "but expect to add more to the kit that represents mothers words of love closer". Then make Song 7 ("May No One Ever Feel Lonely") on it, with a check-in after that song.
- **Shared recordings (Anthony, 2026-11-23).** "The songs shared with me, just download them." A song's chosen recording listed in `project-docs/production-system/catalogs/songs.json` may be downloaded even when it is a file shared with him from another account (`tools/drive_sync.py get-id`).

- **Access set up for smooth cloud production (2026-11-22).** Cloud jobs run on GitHub Actions (see `docs/VIDEO-PIPELINE-VALIDATION.md`). They read songs from and save renders to the Drive folder with `tools/drive_sync.py` and the `GOOGLE_DRIVE_OAUTH` secret. Every agent on the Mac commits as `lovelaceaml-hub <281993171+lovelaceaml-hub@users.noreply.github.com>` (GitHub rejects pushes that expose the private Gmail). Gemini helpers may run read-only git history commands. Never print, copy or commit these secrets.

- **Concert playback and music sync (Anthony, 2026-11-23).** How the videos are played on December 6 is not decided yet (finished 4K videos in a cue app, the live engine, or simple play per song). Prepare for both: every song's section markers are exported for show software (`cues.csv`) and for `engine/live.py` (`cues.py`). Music sync tools (`tools/music_sync`, cloud job "Music sync") give real beats, downbeats, sections, per-instrument hits, sung-word timing and rehearsal matching; results land in the Drive folder under Status/Sync. Sung-word timing (`words.json`) is copyrighted lyrics and stays in Drive only. All timing is a suggestion until someone listens and confirms.

## Claude project handoff, November 22, 2026

Start with [CLAUDE-HANDOFF.md](project-docs/production-system/CLAUDE-HANDOFF.md)
and the [dated Drive handoff folder](https://drive.google.com/drive/folders/1lxcic8BcSzNgPtEY_Yg_2TBAbNam72dZ).
The handoff covers the whole concert project, including exact media identities,
reproduction resources, retained integrations, current owner directions and
historical recovery gaps. The current transfer and source-snapshot receipts
are in [the handoff completion record](project-docs/production-system/evidence/claude-drive-completion.json).

The Song 11 recreation is complete at native 1080p60 for design/review. Exact-output
owner creative approval is not recorded, so it is not an approved final 4K60
show master. Preserve earlier 720p artifacts as history; do not generate new
phone versions. Recover existing finished files before considering a new render.
There is no unfinished render queue or active background production service.

The final integrated source checkpoint, including the parallel owner updates through PR #119, is described in [FINAL-SOURCE-CHECKPOINT.md](project-docs/production-system/FINAL-SOURCE-CHECKPOINT.md). Its post-merge manifest and receipt identify the exact final backup; earlier source archives remain verified recovery checkpoints.

## Earlier navigation (historical; superseded by the owner directions above)

On November 22, 2026, the user withdrew the previously provided AGENTS.md
instructions. This page records that change and points to project facts. The
current conversation supplies the working directions; the earlier instructions
remain available in Git history.

## Earlier Song 11 recreation

The complete **Almighty God Knows the Future** recreation is rendered, checked and saved; source integration is tracked
in [PR #112](https://github.com/lovelaceaml-hub/concert-backdrops/pull/112).
Start with the current [handoff](project-docs/production-system/AI-HANDOFF.md)
and [recreation record](project-docs/production-system/S11-RECREATION.md).
The owner corrected the earlier body-fitting fan-study direction; PR #111 is
closed without merging. Current work uses separately shaped modest garments
and the established Song 11 concert world. Exact render/delivery state belongs
to the current production record, not the historical Advanced Dance summary.

## Current project records

- [Start here](project-docs/production-system/START-HERE.md): current delivery,
  recovery path and historical production notes.
- [Session handoff](project-docs/production-system/AI-HANDOFF.md): concise
  continuation and source identities.
- [State](project-docs/production-system/STATE.json): current maintenance status.
- [Deliveries](project-docs/production-system/DELIVERIES.md): finished films,
  support files and exact saved links.
- [Advanced Dance workflow](tools/advanced_dance/README.md): choreography,
  anatomy, validation, deliberate reproduction and packaging commands.

Advanced Dance's two revised 32-second films and complete ten-film package
are saved. [PR #109](https://github.com/lovelaceaml-hub/concert-backdrops/pull/109)
merged on November 22, 2026 at commit
`5a602349f90f50d79968bab77dd08db1a20c4339`. The delivered picture source is
`254414bc0356171f7d5ad89361c75d45fd01a407`; later maintenance records describe
documentation and code upkeep separately from those rendered pictures.
