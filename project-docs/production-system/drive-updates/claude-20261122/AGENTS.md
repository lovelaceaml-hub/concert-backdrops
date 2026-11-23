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

## Shared execution rules

Read the current user's direction and the current repository instructions before historical notes. Use an isolated branch/worktree, one writer per area and one coordinator for shared lighting, timing and assembly. Preserve the approved engine snapshots and exact recording identities. Keep full songs, lyrics, frames, videos and credentials out of Git.

Use `scripts/concert` for status, catalogs, source verification, plans, audio preparation, exact archive restoration and handoff export. Use `scripts/video produce` for registered production projects. Keep model and motion provenance; generated raster assets in legacy folders are excluded. Cloud CPU remains the default, no cloud GPU provider is configured, and no Mac rendering is used by this increment.

The shared queue is bounded continuation work, not an unattended service. Report actual rendered output, review scope, archive links and remaining limitations at closeout.

---

## Historical file content retained below

# Concert Backdrops: instructions for every AI

All AIs (Claude, Codex, Gemini, helpers) work from this one folder. Anthony, 2026-11-13: "Make sure that this is all being recorded, communicated, and stored in the same folder so that all the AIs can work together on the same project". Reorganized 2026-11-13 by the coordinating Claude Code session; every earlier instruction is kept below.

## Read first, in this order
1. DESIGN-SYSTEM.md: the message, the number one priority, the official concert facts, the rules, and the decisions waiting for Anthony.
2. README.md: what is where.
3. Your track's status page: VIDEO-HANDOFF.md (videos) or SHARED-HANDOFF.txt and production-status.json (sample pictures).
4. The last lines of production-log.jsonl.

## For everyone
- The message (Anthony, 2026-11-13): "Make sure each of the chats and the whole project understand that the mother's words of love that bring peace are the main theme and the main importance of this concert. That is the message we are trying to get across." Every picture, video, document and decision here serves it.
- Number one priority (Anthony, 2026-11-13): study the Mother's Love campaign thoroughly first, then make everything magnificent, glorious and heavenly. Full quote in DESIGN-SYSTEM.md section 2.
- Helpers (Anthony, 2026-11-13): "Each thread can use as many Haiku agents as necessary. No limit in the cloud." Use them for research, reading the campaign, checking documents and measuring recordings. Heavy work (rendering, big media jobs) runs in the cloud, never on the Mac.
- Add a line to production-log.jsonl for every change. Do not delete anything. Do not edit the MP3s, the Lyrics doc or the Visual Plan doc. Do not copy lyrics into new files. No em dash or en dash anywhere. No paid services without Anthony's OK.
- Shell commands on the Mac run with nice -n 19; if the 1-minute load is above 50, pause and say so.
- One active writer per area at a time; do not start other AI sessions or duplicate generation without coordination.

## Two tracks, separate areas
- Video track (Claude Code coordinator and the 11 song design sessions): Engine/, Designs/, Storyboards/, Videos/, VIDEO-HANDOFF.md. Engine code also lives in the private GitHub repo lovelaceaml-hub/concert-backdrops for cloud rendering.
- Samples track (Codex): Samples/, SHARED-HANDOFF.txt, production-status.json, generation-archive.json, generation-specifications.json, FILE-LIST.txt, Generation Archive/.
- Each track never writes to the other's area. Shared files (this one, DESIGN-SYSTEM.md, README.md, production-log.jsonl, Reference/) are open to both; append or edit carefully and log it.

## Samples track rules (written by Codex, kept as written)
Task: 30 individual PNG sample backdrops, not video production. Shot list owns scene, phrase, color, and exact filename. Anthony explicitly superseded its photoreal style: match his glowing scenic reference. People must be artistic outlines or forms of light, mist, ribbons, or particles, never actual-looking people. Sparkles are optional. No realistic faces or skin. Heavenly Mother only rear-view outline or hands.
Reference: Design Reference.png in this folder. Bottom third calm and uncluttered. Text only where shot list specifies a phrase, exact wording, elegant thin serif in upper third with specified color and faint glow. No titles, extra text, logos or watermarks. Preserve all existing source assets.
Native image generation authorized. One generation at a time. Inspect every output before saving. Redo once for defect, save best and log any remaining issue.
Samples contains final selected images only, exact shot list names. Update shared records after each batch. Check production-status.json and live Samples files before resuming. Earlier versions remain in generator libraries; don't delete them.
Note from the video track: the shot list's shortened expression wording and older style are superseded by DESIGN-SYSTEM.md (full campaign wording, label above the phrase). See REVIEW-Samples-2026-11-13.md and REVIEW-Claude-Designs-2026-11-13.txt before any new generation.


## Natural performance update - PR 104

The owner's latest direction is to keep improving fluid, expressive whole-body motion, including dancing. Read the current repository's `project-docs/production-system/NATURAL-PERFORMANCE.md`, `MOTION-LIBRARY.md`, `catalogs/motions.json`, and the current delivery/state records before continuing. The reusable wrapper is `tools/concert_dance/performance.py`; reproduction commands are in that directory's README. Preserve the approved promo and Song 11 sources.

The registered `concert-dance-study` uses an eighteen-second continuous clock and six cloud CPU workers at native 1080p60. `concert-dance-study-4k` configures native 3840x2160 with three CPU workers. A native 4K still is verified; the full 4K movie is not yet rendered. Use the delivery catalog for the exact finished media, hashes, reviews and owner approval status. Do not infer a completed render from a preset.

The conditioned dance reuses the prepared CMU 05_02 capture. Two figures with a phrase offset are not a newly captured duet. Stored 30 Hz source poses are interpolated for 60 fps output. Inspect support, pivots, flight, landing, hands and cloth in motion. Keep source frozen during a render and use the single coordinator for frame receipts. The next creative work is a broader independently reviewed motion library, authored hands, better costume turns and complementary duet choreography.

The exact saved replacement `Concert-Production-System-Handoff-2026-11-20.zip` is uploaded and raw-byte verified in Production System (file ID `1gp0x2dnj06eIPDuq6vSGpGtKn_bvKrML`, 350534 bytes, SHA256 `eb8bba933a37179fa970c84aecc67cbc0b493809d1e2b2e7863c3900b9606537`). All three prior Drive operations are complete. That ZIP is an immutable historical snapshot; use current main and PR104 for newer source and records. Do not repeat the completed transfer or ask for its confirmation again.


The complete eighteen-second 1080p60 dance movie now passed both technical audits and is delivered with its native 4K still and decoded review sheet. All 197 frozen picture inputs match. All three Drive copies were downloaded and matched by raw bytes and SHA256. The independent final visual inspection covered 89 selected encoded frames; it preserves the long preparation and settling as next creative work. No owner approval or real-time naturalness certification is recorded.

- [Natural-Dance-Duet-18s-1080p60.mp4](https://drive.google.com/file/d/1IImU7ohiNhI86WHtIPNB_3S0iFD2HgAH/view)
- [Natural-Dance-Duet-Native-4K.png](https://drive.google.com/file/d/1nB2MjshQhFJHe7c-KyjxcuWBBPGvFYyq/view)
- [Natural-Dance-Duet-Motion-Review.jpg](https://drive.google.com/file/d/1AmBWnRldfLNjbL9Vh31WzMEhAPby12Vm/view)

After rendering, run `env PYTHONHASHSEED=0 .venv/bin/python tools/concert_review/dance.py`. It checks the completed native movie, exact presentation times, unchanged inputs and canonical audio alignment. The shared production-system handoff and improvement queue contain the detailed source, capture limitations and next actions.


## November 21, 2026: original fan and silk trio

The owner asked to try the three supplied references as well as possible without waiting for more uploads. A new original twenty-second performance is complete at native 1080p60 with three distinct authored roles, planted steps, two held fans and finite simulated silk. All three media files below are saved and their Drive bytes verified. Picture source: `dffe8f165944c627ae39a8bb7d47bc5a9e703305`. Integration record: https://github.com/lovelaceaml-hub/concert-backdrops/pull/106. Exact-output owner approval is not recorded.

| Saved file | Verified Drive copy | Contents |
| --- | --- | --- |
| [Fan-Silk-Trio-20s-1080p60.mp4](https://chatgpt.com/library?file_id=libfile_5d95a136726c8191a7eacbf8509a9bec&account_id=personal) | [Open in Drive](https://drive.google.com/file/d/1e4p1pwcjfhZN35lD-ducwa_mU2_M5dsh/view?usp=drivesdk) | Original continuous trio with distinct authored roles, grounded steps, held fans, finite silk, mirror lake and a gentle closing pose. Not reconstructed source choreography. |
| [Fan-Silk-Trio-Native-4K.png](https://chatgpt.com/library?file_id=libfile_401345b49ea88191a3d6ba7e0c794939&account_id=personal) | [Open in Drive](https://drive.google.com/file/d/1r3NL97rDqXL1waC_gKflb7cODqh7n0dV/view?usp=drivesdk) | One separately rendered native 3840 x 2160 frame. No upscaling; a full 4K movie is not included. |
| [Fan-Silk-Trio-Motion-Review.jpg](https://chatgpt.com/library?file_id=libfile_0a92fd2387848191a628133b595d7be6&account_id=personal) | [Open in Drive](https://drive.google.com/file/d/1x418ePl741G1Ooo0cZHzwwYirYxFQXG3/view?usp=drivesdk) | Nine labeled frames decoded from the final movie, with uniform scaling and no brightness or content edits. |

The full film passed the pipeline and independent technical audits: 1,200 frames, exact presentation timing, unchanged 201-file inputs and canonical audio alignment. Fourteen focused motion/prop and registration checks passed. The final visual review inspected 37 ordered decoded samples plus a separate nine-frame overview; it was not real-time playback. Silk sometimes overlaps the upper body and mostly drapes as a finite panel. A full 4K movie has not been rendered.

Read the current repository handoff and reproduction instructions:

- https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/START-HERE.md
- https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/FAN-SILK-PERFORMANCE.md
- https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/tools/concert_fan/README.md
- https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/NEXT-PERFORMANCE-UPGRADES.md

The first two source posters could be inspected; moving footage was unavailable. This is original choreography, not a reconstruction of the three source videos. Continue useful original work without another blocking upload request. For closer fidelity, continuous full-body footage is helpful. The next priority is an expressive complete phrase with weight transfer, travel, turn, changed level and recovery, then better skirt/silk response.

Use cloud CPU rendering. On memory-constrained hosts, render review ranges 0:400, 400:800 and 800:1200 as separate invocations before producing the final movie; run native 4K checks separately. Resume reuses validated frames. Do not modify the frozen picture baseline to make an audit pass. Preserve all earlier delivery records and the exact previously confirmed ZIP; do not replace or upload that ZIP again.
