# Song 08 backdrop version 2: checklist (written before the full render)

Every rule of the coordinator's version 2 brief (which quotes DESIGN-SYSTEM, PHASEB, VIDEO-HANDOFF and AUTONOMOUS-RUN), with yes or no and where it was checked. Stills: half size at 22 landmarks and full size at 8 acting and finale moments (`out/s08_full2/`, not committed); measurements by `tools/s08_full2/check.py` and the word box script recorded below.

## The message and the bar

| Rule | Yes/No | Where checked |
|---|---|---|
| The mother's words of love that bring peace are the centre; every scene serves them | yes | the two expressions are the two acted, still, held moments; everything else leads to them or follows from them (TIMELINE) |
| Majestic, heavenly, warm; never dark, cold, empty, eerie or decaying | yes | stills at every landmark: royal purple and gold night, gold column, rose ribbons, gold Gratitude, embroidered dawn, golden hold |

## Length and timing

| Rule | Yes/No | Where checked |
|---|---|---|
| Music part exactly the live length 210.0 s, then a 15 s calm hold (225.0 s) | yes | `TOTAL = 225.0`, `LIVE = 210.0`; check.py on the files |
| Reference measured; within 1 s of live, used as is | yes | 209.08 s decoded, 20 ms RMS and attack search, `engine/analyze.py`; TIMELINE |
| CUES.md with every section start, what is on screen and the calm moment | yes | CUES.md (13 cues) |
| 60 fps, 1920x1080 | yes | render.py `FPS = 60`; check.py |

## Look of this song

| Rule | Yes/No | Where checked |
|---|---|---|
| Royal festival night: deep royal purple, crimson, gold; gold aurora like embroidery, rays, sparkle; grand, symmetrical | yes | LOOKS in s08_full2.py; stills 0:44, 1:04, 2:55, 3:23 |
| Own signature effects (gold seam and column, Embroidered Sky, curtain gate), none reused from another song | yes | s08_full2.py Seam, GoldColumn, Linen, HeavenLight |
| No comets | yes | the Comets class and its set removed; the scene list has no comets |
| Revision 3 craft kept: cream serif phrases with capsule labels, warm people, eased motion, no grain | yes | Claude Final v1 words (f43f451); motion strip |

## Expressions and the arch

| Rule | Yes/No | Where checked |
|---|---|---|
| Exact wording from words.EXPRESSIONS, website colours | yes | `expr="Compliment"`, `expr="Gratitude"` take the wording and colour from the module |
| Only where a line is that exact act | yes | Compliment on the prince and princess lines, Gratitude on the thanksgiving line (design section 5) |
| Readable 8 to 10 s with nothing competing | yes | 9.8 s each; `Clear` dims every light set inside the box; stills 1:02, 1:04.5, 1:06.5, 1:31, 1:33.5 |
| Upper middle, block centred about a third down, people below | yes | box centres 0.398 and 0.401 of the height; people below and to the sides (word box script) |
| Words collapse into their star | yes | `leave="arch"` to star 9 and star 2; motion strip 1:09 to 1:12 and 1:36.5 to 1:39.5 |
| Star history: 08 relights 9, lights 2; all nine lit at the end; no other star | yes | `_arch_lit`; stills 0:00 (2 dark), 1:40 and 3:45 (all nine) |
| A relight is a brief flare and one new thin ring | yes | `_arch_lit` flare on star 9 at 1:10.8 |
| The people do the expression (PHASEB 6 table) | yes | Compliment: applause and a hand on the heart; Gratitude: a hand on the heart and a bow, the congregation bowing (full size stills) |
| Symbols in the world, subtly, in the expression's colour, never an icon over the words | yes | clapping hands constellation in the right sky, bowing person traced by fireflies in the left sky, both outside the reading boxes |
| Hearts drift off each expression in its colour | yes | Hearts sets (Compliment #364E96, Gratitude #F2B25E) |
| Gratitude includes thanks to Father and Mother | yes | everyone bows toward the warm star at the horizon; Mother's answer flows back |

## People

| Rule | Yes/No | Where checked |
|---|---|---|
| Only warm gold glitter or crystal people, radiant and whole, clothed in light | yes | Body look "glitter", robes; full size stills |
| Fewer people, more light | yes | the pair, one congregation moment, Mother once; light carries the rest |
| Touching only between two people of the same gender (or parent and child) | yes | no touching at all (the pair bows and applauds) |
| Refined natural motion, no stiff or random poses | yes | eased gestures, motion strip |
| Heavenly Mother only from behind | yes | `facing=180.0` (away from the camera, actor convention 0 faces +z) |
| Big enough to read from the back of the hall | yes | about 30 percent of the frame height in the Compliment and the meeting (stills 0:48, 1:04, 1:18) |

## Words on screen

| Rule | Yes/No | Where checked |
|---|---|---|
| Opening: logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), song title large, from frame 0, at least 7 s, on calm sky | yes | lockup.py; readable 0:00 to 0:07.8; still 0:00 (the seam opens only from 0:08) |
| Signature top left from the end of the opening to the last frame: logo mark, song title, concert title, DEC 6 · 4:30 PM (brightest), HEALING CONCERT · LAS VEGAS | yes | lockup.py; window 8.4 s to the end, one fade in, no flashing; check.py samples it 4 times a second |
| Date line capitals at least about 22 px at 1080p | yes | Jost 500 at 33 px: capitals 23 px |
| Nothing covers the signature; 40 px between it and any expression box | yes | signature block bottom 206 px; Compliment box top 284 px, Gratitude 347 px; `Clear` keeps light sets out of the signature corner |
| Lyric fragments: 3 to 6, short, each with its own effect, never with an expression, never full lyrics | yes | three fragments, 3 to 4 words, gold rain, pen, stitch |
| Warm white with gold on night skies, navy on bright skies; nothing dark behind text | yes | all skies here are night or dusk; "the glory of Zion" moved up onto the purple sky (still 3:23.5) |
| No end card (song 11 only); ends on the calm hold with the signature | yes | still 3:45 |

## Never

| Rule | Yes/No | Where checked |
|---|---|---|
| 1 No white-outs | yes | brightest sampled frame and the share above 245 (check.py) |
| 2 No white text on pale skies | yes | finale fragment moved up; sun and flood softened; fix 1: the seam waits for the chord and the gate stays faint until "the glory of Zion" has gone, so no pale glow sits above and below it |
| 3 Nothing crossing an expression box or the signature | yes | `Clear` on every song light set; people kept below and to the sides; fix 1: the gold column of the Gratitude waits until the words are in star 2 (1:38.2 to 1:43) |
| 4 One expression at a time | yes | WT times |
| 5 No garbled letters while words form or leave | yes | motion strip |
| 6 No words mirrored in water | yes | `reflect=False` on every word |
| 7 No dark, brown, solid or mannequin people | yes | glitter bodies |
| 8 No mushy blur, jitter, popping or sliding | yes | the gold wave keeps out of the lens (fixed at 1:40); motion strip |
| 9 Bottom third calm | yes | lights, rings and gold dimmed below 0.37 of the height; no arch or star field mirrored; fix 1: no people or congregation mirrored in the lake; softer mirror; check.py bottom third numbers |
| 10 Calm camera, never frozen | yes | eased keys, still only while words read; gentle drift elsewhere |
| 11 No other logos or watermarks, no realistic faces | yes | stills |

## Records and delivery

| Rule | Yes/No | Where checked |
|---|---|---|
| Branch backdrop2/s08-full from the approved tag; code in tools/s08_full2, docs in project-docs/backdrops/s08-full2 | yes | git |
| No audio, lyrics, videos or frames in git; no em or en dash | yes | git status; dash scan of every new file |
| Render only in this cloud session; no Render workflow, no paid service | yes | four local processes |
| Three files: stage (silent, CRF 16), review (music, AAC 320k, CRF 20), phone (720p60, under 25 MB) | yes | fix 1 files: each 225.000 s, 13500 frames, 60 fps; stage 172.2 MB silent, review 102.2 MB AAC, phone 23.5 MB; no black, frozen or repeated frames; share above 245 at most 1.5 percent; signature on every sampled frame after 0:09; hits at 43.20, 109.16, 202.28 s heard on the frame (check.py) |
