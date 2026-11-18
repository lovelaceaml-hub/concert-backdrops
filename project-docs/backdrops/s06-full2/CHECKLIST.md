# Song 06 backdrop v2: checklist

Every rule of the v2 brief, yes or no, and where it was checked. "Stills" = landmark stills at full size and at one third size (the back of the hall); "strips" = motion strips at 12 frames a second through every word arrival and departure, the opening and the people's entrances and exits; "overlap" = `work/s06_full2/overlap.py`, which projects every person's head and feet against the word boxes every 0.5 s; "verify" = `tools/s06_full2/verify.py` on the finished files.

## Rules read
| Rule | OK | Where checked |
|---|---|---|
| Drive AGENTS.md, DESIGN-SYSTEM.md, VIDEO-HANDOFF.md, AUTONOMOUS-RUN.md, CONCERT-OVERVIEW.md, the 06 design, Status/06.md, PHASEB through Update 25 read | yes | read by a read-only helper; conflicts listed in the report and TIMELINE.md |
| Campaign pages read (about, checklist, expressions) | yes | Inclusiveness: forgiveness that embraces faults, respond gently, help them move forward; Concession: when impatient, take a breath and yield |

## The message and the bar
| Rule | OK | Where checked |
|---|---|---|
| Mother's words of love that bring peace are the centre; every scene serves them | yes | the two expressions are the two acted heart scenes; the rest is the grain, the field and the light they grow |
| Majestic, warm, heavenly; never dark, cold, empty, eerie or decaying | yes | stills: harvest evening throughout, darkest moment a warm ember dusk |

## Length and timing
| Rule | OK | Where checked |
|---|---|---|
| Music part exactly the live length 137.0 s, then a 15 s calm hold; total 152.0 s | yes | render.py clock map; prepare.py score 152.000 s; verify (frames 9120) |
| Reference measured; conformed section by section (differs by 2.15 s); stated as an estimate | yes | TIMELINE.md "Live-length mapping" |
| CUES.md with every section start, what is on screen, the calm moment that ends it | yes | CUES.md |
| Hold gently alive, never black | yes | stills 140 and 151.98 s; verify blackdetect |

## Look
| Rule | OK | Where checked |
|---|---|---|
| Song 06 look: harvest evening, amber, wheat gold, deep orange, golden dust, long low sun, rays, wide, warm, horizon low | yes | stills |
| No comets | yes | the base song has none (grep); stills |
| Signature effects of this song (the warmed grain, roots, the field of wheat, windows of the plain, living water in the cracks, the fragrance wind, the last grain) not reused from other songs | yes | design section 8 and 11a; first-run effects re-used only from this song |
| Revision 3 craft: cream Cormorant words with coloured capsule labels, gold glitter people, warm, smooth eased motion, no grain | yes | stills, strips |

## Expressions and the arch
| Rule | OK | Where checked |
|---|---|---|
| Exact wording from words.EXPRESSIONS; website colours (#62B2FA, #5ABA5A) | yes | the words come from the approved words module (Claude Final v1), colours checked in its source |
| Only where the lyric line is the act (Concession: provisional exception 12a, noted) | yes | TIMELINE.md |
| Readable 8 to 10 s with nothing competing | yes | Concession 8.6 s, Inclusiveness 9.7 s; every light dimmed inside the reading box (Calm), the arch too (Clear); overlap: no head inside a box |
| Upper middle, block centred about a third of the way down; people below | yes | stills; overlap: heads at 0.48 to 0.50 of the height, box bottom at 0.41 |
| Words collapse into their star | yes | letters fade whole and one spark of the colour flies to the star (strips 82.0 to 83.2 and 94.4 to 95.6) |
| Star history: start 3, 4, 6, 7, 8, 9; 5 lights; 4 relights (flare and one new ring); end 3 to 9 | yes | song module _arch_lit; stills 140 s |
| Acted: Concession stepping aside with an open palm (two men); Inclusiveness an embrace of two women | yes | stills 77.6, 86.4, 92.0 s; TIMELINE.md acting plan |
| Symbols in the world, subtle, in the colour, near the moment, never over the words | yes | Concession: embers flock over the wheat to the right (75.8 to 78.9); Inclusiveness: petals settle beside the women (87.0 to 93.6) |
| Hearts in the expression colours drift off each expression | yes | hearts drawn as heart outlines of sparks (the pinned engine has no heart particle); Concession's end before Inclusiveness forms |
| Only one expression reads at a time | yes | strips 81.2 to 84.0 |

## People
| Rule | OK | Where checked |
|---|---|---|
| Only warm gold glitter people (whole, radiant, clothed); never shattering, ash, dark, glowing eyes | yes | stills; spark-forming entrances and the dissolve exits of the first run removed: people fade in and out gently |
| Fewer people, more light | yes | three small scenes; walkers far off in the refrains |
| Touch only between two people of the same gender, or a parent and child | yes | mother and child; two women; the two men do not touch |
| Refined, natural movement; soft faces, no realistic faces | yes | approved Revision 3 bodies and acting |
| Heavenly Mother not shown as a figure | yes | design: her love is the warmth of the horizon star |
| Big enough to read from the back of the hall | partly | standing people are about 16 percent of the picture height, to keep them clear of the words and the bottom third; readable at one third size, smaller than the first run |

## Words on screen
| Rule | OK | Where checked |
|---|---|---|
| Opening readable from frame 0, held at least 7 s: logo, HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (italic), song title large, on calm sky | yes | stills 0 and 7.0 s, strips 7.0 to 9.4 s: whole to about 8.2 s |
| Signature top left from the end of the opening to the last frame: logo mark, song title, concert title, DEC 6 · 4:30 PM (brightest, capitals about 24 px), HEALING CONCERT · LAS VEGAS; never flashes | yes | stills; verify (letter pixels in the corner on every frame from 8.6 s) |
| 40 px clear between the signature and any expression box | yes | signature ends about 176 px from the top; the expression boxes start about 240 px from the top (gap about 64 px) |
| 3 to 6 short lyric fragments, never with an expression, never the full lyrics | yes | five fragments of 3 or 4 words; none overlaps an expression |
| Each fragment has its own special effect from the song's imagery | partly | each appears inside its own scene effect (the sinking grain, the shared loaf, the lighting windows, the filling cracks, the fragrance wind), but the letters themselves now arrive and leave in the one clean style, because the first run's letter effects broke letters apart (never-rule 5) |
| Warm white text on the evening skies; nothing dark behind text | yes | stills; the opening veil is a faint warm shade, not dark |
| No end card (song 11 only) | yes | |

## Never
| Rule | OK | Where checked |
|---|---|---|
| 1 No white-outs | yes | brightest stills: mean 125 to 148 of 255, 0.1 percent of pixels above 245 |
| 2 No white text on pale skies | yes | frame 0: the camera tilts up so the title is on the blue sky, the sun below it |
| 3 Nothing crossing a reading box or the signature | yes | overlap; Calm; strips |
| 4 Only one expression at a time | yes | strips |
| 5 No garbled letters while words form or leave | yes | strips: the approved clean leave restored |
| 6 No words mirrored in water | yes | words reflect=False |
| 7 No dark, brown or mannequin people | yes | stills |
| 8 No mushy blur, jitter, popping or sliding | yes | strips; the first run's per-frame random spring (jitter at 60 fps) replaced by smooth motion |
| 9 Bottom third calm | yes | every light fades below 0.37 of the height (Calm), no reflections of people or lanterns, the rings under the people removed; overlap: feet at 0.62 to 0.66 (one second at 0.68 as the young woman appears) |
| 10 Calmer camera, never frozen | yes | eased keys; verify freezedetect |
| 11 No other logos or watermarks, no realistic faces | yes | |

## Render and delivery (filled in after the render)
See the bottom of this file.
