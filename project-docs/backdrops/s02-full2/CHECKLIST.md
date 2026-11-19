# 02 The Rose: backdrop version 2, checklist

Every rule of the version 2 brief (2026-11-18), answered yes or no, with where it was checked. "Stills" are the landmark stills at full and quarter size (contact sheet "02 backdrop v2 stills.jpg"); "video" is the final stage file and its checks (export.py --check). Final results after the full render are in the last section.

## Drive versus this brief

The Drive rule files (read in this session, last changed 2026-11-14 to 2026-11-17) are older than the brief, which carries Anthony's 2026-11-18 decisions, so the brief was followed where they differ: 60 fps (DESIGN-SYSTEM 4 still says 30 fps), live length plus a 15 s hold (DESIGN-SYSTEM 9 says a hold "as long as needed"), the opening and signature wording (DESIGN-SYSTEM 7 says title about 5 s), comets in song 01 only (no Drive file says so), the website colours (DESIGN-SYSTEM 5 still lists the pastel ones). From the newer handbook: "Only warm gold glitter people", so no crystal people were used.

## The message, look and length

| Rule | Yes/No | Where checked |
|---|---|---|
| Every scene serves the message (the Words of Mother's Love bring peace): the spoken Encouragement wakes the seed and brings the spring | yes | design 1 and 10; TIMELINE |
| Majestic, warm, heavenly; never dark, cold, empty or eerie | yes, with a note | stills: nights lifted to silver blue with warm lights; the lonely night is the darkest part, deep starry blue, never black |
| Music part exactly the live length 4:00 (240.0 s) plus a 15 s calm hold, total 255.0 s | yes | export.py TOTAL, video check |
| Reference measured; mapped section by section; marked as an estimate | yes | TIMELINE "Length and the time map" and "Measurements" |
| CUES.md with every section start, what is on screen, and its calm moment | yes | CUES.md |
| The song's own look (winter night, snow, frost, pale pink dawn; silver blue, white, blush pink; no rain; close and quiet, horizon mid) | yes | stills |
| Signature effects are this song's own; no comets (song 01 only) | yes | rose.py (Comets class removed); stills |
| Craft kept from Revision 3: cream Cormorant phrases with a coloured capsule label, smooth eased motion, no grain | yes | stills 2:35 and 4:06 |

## Expressions and the arch

| Rule | Yes/No | Where checked |
|---|---|---|
| Exact wording from words.EXPRESSIONS, "(or root)" kept | yes | rose.py uses expr="Encouragement" (words.py at the tag); stills |
| Website colour (Encouragement #9E6AF6) | yes | words.COLORS |
| Only where a lyric line is that act (design: verse 3, the singers tell the lonely one to remember) | yes, placed by measured form | TIMELINE; noted as an estimate (not placed by ear) |
| Readable 8 to 10 s with nothing competing in its box | yes: 10.0 s and 8.4 s | WT in rose.py; stills; blossoms, hearts, snow and candles fade out of word boxes (_clear) |
| Upper middle, block centred about a third of the way down; people below | yes | stills (block centre about 0.36 of the height) |
| Words collapse into the star in the arch | yes | leave="rise" into star 7 |
| Star history: start 9 and 7; 02 relights 7 (brief flare, one new thin ring); end 9 and 7; nothing else lit | yes | arch_lit in rose.py; the hold's return of the words adds a soft glow only, no second ring |
| Only one expression reads at a time | yes | WT windows do not overlap |
| The people DO the expression while it reads | yes | ACTING plan in TIMELINE; still 2:35 |
| Symbol in the world, subtly, in its colour, never over the words | yes | praying hands as a violet constellation, top right, 2:16.8 to 2:45 |
| Hearts in the expression colour drift off the expression | yes | Hearts class: from the words as they rise, then from the women |

## People

| Rule | Yes/No | Where checked |
|---|---|---|
| Radiant, whole, gold glitter, clothed in garments of light; no dark, ash, shattering or glowing eyes | yes | stills; nobody dissolves into sparks (they fade whole) |
| Fewer people, more light | yes | a young woman (verse 2), the traveler and three women (verse 3) only |
| Touching only between two people of the same gender | yes | all women |
| Refined natural movement, no stiff poses | partly | the engine's acting and gestures; the people are soft and small at backdrop distance (weak point) |
| Heavenly Mother only from behind or as hands of light | yes | she is not shown as a figure |

## Words on screen

| Rule | Yes/No | Where checked |
|---|---|---|
| Opening readable from frame 0, held at least 7 s: logo, HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (italic), song title large; on calm sky | yes | stills 0:00 and 0:07; whole 0:00 to 0:07.0, gone by 0:08.6; navy because song 01's morning sky is pale |
| Signature from the end of the opening to the last frame, top left: logo mark, song title, concert title, DEC 6 · 4:30 PM (brightest), HEALING CONCERT · LAS VEGAS | yes | render.py Lockups; on every frame from 0:09.6 to the end (fade in 8.0 to 9.6) |
| Signature never flashes | yes | one constant layer; during the pale dawn (3:03 to 3:59.5, set from the measured sky brightness behind it) the letters change colour to navy over 3 s and back to warm white over 3 s; navy is laid over the whole white layer, so the sky never shows through the letters |
| Nothing covers the signature; 40 px clear from any expression box | yes | particles fade in its corner (SIG_BOX); stills: about 50 px between it and the ENCOURAGEMENT capsule |
| Date line capitals at least about 22 px at 1080p | yes | Jost 500 at 32 px: capitals about 23 px |
| 3 to 6 short fragments with their own effects, never with an expression | yes, 3 | TIMELINE fragments |
| Warm white on night skies, navy on bright skies, nothing dark behind text | yes | "becomes the rose" in navy ink on the dawn; opening navy on the morning |
| End card: song 11 only | yes | none here; ends on the calm hold with the signature |

## Never

| Rule | Yes/No | Where checked |
|---|---|---|
| 1 No white-outs | yes | brightest moment 3:40 (dawn): the scene stays visible; video check (no frame near full white) |
| 2 No white text on pale skies | yes | see words |
| 3 Nothing crossing a reading box or the signature | yes | _clear, SIG_BOX, the rose moved to the left of the words |
| 4 One expression at a time | yes | |
| 5 No garbled letters while words form or leave | yes | motion strip |
| 6 No words mirrored in water | yes | every word reflect=False |
| 7 No dark, brown or mannequin people; big enough | partly | gold and bright; people are small at the back of a hall (weak point) |
| 8 No mushy blur, jitter, popping or sliding | yes | motion strip |
| 9 Bottom third calm | yes | Calm wrapper on snow, frost, candles, footprints, blossoms, dancer; camera reframed so the seed and the rose sit above it |
| 10 Calm camera, never frozen | yes | slow keyed camera, gentle drift |
| 11 Only the campaign logo; no realistic faces | yes | |

## Technical

| Rule | Yes/No | Where checked |
|---|---|---|
| Rendered only in this cloud session; no Render workflow; nothing paid | yes | export.py, 4 local processes |
| Native 60 fps, 1920x1080 | yes | video check |
| No song audio, lyrics, videos or frames in git | yes | git status; media outside the repository |
| No em dash or en dash anywhere | yes | grep of the branch |
