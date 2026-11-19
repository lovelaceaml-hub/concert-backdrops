# Song 09 "Let's Save the World": backdrop version 2 checklist

Every rule of the version 2 brief (2026-11-18), with yes or no and where it was checked. "Stills" means the landmark stills rendered in this session and looked at at full size and at quarter size; "code" means `tools/s09_full2/`; "render" means the checks on the finished files (section at the end, filled after the render).

## Sources

| Rule | Yes/No | Where checked |
|---|---|---|
| Drive rule files read (AGENTS, DESIGN-SYSTEM, VIDEO-HANDOFF, AUTONOMOUS-RUN, CONCERT-OVERVIEW, Status 09, PHASEB through update 25, handbook) | yes | read through the Drive connector by a helper; differences below |
| Repo handoff, AGENTS.md, handbook, approved R3 source read | yes | HANDOFF-FULL-BACKDROPS.md, tools/nine_colours_minor, engine/titles.py, words.py, brand_symbols, brand_hearts |
| First run reused where good, its faults fixed | yes | timeline, boats, beads, shore, people, saints, net kept; comets, 30 fps, bottom-left signature, dark night, violet text removed |
| Campaign studied (about, checklist, expressions page) | yes | Encouragement: sincere support for someone in a hard moment, "pray" or "root" for them, so they know they are not alone |

Where the brief and the Drive files differ: DESIGN-SYSTEM 4 still says 30 fps and has no 15 s hold or top-left signature lines; the brief (2026-11-18, newer) wins and is followed. The handbook says only gold glitter people are approved (crystal not yet): only gold glitter people are used, which satisfies both.

## The message and the bar

| Rule | Yes/No | Where |
|---|---|---|
| Mother's words of love that bring peace are the theme; every scene serves it | yes | design idea kept: each act of love calms the water; the Encouragement is the heart; the net carries the colours of Mother's words |
| Majestic, heavenly, warm; never dark, cold, empty, eerie | yes | stills: darkest landmark mean about 120 of 255 (was 58 in the first run); the early-church night is a luminous twilight |

## Length and timing

| Rule | Yes/No | Where |
|---|---|---|
| Music part exactly the live length 276.0 s, then a 15 s calm hold | yes | code: TOTAL 291.0, FPS 60, 17,460 frames; render check |
| Reference measured; within 1 s so used as is; stated in TIMELINE | yes | 275.736 s; TIMELINE.md |
| CUES.md with section starts, what is on screen and the calm moment ending each | yes | CUES.md |
| Hold gently alive, never black | yes | stills 4:36, 4:45, 4:50.98 |

## Look

| Rule | Yes/No | Where |
|---|---|---|
| Song 09 look: misty sea dawn at Galilee, teal, sea green, pearl, pale gold, mist and cloud, glittering water, horizon mid, wide sea | yes | stills |
| Signature effects from the design are the hero effects (calling road of light, shore of grains, lamp saints, net of light, boats) | yes | stills 0:59.5, 1:25, 2:40, 4:02 |
| No comets (song 01 only) | yes | code: Comets class removed; stills |
| No effect reused from another song's signature; R3 craft kept (word style, people quality, warmth, eased motion, no grain) | yes | code |

## Expressions and the arch

| Rule | Yes/No | Where |
|---|---|---|
| Exact wording from words.EXPRESSIONS, "(or root)" kept | yes | code uses expr="Encouragement" (the engine's own wording) |
| Website colour #9E6AF6 for Encouragement | yes | words.COLORS |
| Expression only where the lyric line is that act (design places only Encouragement) | yes | TIMELINE, ACTING |
| Readable 8 to 10 s, nothing competing in its box | yes | 2:58.5 to 3:07.5 (9 s); code dims every light in the reading box; no other text on screen |
| Upper middle, block centred about a third down, people below | yes | still 3:02 |
| Words collapse into star 7 | yes | leave="arch" to star 7; still 3:08.5 |
| Relight only: brief flare and one new thin ring; no new star | yes | code StarRing at 3:10; arch all nine lit start to end |
| The people do the expression while it reads (hand on the shoulder of someone kneeling) | yes | ACTING.md; stills 3:02 |
| Symbol in the world in the expression colour, not an icon over the words | yes | praying hands traced by violet sparks over the lamps, 2:51 to 2:56 |
| Hearts in the expression colour drift off the expression | yes | violet hearts of light 3:07.6 to 3:14; still 3:10.5 |

## People

| Rule | Yes/No | Where |
|---|---|---|
| Only radiant whole people (gold glitter here), clothed in light, soft faceless heads | yes | code LOOK glitter; stills |
| Fewer people, more light; a few tender acted moments | yes | ACTING.md |
| Touching only between two people of the same gender | yes | two men (fishermen), two women (Encouragement) |
| Refined eased movement, natural hands | yes | engine refined acting (master_acting, pairs); motion strip |
| Heavenly Mother only from behind | yes | facing away from camera toward the sunrise |

## Words on screen

| Rule | Yes/No | Where |
|---|---|---|
| Opening readable from frame 0, held at least 7 s: logo, HEALING CONCERT, title lines (second italic), song title large, R3 lockup style, on calm sky | yes | cards09.py; stills 0:00 and 0:07.5 (readable to 7.6 s) |
| Signature top left from the end of the opening to the last frame, never flashing, same lines as all songs | yes | windows 7.9 s to the end, one slow fade in; stills from 0:10 to 4:50.98 |
| Date line capitals at least about 22 px at 1080p | yes | Jost 600 at 34 px: capitals about 24 px; fix 1: the last line (HEALING CONCERT · LAS VEGAS) navy, readable on every sky |
| Nothing covers the signature; 40 px from any expression box | yes | lights dimmed in its corner; still 3:02 (label clear of it by more than 100 px) |
| 3 to 6 short fragments, each its own effect, never with an expression, never full lyrics | yes | 4 fragments: pen, gather, forge stitch, net weave |
| Navy #1f2a6b with soft white glow on bright skies; warm white on darker skies | yes | fragments, lockups, the Encouragement (fix 1) and all four signature lines navy on the bright skies |
| No end card (song 11 only) | yes | ends on its calm hold with the signature |

## Never list

| Rule | Yes/No | Where |
|---|---|---|
| 1 No white-outs | yes | brightest frame mean 174 of 255; the cast net's soft white blob (3:49) found in the motion strip and fixed; render check |
| 2 No white text on pale skies | yes | fix 1: the Encouragement is navy and stays navy until its letters break up; motion strip 3:08 to 3:10.4 |
| 3 Nothing crossing a reading box or the signature | yes | code Clear wrapper; fix 1: the pair now stands below the Encouragement box; stills 3:02 to 3:06 |
| 4 One expression at a time | yes | only one |
| 5 No garbled letters while words form or leave | yes, one note | motion strips: letters assemble from light for about half a second before they settle; no broken letters once readable |
| 6 No words mirrored in water | yes | reflect=False on all words |
| 7 No dark, brown, solid or mannequin people; big enough | yes | stills (Encouragement pair about a fifth of the frame height) |
| 8 No mushy blur, jitter, popping or sliding | yes | motion strip |
| 9 Bottom third calm | yes, one note | code: lights fade out below about a third of the height, BOTTOM_CALM, people not mirrored, rings small and far out; fix 1: the shore line of grains dimmed to faint and steady; the Encouragement pair's feet reach the top of the bottom third |
| 10 Calm camera, never frozen | yes | eased camera keys, slow drift |
| 11 No other logos or watermarks; no realistic faces | yes | only the campaign logo |

## Process

| Rule | Yes/No | Where |
|---|---|---|
| Render only in this cloud session; no Render workflow, no paid service | yes | export.py run here |
| No song audio, lyrics, videos or frames in git | yes | work/ and out/ are ignored |
| No em dash or en dash | yes | checked in code and docs |
| Branch backdrop2/s09-full from the approved tag; code tools/s09_full2, docs project-docs/backdrops/s09-full2 | yes | git |
| Native 60 fps, 1920x1080 | yes | render check |

## Render checks (after the render)

After fix 1 (2026-11-19): all three files have 17,460 frames, 291.0 s, 0 black frames, the signature on every frame after the opening, and sync 0 ms at all three hit points. Stage and review each have one near-repeated frame pair at 3:38.27 (mean change 0.018 of 255 against the 0.02 limit; invisible; accepted by the coordinator), so verify.py reports ok false. The phone copy has 38 near-repeats from its bitrate limit. Before fix 1: Stage and review files pass every check (17,460 frames, 291.0 s, 0 black, 0 repeated, signature on every frame after the opening, sync 0 ms at all three hit points). The phone copy has 33 near-repeated frames in the quietest interlude (bitrate limit); see STATUS.md for the file names, SHA-256, length, frame counts, black, frozen and repeated frame checks, signature presence and the sync check at 0:59.5, 2:28.8 and 4:02.
