# Autonomous run: continuity pass, attack reviews and 1-minute promos

## Current continuation — November 22, 2026

Start with [the Claude handoff](production-system/CLAUDE-HANDOFF.md),
[current state](production-system/STATE.json) and the standing owner directions
in [root AGENTS.md](../AGENTS.md). The sections below retain their earlier
production/design context. Dated instructions about queues, phone copies,
missing song recordings or cloud-only GPU use do not override the current
handoff and owner directions. All eleven original song recordings are retained;
older full-song movie recovery gaps are documented separately. The completed
renewed Song 11 movie is a 1080p60 design/review delivery; final4K60 requires
owner approval of design, timing and content. There is no unattended render queue.

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
