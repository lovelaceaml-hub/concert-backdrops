# Song 04 backdrop v2: checklist

Every rule of the version 2 brief (2026-11-18), answered yes or no, with where it was checked. "Stills" means the landmark stills rendered in this session (`work/s04v2/st*`, contact sheet "04 backdrop v2 stills.jpg", after fix 1 "04 backdrop v2 stills fix1.jpg"); "checks" means `work/s04v2/out/checks.txt` from `tools/s04_full2/export.py` on the final files.

## Length, timing, format

| Rule | Yes/No | Where checked |
|---|---|---|
| Music part exactly the live length, 220.0 s (3:40) | yes | song04.py MUSIC_END; the reference (219.435 s) conformed with atempo 0.997430 to 220.0 s (prepare.sh) |
| 15 s calm hold after the music, gently alive, never black | yes | song04.py HOLD; stills at 228 s; checks (darkest frame) |
| Total 235.0 s = 14,100 frames, native 60 fps, 1920x1080 | yes | checks (frame count, rate, size) |
| Reference measured here (analyze.py, loudness, hits, repeats) and mapped to the live length | yes | TIMELINE.md "The music" |
| CUES.md with section starts, what is on screen and the calm moment that ends each | yes | CUES.md |
| Rendered only in this cloud session; no Render workflow, no paid service, nothing on the Mac | yes | work/s04v2/run_parts.sh (16 parts on this machine's 4 cores) |

## The message, the look

| Rule | Yes/No | Where checked |
|---|---|---|
| The mother's words of love that bring peace carry the video (Apology and Inclusiveness acted and read; the thaw grows from them and from Mother's warmth) | yes | TIMELINE.md story; stills 34, 62, 85 |
| Heavenly, warm, never dark, cold, empty or eerie | yes | stills: a pale pearl morning that thaws into apricot and rose gold; no dark frame (checks) |
| This song's look (DESIGN-SYSTEM 6): frozen pale winter morning thawing into apricot; ice blue, pearl, apricot; low cold sun, haze, then warm rays; horizon high, more lake | yes | song04.py LOOKS frost, warm, glory, hold; stills 4 to 228 |
| No comets (song 01 only) | yes | song04.py has no comet set (removed from the first run) |
| Signature effects of this song only (ice and thaw, melted footprints, the line that turns gold, warm beam, heart flower, golden breath, freed petals) | yes | song04.py classes; the lake and arch are the shared motifs |
| From Revision 3: the word style, people quality, warmth, smooth eased motion, no grain | yes | cards04.py (Cormorant italic phrase, coloured capsule label); people.py (Claude Final v1 bodies, glitter look) |

## Expressions and the arch

| Rule | Yes/No | Where checked |
|---|---|---|
| Exact words.EXPRESSIONS wording, never retyped | yes | song04.py _expr_spec reads PW.EXPRESSIONS |
| Website colours (Apology #F6CE46, Inclusiveness #5ABA5A) | yes | same; capsule fill |
| Only where the lyric is that exact act: Apology at "I'm sorry ... forgive me" (27.4), Inclusiveness at "came to me first to embrace me" (59.3) | yes | TIMELINE.md lyric moments (word level transcript) |
| Gratitude's words never appear (star 2 is first lit in song 08); "I thank you" acted only | yes | TEXTS has no Gratitude; PHRASES star 2 never lit |
| Respect not placed here (stays in song 05) | yes | TEXTS |
| Each expression readable 8 to 10 s: Apology 9.6 s, Inclusiveness 9.0 s | yes | song04.py T |
| Nothing competing inside a reading box (no text, person, burst or particle) | yes | Clear() dims every particle set inside the boxes; people stay below the box (stills 34, 62); one text at a time |
| Upper middle, block centred about a third of the way down, people below | yes | TEXTS y = 0.69 from the bottom (31 percent down); stills |
| Words collapse into their star | yes | cards04.TextFX: sparks fly to STAR_POS[2] and [3] |
| Star history: start 3, 7, 9; relight 3 (flare and one new thin ring); light 4; end 3, 4, 7, 9; no other star | yes | song04.py PHRASES and RINGS_AT_START; engine/arch.py; stills 34 and 85 |
| The person or people do the expression while it reads | yes | people.py: Apology open hands low with a bow; Inclusiveness an embrace of two women |
| Symbols in the world, subtle, in the expression colour, never over the words | yes | song04.py symbol sets (Constellation for Apology, PetalShape for Inclusiveness) wrapped in Clear |
| Hearts in the expression colours drift off each expression | yes | song04.py HeartDrift |

## People

| Rule | Yes/No | Where checked |
|---|---|---|
| Only warm gold glitter (or crystal) people, radiant and whole, clothed in garments of light, soft faces | yes | people.py LOOK glitter, dress garments; stills |
| Fewer people, more light | yes | two sisters through verse 1 and chorus 1; ten people only in the last part |
| Every touch between two people of the same gender, or a parent with a child | yes | sisters (two women); a mother and a father each holding a child's hand; nobody else touches |
| Refined, natural, eased movement | yes | Claude Final v1 gestures with ease; motion strip review |
| Heavenly Mother only as light (the low sun and the golden breath) | yes | no figure |

## Words on screen

| Rule | Yes/No | Where checked |
|---|---|---|
| Opening readable from frame 0, held at least 7 s: logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), song title large | yes | cards04.py; whole 0.0 to 8.4 s; first frame |
| On calm sky, nothing busy behind | yes | the opening camera looks up so the lockup sits on the pale sky; still at 4 s |
| Signature from the end of the opening to the last frame, top left: logo mark, song title, concert title, DEC 6 · 4:30 PM (strongest), HEALING CONCERT · LAS VEGAS; never flashes | yes | cards04.py; checks (signature deviation per frame) |
| Date capitals at least about 22 px at 1080p | yes | Jost 600 at 34 px: capitals about 24 px |
| 40 px clear between the signature and any expression box; nothing covers the signature | yes | signature ends about 182 px from the top; the highest expression box starts about 222 px down; Clear() dims particles near the signature |
| 3 to 6 short fragments, each with its own effect, never with an expression | yes | 4 fragments (TIMELINE.md); gaps checked in T |
| Navy with a soft white glow on bright skies; nothing dark behind text | yes | all text navy #1f2a6b with white glow; the sky is pale throughout |
| No end card (song 11 only); ends on the calm hold with the signature | yes | |

## Never

| Rule | Yes/No | Where checked |
|---|---|---|
| 1. No white-outs | yes | checks: no frame with mean above 235 |
| 2. No white text on pale skies | yes | all text navy |
| 3. Nothing crossing a reading box or the signature | yes | fix 1: the dividing line / gold path, footprints and the closing light also pass Clear() (box padding 0.05); the verse 1 camera sits the sisters lower, below the words; fix 1 stills |
| 4. One expression at a time | yes | T |
| 5. No garbled letters while forming or leaving | yes | the letters are crisp pictures that reveal and dissolve with a soft front; motion strip |
| 6. No words mirrored in water | yes | text is drawn over the finished picture, never reflected |
| 7. No dark, brown, solid or mannequin people; big enough for the back of a hall | yes | stills (about a quarter of the picture height in verse 1) |
| 8. No mushy blur, jitter, popping or sliding | yes | motion strip; eased camera keys (Catmull-Rom) |
| 9. Bottom third calm | yes | fix 1: every particle set, including the world's dust, floats and lanterns, passes Clear(): nothing below 0.34 of the height, full only from 0.40; no reflections of particles; the near water mirrors little of the sun's glow; people kept in the middle band; fix 1 stills |
| 10. Calm but never frozen camera | yes | camera always moving slowly; checks (frozen stretches) |
| 11. No other logos or watermarks; no realistic faces | yes | |

## Records and delivery

| Rule | Yes/No | Where checked |
|---|---|---|
| No song audio, lyrics, videos or frames in git | yes | `git show --stat`; .gitignore covers work/ and media |
| No em or en dashes | yes | grep over the branch's files |
| Branch backdrop2/s04-full from the approved tag; code in tools/s04_full2, docs here; no approved promo, engine or other songs' files edited | yes | `git diff --stat film10-revision3-approved-2026-11-16` |
| Three files, SHA-256, STATUS.md, draft PR | yes | STATUS.md (files, hashes, checks) |

## Result

Every line above is yes. Checked again on the fix 1 files 2026-11-19 (export.py): 14,100 frames at 60 fps, 235.000 s, no black, white, repeated or frozen frames, the signature on every frame after 0:11, music in sync at three hits.
