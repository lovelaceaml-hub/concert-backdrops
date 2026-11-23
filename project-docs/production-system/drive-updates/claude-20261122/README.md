# Current cloud tools and access update - November 22, 2026 (America/Los_Angeles)

This addendum takes precedence over conflicting environment and source-snapshot statements in the preserved handoff below. [PR #116](https://github.com/lovelaceaml-hub/concert-backdrops/pull/116) merged the reusable cloud implementation at `3812463e1196f4c47b468e05060dbc1c8154ff75`. Continue from current main and the owner directions in [root AGENTS.md](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/AGENTS.md).

## Cloud proof scope and local runtime distinction

The independently reviewed [cloud run 45124306242](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45124306242), at the earlier `d3158465` source, passed all eight tool steps: bootstrap, browser doctor, Three.js capture, pipeline preview, Remotion, Blender background rendering, the reusable song scene, and Blender MCP. Evidence includes real animated CPU WebGL frames, a live Blender MCP connection reporting 5.2.4 LTS, and four technical-demo render QAs, including the four-second, 240-frame Song 11 scene excerpt. The separate Docker build and Drive access jobs passed. These are Ubuntu 24.04 GitHub Actions CPU results; they do not establish browser, Xvfb, Docker or live-GUI readiness inside this chat's local sandbox.

The exact PR #116 head `285df02e51cc68073fe17c8a06ae0d7f54737df7` also passed [run 45125796332](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45125796332), completed at 06:47:47 UTC on November 23 (November 22 in the owner's timezone). All eight original tool outcomes and all three jobs passed; the actual outcome summary was checked because these tool steps use continue-on-error. See the [verification record](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/docs/VIDEO-PIPELINE-VALIDATION.md). Shotcraft Workbench's interactive browser/export flow was not exercised. Docker evidence proves a build. Technical demos do not establish all-eleven-song coverage, a final 4K film, or creative approval.

## Reusable scenes and cloud access

Use [the production guide](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/docs/VIDEO-PIPELINE.md), `.github/workflows/tool-proofs.yml`, and the `song-scene-demo` project. The configurable `scenes/p3d/song_scene.py` routes existing `engine/songs` scenes through p3d-kit with song, audio or prepared features, start time, bloom and grain parameters. Project shots define duration; approved scene registrations remain frozen. The proof command is `./scripts/video preview song-scene-demo --quality review`.

Cloud jobs use `tools/drive_sync.py` inside the existing Concert Backdrops - Songs folder: `list`, `get` for song sources, `put` for renders, and `check` for a small read/write/delete probe. The Actions secret **name** `GOOGLE_DRIVE_OAUTH` supplies the owner's authorized read/save access; `GOOGLE_DRIVE_SA_KEY` is the read-only fallback. Keep secret values out of logs, chats, source and archives. Full song recordings stay in Drive and are fetched for the job. Preserve the owner's cloud-first CPU and separately conditioned Mac GPU directions already recorded below.

Per the current owner access directions, agents committing on the Mac use `lovelaceaml-hub <281993171+lovelaceaml-hub@users.noreply.github.com>` so pushes do not expose the private Gmail. Gemini helpers may run read-only Git history commands.

## Current source archive

The initial 861-entry source archive frozen at `3ef80d97d2cc25d5201195bb8ced3646811200db` is a historical snapshot predating PR #116. Resolve the current source archive and its verification from [the handoff completion record](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/evidence/claude-drive-completion.json); the source refresh is maintained separately from this note. Song 11's delivered picture identity and recorded approval status remain as stated below.

---

# Current project handoff for Claude — November 22, 2026

This current section supersedes conflicting dated directions in the preserved historical body below.

Start here:

- Claude handoff: https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/CLAUDE-HANDOFF.md
- Drive handoff folder: https://drive.google.com/drive/folders/1lxcic8BcSzNgPtEY_Yg_2TBAbNam72dZ
- Current state and exact transfer receipts: https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/evidence/claude-drive-completion.json
- Whole project: https://github.com/lovelaceaml-hub/concert-backdrops

## Current owner directions and production status

The latest owner priorities (GitHub PR #114) are already authorized: first make the retained tools work and be reusable for every song, then integrate proven quality gains into the current engine, then simplify status, stale PRs and distributed rendering. For browser 3D, Remotion and live Blender blocked by cloud sandbox limits, try permitted cloud routes first; use the owner's Mac only if none works and explain why. These limits do not establish a missing GPU. The current request is to finish the Claude handoff.

Improve the existing concert system. Preserve and make reusable Blender, the Three.js scene preview, Remotion, Video Shotcraft and Blender MCP. Their source, pins and configuration are retained; installation and runtime readiness must be checked in the receiving environment. The historical integration setup report is not a fresh verification of this checkout.

Work and review at 1080p. Render the final show version at 3840×2160 and 60 fps only after design, timing and content approval. Do not create new phone versions. Existing lower-resolution files remain historical artifacts. CPU work stays in the cloud; GPU work, if needed, uses the owner's M1 Pro Mac (16-core GPU, Metal 4), with the recorded load guard and nice -n 19. Root AGENTS.md contains the standing November 22 owner directions; its earlier navigation-only role is superseded.

The complete 275-second Almighty God Knows the Future recreation is finished at native 1080p60, checked and saved. It preserves the original music and concert story, with separately shaped modest costumes and continuous conducting. Exact-output owner creative approval has not been recorded; this is not an approved final 4K60 show master. The producing commit remains eec8d16519ea82309ef851975792e9dfc548da03 and its completed cloud run is 45108198761. Documentation and transfer changes do not alter that picture identity. All eleven canonical original song recordings have verified existing Drive locations. Historical full-song film locations and older alternate encodes remain separately labeled in the handoff.

There is no unfinished render queue or unattended production service. Recover the finished files and current resources before beginning the owner's next requested change. Follow the current handoff's inventories and verification levels for media, exact recovery parts, source snapshots and preserved review evidence. Larger files may have both a directly available Drive copy and an independently verified recovery set; use the recorded hashes and do not infer byte identity from names alone.

---

# Preserved earlier project record

The complete earlier document follows without edits. It is retained as history; old queue, cloud-only, phone-version or missing-recording statements do not override the current section above.

---

# Current production handoff: November 20, 2026

This current section supplements the historical record below. The owner approved the Song 11 beauty study and explicitly reopened improvement work, including saving, documenting, pushing and merging the shared system. Earlier stop instructions describe their earlier sessions; apply the current user's direction to the current task.

Integration record: [pull request 102](https://github.com/lovelaceaml-hub/concert-backdrops/pull/102). If it is still open, read the same production-system paths on [the integration branch](https://github.com/lovelaceaml-hub/concert-backdrops/tree/system/concert-production-kit/project-docs/production-system). After it merges, use the current main links below.

Fresh cloud CPU setup for these studies is `python3 scripts/bootstrap.py --p3d-only --reference-fonts`. The exact 74 reference fonts are reconstructed and checked from pinned source packages. A separate checkout reproduced a native frame exactly with the existing locked runtime; a new operating-system installation was not claimed.

Start with [START-HERE.md](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/START-HERE.md), [AI-HANDOFF.md](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/AI-HANDOFF.md), and [STATE.json](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/STATE.json) on current `main`. The versioned repository is the source for executable code and current catalogs. This header is a navigation and status summary, not a replacement for those records.

The approved 66-second Nine Colours Revision 3 promo remains the creative reference. The owner-approved 30-second Song 11 beauty study is the clarity and production reference. Approval belongs to those specific files. New Consideration and model studies require their own review.

All eleven selected full original recordings were downloaded, hashed and decoded during this setup. Songs 02 and 10 have full recordings even though the inherited promo clips remain silent placeholders. Read the [source audit](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/SONG-AUDIO-AUDIT.md) and exact song record; rehearsal/live arrangement conformity has not been established by this audit.

## Current shared entry points

- Repository: https://github.com/lovelaceaml-hub/concert-backdrops
- Production instructions and catalogs: `project-docs/production-system/`
- Media home: https://drive.google.com/drive/folders/1hrk62bFIOHv2NwXvYl2bNSmp0cwBoXrr
- Planned portable handoff location: https://drive.google.com/drive/folders/1QDGGqqkJlbovBLCthX-QChqfD8zSmK8X

Check the repository state for actual upload completion. The approved Song 11 viewing MP4 and exact master archive are in the media home. The exact approved master can be restored from its two verified binary parts with `scripts/concert restore-master`. New media and handoff files are separately listed in the upload manifest and must not be assumed present before their recorded upload succeeds.

---

## Historical file content retained below

# Concert Backdrops

**Owner-authorized integration, 2026-11-16:** the owner explicitly requested "Push, merge, and commit everything" after the stopping point. The completed video stack (#73, #71, #70, #69, #66, #64, #59, #57) and speed PR #55 are merged into `master/words-that-bring-peace`. Documentation is being integrated through #72 and #58 into `main`; [the integration record](https://github.com/lovelaceaml-hub/concert-backdrops/pull/55#issuecomment-6933778970) tracks final merge results. This supersedes earlier draft/unmerged instructions for these named PRs only. The exact 4K60 file is unchanged; local download and quality review are still unconfirmed. No render or paid workflow was started.

**Codex stopping point, 2026-11-16 (Las Vegas):** paused at the owner's request after saving findings. The exact 4K60 master and its Drive parts are preserved; download to the owner's computer and review of the quality export are still unconfirmed. A local Codex handoff prompt, checksums, known transfer failures and the next step are saved in [the session checkpoint](https://drive.google.com/file/d/1BdI-R2ceMFqyBe1nsxSdzBtM6dG5K9UN/view). Resume with local delivery, not another render or encode. No background render job is running, and PRs remain draft and unmerged.

**Current quality master, 2026-11-16:** one native 3840x2160, 60 fps, 10-bit export of the approved Revision 3 is complete and checked. Added composite grain is removed; the edit and exact music stream are preserved. The owner requested one highest-quality file. The exact 318,834,702-byte master is available in [Google Drive](https://drive.google.com/drive/folders/1_m5HLeo8brJgZMgdXleEbY7klrAGaxgS) as four parts with an offline helper that restores one original MP4. Download the folder on a computer, unzip it, open Open-to-save-video.html, select all four parts, then save the video. The restored file was verified byte for byte. The owner's download is not yet confirmed; no smaller encode was created. The new quality file awaits owner review; prior approved files remain archived. [Quality record and checks](https://drive.google.com/file/d/1Naj7qe3t4kvS1KV8xYG2PrbYJcFc5On8/view).

## Approved promo, 2026-11-16

The owner approved Film 10, Nine Colours, Revision 3: 66 seconds at native 60 fps. [Approved delivery and handoff](https://drive.google.com/file/d/1IwhQMsGrQTG9I5wMCIgSRTPtM8jkdcTL/view) records the exact source tag, video links, checksums and validation. [Phone video](https://drive.google.com/file/d/1CBQ4OtpLW3Kp3zBWsEMkjXYiAWUwhDQw/view) and [1080p master](https://drive.google.com/file/d/1gcxnb4Oyexq5Kbb8LvFWqOrikF-BVSht/view) are saved in Videos. The handbook, PHASEB UPDATE 21 and Film 10 handover are in Promo masterpiece (2026-11-16). Preserve this cut; future alternatives get a new revision. PR #71 remains draft and unmerged.

Video backdrops for "The Words of Mother's Love Healing Concert", performed by choir and orchestra at The World Mission Society Church of God, 6720 W Sahara Ave, Las Vegas, on Sunday December 6, 2026 at 4:30 PM. Eleven songs, each with a video on the screen behind the performers.

**The message:** the Words of Mother's Love bring peace. That is the main theme and the main importance of the concert, and everything here serves it.

This Google Drive folder (Anthony's lovelace.aml account) is the project's one official home. Every AI and every file works from here.

## Start here
- DESIGN-SYSTEM.md: the message, the priorities, the official concert facts, the rules every video follows, and the decisions waiting for Anthony.
- AGENTS.md: how every AI works in this folder.
- VIDEO-HANDOFF.md: where the videos stand, song by song, and the next steps.
- Designs/CONCERT-OVERVIEW.md: all 11 designs side by side and the problems between them.
- SHARED-HANDOFF.txt and production-status.json: the 30 sample pictures (Codex).
- production-log.jsonl: a line for every change, by every AI.

## Folders
- Songs: the MP3s at the top of this folder, named in set order (02 and 10 still missing).
- Designs/: one detailed video design document (Google Doc) per song, and the concert overview.
- Storyboards/: planning stills (song 03 so far).
- Videos/: finished videos, one folder per song.
- Engine/: the graphics program that draws every frame, its handoff and PROCESS-AND-TOOLS.md. Working copy of the code: private GitHub repo lovelaceaml-hub/concert-backdrops.
- Samples/: the 30 sample pictures, with Generation Archive/ behind them.
- Reference/: the concert poster and the set list with live lengths.
- Reviews: REVIEW-Samples-2026-11-13.md (Claude on the samples), REVIEW-Claude-Designs-2026-11-13.txt (Codex on the designs).
- Google Docs: "Concert Backdrops - Lyrics" and "Concert Backdrops - Visual Plan" (the early plan, now superseded by Designs/).
