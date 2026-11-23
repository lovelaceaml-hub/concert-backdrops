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

## Current continuation contract

Follow the current user authorization and the first applicable bounded task in `IMPROVEMENT-QUEUE.md`. Continue already authorized read, build, render, review, save and integration work without repeatedly asking to proceed. If an actual approval control blocks an action, preserve completed work, explain the named blocked action and the stated reason, and prepare a concrete result for approval.

No persistent background service, scheduled render farm or cloud GPU account is configured. A new chat resumes from recorded state, exact inputs and verified frame receipts. Never represent a saved queue as a running service, a source-only fix as a delivered film, or a technical pass as owner approval.

---

## Historical file content retained below

# Autonomous run: continuity pass, attack reviews and 1-minute promos

Started 2026-11-13 while Anthony is away. His words: "Have those threads carry out the work as much as they can from beginning to end, communicating with each other and verifying so you're all on the same page. Then you can have rounds where Astra will review everything as an attacker, with a really strong will against what you're doing. Fable Extra is the one we can use for reference and for advice. ... I'm going to be away from my computer, so all of this needs to be done autonomously. Utilize Astra and solve for very specific things when it makes sense. I want a 1-minute promo for each of the songs. They should be done in the cloud. Have all the docs updated, committed, pushed, and merged."

## Who does what
- Coordinator: the Claude Code session that started the 11 song sessions. Sets the plan, merges, runs the Astra rounds, collects the promos.
- Song sessions (Opus, one per song, ids in VIDEO-HANDOFF.md): each owns its song from design to promo.
- Astra (Codex, model gpt-6-astra): attacker reviews. Reads everything and argues hard against it. Findings go to the owning song session.
- Fable (Claude, claude-fable-5-2, extra effort): reference and advice when a session is stuck on a creative or technical choice.
- Rendering: cloud only, through the "Render" GitHub Actions workflow in the private repo lovelaceaml-hub/concert-backdrops.

## Writing to shared files (Astra round 0, finding 7)
To stop eleven sessions overwriting each other: each song session writes its status only to Status/NN.md (its own file: the board fields plus a short log). The coordinator copies those into CONTINUITY-BOARD.md and production-log.jsonl. Sessions no longer edit CONTINUITY-BOARD.md, AGENTS.md, DESIGN-SYSTEM.md or production-log.jsonl.

## Steps for every song session (phase 1, done 2026-11-13; phase 2 is in PHASE2.md)
1. Continuity pass on its design doc: the provisional decisions (DESIGN-SYSTEM.md 12a), the star history, the live length, exact hand-offs agreed with the neighbor sessions by message, the small fixes in Designs/CONCERT-OVERVIEW.md. Write a plain text copy of the doc to Designs/text/ so Codex and cloud machines can read it.
2. Post its song's facts to its own Status/NN.md (stars lit at start and end, opening frame, closing frame, live length, promo segment); the coordinator copies them into CONTINUITY-BOARD.md.
3. Promo: choose the most moving 60 seconds of its recording (with its key expression moment), cut a 60 second clip into the repo's audio/promo/, write engine/songs/sNN_<name>.py for that minute (palette, scene tracks, the song's expressions and fragments in full wording, opening title card with the poster's concert title, arch state from the star history, an ending card), render stills in the cloud, check them, fix, then render the video in the cloud and check it.
4. Work in its own git worktree and branch, open a pull request; the coordinator merges.
5. Log every change in the Log section of its own Status/NN.md (the coordinator copies it to production-log.jsonl).

## Limits
- Songs 02 and 10 have no recording: their promos are drawn to a calm 60 second visual timeline without music (marked as such) until a recording exists.
- Promos use the engine's current effects (sky, sun, stars, aurora, rain, clouds, lanterns, petals, rays, rings, sparks forming words, the arch) plus short lyric fragments. The signature effects in the designs (shattered sky, frozen rain, the thaw and so on) need new engine work after the promos.
- Heavy work never runs on the Mac.
- Honest label (Astra round 0): these promos are built from the engine's current effects (sky, light, words, the arch). They do not yet show the people of light acting out each expression or the songs' signature effects; that needs new engine work. Say so wherever a promo is delivered.

## Status
See the end of this file and production-log.jsonl.
- 2026-11-13: engine made able to draw any song; cloud render workflow merged (pull request 1); smoke test started.

## Technical how-to for song sessions (read fully before step 3)
Repo: /Users/anthony/Projects/concert-backdrops (private GitHub lovelaceaml-hub/concert-backdrops). Never commit in its main folder; use your own worktree:
  git -C /Users/anthony/Projects/concert-backdrops fetch -q && git -C /Users/anthony/Projects/concert-backdrops worktree add /Users/anthony/Projects/concert-backdrops-wt/sNN -b promo/sNN origin/main
  cd /Users/anthony/Projects/concert-backdrops-wt/sNN && mkdir -p audio/promo && git branch --show-current   (must print promo/sNN; run every later command from this folder)
  If your branch was made before pull request 3 was merged: git fetch -q && git merge origin/main (it brings engine/arch.py, the silent-clip fix and the stricter checks). Your song file's own star_state and link_state are replaced automatically by engine/arch.py.
Promo clip (light, on the Mac): pick the 60 seconds, then
  nice -n 19 ffmpeg -v error -y -ss START -t 60 -i "<song mp3 in this folder>" -af "afade=t=in:d=1.5,afade=t=out:st=58:d=2" -ac 2 -b:a 160k audio/promo/sNN.mp3
Song file: copy engine/songs/s03_original.py to engine/songs/sNN_<short_name>.py and rewrite it for this 60 second promo:
- TOTAL = 60.0 (the video length), SONG_END = 60.0, MUSIC_END = about 59.5; landmarks, palettes (PAL and _pal_keys) and every Track rewritten for this minute and this song's design. Keep the end calm (FADE can end near 60).
- PHRASES: always 9 entries in campaign order (index 0 Greeting ... 8 Compliment), full wording, lines split for layout. Light already lit before this song: star=-100.0, form=hold=1e9. Not lit yet in the concert: form=hold=star=1e9. Lit for the first time here: form, hold, star inside the minute. Lit earlier and spoken again here: star=-100.0 plus form, hold and arrive. Give each spoken expression about 8 to 10 seconds.
- FRAGMENTS: 2 to 4 short lyric fragments from your design: dict(text=..., t0=..., t1=..., out=..., dy=0.0, size=74). Never on screen together with an expression.
- CREDIT: song title and "The Words of Mother’s Love Healing Concert" (the poster title); t_move and t_rest can be earlier in a promo.
- TITLE and TAGLINE as the promo's end card: TITLE label "Healing Concert", lines ["The Words of Mother’s Love"]; TAGLINE text "Sunday, December 6 · 4:30 PM\nThe World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas" (two lines; the newline is written as \n in Python); TITLE_HIT about 50.
- NINTH: set to 1e9 unless your design wants the whole arch to glow near the end.
- Use only the engine's existing effects (see the Tracks). Do not edit render.py, text.py or shaders.py; if you truly need an engine change, message the coordinator instead.
Cloud render (never render on the Mac): commit and push your branch, then
  gh workflow run render.yml --ref promo/sNN -f song=sNN_<short_name> -f audio=audio/promo/sNN.mp3 -f mode=stills -f stills="2,6,12,20,30,40,50,57" -f name=sNN-stills
  gh run watch <id> --exit-status (run it in the background), then gh run download <id> -D /tmp/sNN-stills and look at every still.
  Fix and repeat until the stills are right; then the same with -f mode=video -f name="NN <Song title> - 1 Minute Promo". Download the video artifact, check it (length, music present, frames at several times), copy it to Videos/NN <Song title>/ in this folder.
Songs 02 and 10 have no recording: make a 60 second silent promo. Create a silent 60 second audio file for the workflow (ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 60 -b:a 64k audio/promo/sNN.mp3) and mark the promo as "visual only, no music yet".
Pull request: gh pr create --base main --head promo/sNN with a plain summary; the coordinator merges. Remove your worktree after the merge.
Advice when stuck (Fable, extra effort): claude -p --model claude-fable-5-2 --effort xhigh "<your question with the context it needs>" (run with nice -n 19).
- 2026-11-13: relit lights added (pull request 2). Cloud smoke test passed: song 03 stills rendered on GitHub at 0.4 to 1.3 seconds per frame (run 43535921871). All 11 song sessions briefed for the autonomous run.
- 2026-11-13: Astra round 0 (Reviews/ASTRA-ROUND-0.md): 15 findings. Engine and workflow fixes merged (pull request 3) and tested in the cloud: silent clip stills, and an 8 second video through all four parts, join, music and length checks (runs 43537043841, 43537376826). Concession and Respect relabeled as exceptions for Anthony; song 04 verse 3 back to uncertain; tagline sources corrected (official site: reaches, settles); status files per song; honest promo label.
- 2026-11-13: engine colors merged to main: optional song settings PETAL_COLORS, MOTE_COLORS, LANTERN_COLORS, AURORA_WARM, AURORA_COOL (pair of hex colors, or a function of t returning a pair) and MOTE_Y = (start, end) drift (use (1.05, -0.05) for falling snow). Use them to give each song its own look (DESIGN-SYSTEM.md section 6). git fetch -q && git merge origin/main in your worktree.
- 2026-11-13: Song 09 found its recording has no singing (cloud vocal separation). Checked by the coordinator: "05 God Bless You!.mp3" and "09 Let's Save the World.mp3" are both exactly the official instrumental tracks (subtracting each from the instrumental leaves silence at -91 dB). The sung guide recordings were added for lyric timing: "05 God Bless You! (sung guide, for lyric timing).mp3" (2:22) and "09 Let's Save the World (sung guide, for lyric timing).mp3" (3:06). The coordinator's earlier note that these two were "full sung arrangements" was wrong. Song 05 should time its lyric moments from its sung guide.
- 2026-11-13: Anthony asked for magnificent promos beyond the current engine effects (UPGRADE-SPEC.md). Engine builder session started (local_c76679ae-d31e-4e0b-a4e6-001c8e7677f1): scene plates, people of light, effect layers, fragment styles, shared figure library. Song sessions plan 3 to 6 scenes and paint their plates into Assets/sNN/ until the engine is ready.
- 2026-11-13: copied the 21-pose figure library to Engine/Figure Library/, the demo plates to Engine/Demo Plates/, and the demo frame sheets to Videos/Engine Upgrade Demo/ (from the local git copy; no download). The full demo video stays on GitHub.
- 2026-11-13: all local sessions stopped (Mac overload). Anthony started one cloud session on claude.ai/code that runs project-docs/CLOUD-RUN.md in the repo: engine finish, 11 promo rebuilds with cloud helpers, attack reviews, merging. The coordinator watches main for CLOUD RUN DONE (a light git check every 15 minutes), then copies promos to Drive and runs Astra.
