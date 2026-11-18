# Song 03 backdrop v2: checklist

Every rule of the version 2 brief (quoting DESIGN-SYSTEM, PHASEB and the handbook), with yes or no and where it was checked. Written before the full render; the lines marked "after render" were filled in from tools/s03_full2/verify.py and the final frames.

## Hard limits

| Rule | Yes/No | Where checked |
|---|---|---|
| Rendered only inside this cloud session; no GitHub Render workflow; no paid service; nothing on the Mac | Yes | tools/s03_full2/export.py (4 local processes), people.py |
| No song audio, lyrics, videos or frames in git | Yes | git status; work/ and out/ are ignored; audio stays in work/ |
| Only the short fragments on screen; no lyrics copied into files | Yes | docs refer to lines by first words only, as the design does |
| No em dash or en dash anywhere | Yes | grep of every new file, commit messages and on-screen text |
| Nothing deleted in Drive; MP3s, Lyrics doc and Visual Plan doc not edited | Yes | Drive only read; one new file added to Status |
| Helpers: Haiku only | Yes | one Haiku agent read the Drive rule files |
| Branch backdrop2/s03-full from tag film10-revision3-approved-2026-11-16; code in tools/s03_full2/, docs in project-docs/backdrops/s03-full2/; no approved promo, engine or other songs' files edited; no git add -A | Yes | git diff --stat against the tag |

## The message and the bar

| Rule | Yes/No | Where checked |
|---|---|---|
| Mother's words of love that bring peace are the centre: two expressions acted, read 9.4 s each, then each collapses into its light; the stillness of the lake after each | Yes | TIMELINE.md; stills 30, 226 |
| Majestic, heavenly, warm; never dark, cold, empty, eerie or decaying | Mostly | the night section (0 to 95 s) is a deep indigo night lake with stars, aurora and the memory sky, as the song's look requires; it is darker than the dawn. Judged warm enough, but it is the darkest part of the song |

## Length and timing

| Rule | Yes/No | Where checked |
|---|---|---|
| Music part exactly the live length 5:13 (313.0 s), then a 15 s calm hold, never black: 328.0 s | Yes | verify.py: all three files 19,680 frames, 328.000 s, 60 fps |
| Reference measured; mapped to the live length (cut of one repeated passage, no tempo change, within 0.04 s); recorded as an estimate | Yes | prepare.py, TIMELINE.md |
| CUES.md with every section start, what is on screen and the calm moment that ends it | Yes | CUES.md |

## Look

| Rule | Yes/No | Where checked |
|---|---|---|
| Row 03: indigo night of memory, rain, then a rose dawn; indigo, rose, warm gold; rain, lanterns, aurora, petals; low over the water | Yes | stills; s03_full2.py palette and plates |
| Signature effects of this song only: the shattered memory sky mended into a gold-seamed moon, rain frozen into lanterns, aurora with Mother's cupped hands of light, words carved in gold, words revealed by melting frost, words gathered by petals | Yes | overlay2.py, s03_full2.py |
| No comets (song 01 only) | Yes | no comet anywhere; the words' sparks contract into their light as a gathering cloud (stills 39.4, 39.9, 235.4) |
| Revision 3 craft: cream Cormorant phrases with coloured capsule labels, upper middle; warm people; smooth eased motion; no grain | Yes | overlay2.py; stills |

## Expressions and arch

| Rule | Yes/No | Where checked |
|---|---|---|
| Exact wording of words.EXPRESSIONS (tag), "(or root)" kept; website colours #F6CE46 and #9E6AF6 | Yes | overlay2.py APOLOGY, ENCOURAGEMENT |
| Only where the lyric line is that exact act (design section 7) | Yes | Apology at "Mother, to save my life, She ignored all of Her pain"; Encouragement at "Putting Her hands together, earnestly She prayed" |
| Readable 8 to 10 s with nothing competing: 9.4 s each; the scene behind softened; no text, person, burst or particle in the box | Yes | stills 30, 34, 226, 230: people's heads about 45 px below the box; symbols outside it; hearts only after the words leave |
| Block centred about a third down (0.335), people below | Yes | stills |
| Words collapse into the expression's star | Yes | stills 39.4 to 40.4, 235.4 to 236.9 |
| Star history: starts 7 and 9; lights 3; relights 7 (flare and one new thin ring); ends 3, 7, 9; nothing else lit | Yes | s03_full2.py PHRASES, RINGS_AT_START; stills 44, 237.2, 327.98 |
| Acted while it reads (PHASEB 6) | Yes | ACTING.md; Apology: a hand laid gently on the back of one sitting with head bowed; Encouragement: a hand on the shoulder of one kneeling in prayer |
| Symbols in the world, subtle, in the expression's colour, never over the words; hearts in the colour drift off | Yes (fix 1) | the symbols are faint constellations traced by one spark (stars of the colour joined by hair-thin lines), no longer line drawings that read as icons; overlay2.py _symbol, _symbol_draw, _hearts_draw; stills 32, 36, 229, 233 |

## People

| Rule | Yes/No | Where checked |
|---|---|---|
| Only warm gold glitter people, whole, clothed in light; never shattering, dark, or with glowing eyes | Yes | people stills; they gather from light and fade as light |
| Fewer people, more light | Yes | two pairs in the whole song (about 15 s each) and Mother's hands of light |
| Every touching moment between two people of the same gender | Yes | both pairs are two women |
| Refined natural motion, no stray limbs | Yes | acting.py motion; both kneel on both knees so no leg stands clear of a gown (an earlier still showed a shin apart from the gown; fixed) |
| Heavenly Mother only from behind or as hands of light | Yes | cupped hands only (204.5 to 212.5) |

## Words on screen

| Rule | Yes/No | Where checked |
|---|---|---|
| Opening readable from frame 0, at least 7 s (whole to 8.6 s): logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), the song title large; calm sky behind | Yes | stills 0, 5 |
| Signature top left from the end of the opening to the last frame: logo mark, song title, The Words of Mother's Love That Bring Peace, DEC 6 · 4:30 PM (brightest), HEALING CONCERT · LAS VEGAS; never flashes | Yes | stills 12 to 327.98; verify.py: present at every whole second from 12 s |
| Nothing covers the signature; 40 px clear of any expression box | Yes | about 65 px from the signature's last line to the Apology label |
| Date capitals at least about 22 px at 1080p | Yes | measured 22 px |
| 3 to 6 short lyric fragments, each with its own effect, never with an expression | Yes | three (the design's): 116 to 127.5, 199 to 211, 292.3 to 315.5 |
| Warm white and gold on night skies; navy with a soft white glow on bright skies; nothing dark behind text | Yes | the signature turns navy over the sunrise; "I love You Mother" navy on the dawn |
| No end card (song 11 only); ends on the calm hold with the signature | Yes | still 327.98 |

## Never

| Rule | Yes/No | Where checked |
|---|---|---|
| 1 No white-outs | Yes | soft highlight shoulder on every frame; brightest pixel 251 of 255 |
| 2 No white text on pale skies | Yes | navy on the dawn |
| 3 Nothing crossing a reading box or the signature | Yes | protection behind text; stills |
| 4 One expression at a time | Yes | 26.8 to 40.6 and 222.6 to 237.0 only |
| 5 No garbled letters while forming or leaving | Yes | written by a clean pen reveal; they fade cleanly while sparks rise from them (an earlier version looked doubled; fixed) |
| 6 No words mirrored in water | Yes | all words are drawn after the engine's water |
| 7 No dark, brown, solid or mannequin people; big enough for the back of the hall | Partly | radiant gold glitter; about 0.2 of the frame high, smaller than ideal so the words keep their clear box (noted as a weak point) |
| 8 No mushy blur, jitter, popping or sliding | Yes | motion strips at 12 frames a second from the final render through the opening, both expressions and all fragments; no identical consecutive frames |
| 9 Bottom third calm | Yes (fix 1) | no engine rings; a smooth highlight press below the far shore on every frame; under the mended moon (1:34 to 2:58) the rings painted on the plate's water are stilled below two thirds of the frame (stills 121, 150); people's feet on the shore line |
| 10 Calm camera, never frozen | Yes | slow plate pushes; longest near-still stretch 0.02 s |
| 11 No other logos or watermarks; no realistic faces | Yes | only the campaign logo; smooth artistic heads |

## Delivery (after render)

All three files made, checked and attached; no black frames; music in sync at three hits (0.0 ms). See STATUS.md for the files and SHA-256.

Result: every rule yes, except two partial: the night section is the darkest part of the song (as its look asks), and the people are about 0.2 of the frame high (smaller than ideal, to keep the words' box clear).
