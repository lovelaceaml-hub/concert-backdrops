# Phase 2: rebuild every promo with the upgraded engine

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

Read this when the engine builder (or the coordinator) tells you "engine ready". Also read UPGRADE-SPEC.md, engine/UPGRADE-HOWTO.md in the repo, and Reviews/ASTRA-ROUND-1.md (round 1 attack on the first promos).

Anthony, 2026-11-13: "Do not be lazy. Make these videos magnificint. They shouldnt just look like one scene but multiple things should go based on the theme, make sure the full expressions a created and used beyond only using current engine effects."

## What every promo must have (checked by Astra round 2)
1. 3 to 6 scenes (your plates from Assets/sNN/ plus engine effects), changing on musical moments with soft transitions. Composition and a dominant object must differ from other songs, not just colors (Astra round 1 finding 4: 05 and 11, 03 and 08, 01 and 07 were too alike).
2. People of light act out every expression you show (shared figure library in assets/figures/, your own special figures if any), and the full campaign words appear as the act happens, then rise into the star.
3. At least two of your design's signature effects, done for real with the new effect layers or plates.
4. Reading time contract (finding 2): every expression stays fully formed and solid for at least 6 seconds after formation finishes (formation takes about 3.75 seconds, the dissolve about 1.6 seconds), with no fragment, other text or bright effect over it. Plan about 11 seconds per expression. Fragments: at least 3 seconds solid. Leave a clean gap of at least 0.5 seconds after a dissolve ends before the next text starts (finding 9).
5. Legibility (finding 3): dim and calm the scene behind every piece of text, including labels and the end card; no petals, sparks or rays crossing letters; check the end card text at full size.
6. Bottom third calm (finding 12): no bright reflections, rings or particles in the lower third while performers stand there; words form above it.
7. End card, three lines (finding 1): TITLE label "Healing Concert", lines ["The Words of Mother’s Love"]; TAGLINE "Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\nThe World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas". After each expression, the scene visibly moves from unrest to stillness or warmth: practicing the words brings peace.
8. Star history exact for the cropped minute (finding 5): any star lit earlier in your song before the promo's minute starts lit (star=-100.0), and a relight uses arrive.
9. Track keys strictly increasing (finding 8). The engine now refuses unsorted keys.

## Song-specific findings from Astra round 1
- 05: start star 8 lit and relight it with arrive (finding 5); time the sister verse from the sung guide "05 God Bless You! (sung guide, for lyric timing).mp3", mapping its cue words onto the instrumental minute (finding 7); calm the bright sky behind text; fix the slashed H in HEALING if it is still there (finding 3).
- 09: palette keys out of order around 8 seconds (finding 8).
- 11: rays keys 49.5 then 49.0 out of order (finding 8); text overlaps at 46.7 to 50.6 (finding 9); pale text on pale light at 47 seconds (finding 3).
- 04: pale text on pale light at 45 seconds (finding 3).
- 03 and 08: separate by composition and objects, not just color (finding 4).
- 01 and 07: separate by composition and objects (finding 4).
- 02 and 10: keep "visual only, no music yet" in the file name; 10 marks its three expressions as illustrative until lyrics exist (finding 14).

## Steps
1. In the repo, make a fresh worktree from the new main: git -C $HOME/Projects/concert-backdrops fetch -q && git -C $HOME/Projects/concert-backdrops worktree add $HOME/Projects/concert-backdrops-wt/sNN -b promo2/sNN origin/main, then cd there.
2. Copy your plates and special figures from Assets/sNN/ into assets/plates/sNN/ and assets/figures/ (JPEG plates under 1.5 MB each).
3. Rewrite your song file for the new minute: SCENES, FIGURES, effect Tracks, fragment styles, the timing contract, the end card. Keep your song's look.
4. Cloud stills first (8 to 12 times across the minute, including every expression and the end card), look at every one at full size, fix, repeat. Then the cloud video; check length, music, and frames at 8 or more times. Save over your promo in Videos/NN */ (keep the old one as "... - 1 Minute Promo (v1).mp4") and refresh Status/NN-stills.jpg.
5. Pull request into main; update Status/NN.md (only your file) and your design doc's "Promo v2" section. End your turn with the pull request link and the promo path.
GitHub: one background gh run watch <id> --exit-status --interval 180 per run; never poll in loops.
