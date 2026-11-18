# Song 04, I'm Sorry, Please Forgive Me: full backdrop timeline

Concert item 5, Sunday, December 6. Design: `project-docs/designs/04 I'm Sorry, Please Forgive Me.md` ("The Thaw"), in the approved Revision 3 look. Code: `tools/s04_full/` (song04.py world, camera, words and effects; people.py the people of light; render.py the loader; export.py joining and checks).

## The reference audio

- The church's upload youtu.be/43seZJ9fTgw, stored as `s04.mp3` on Anthony's private Artifact page (SHA-256 a1fa529d6f6dd5f477a429f7c8587c017ed94efebabe669fa8e05e1dd32e7220). Never committed.
- Length 219.43 s (3:39.4). Measured here with `engine/analyze.py` (features for the render) and a half-second loudness pass. Engine tempo estimate 123 (the pulse feels about 80, a gentle ballad).
- The organisers say the live performance is a slight variation, choir only, a cappella, so the live length may differ. The video is built to this reference.
- Video length: 7033 frames at 30 fps = 234.43 s: the music, then 15 s of calm hold (gently alive, never black).

## Measured sections (loudness, dB below the loudest moment)

| Time | Section | Loudness |
|---|---|---|
| 0:00 to 0:31 | opening, soft (quiet dips 0:01 to 0:08, 0:19 to 0:21, 0:29.5 to 0:32) | about -15 |
| 0:31 to 1:15 | verse 1, soft; lifts from 1:05; hit 0:43.5 | -15 to -9 |
| 1:15 to 1:42 | chorus 1, full; loudest 1:25 (hit 1:23.9) | -8 to 0 |
| 1:42 to 1:45 | the drop: the music breathes | -15 to -17 |
| 1:45 to 2:25.5 | verse 2, soft; lifts 2:14 to 2:20 | -14 to -9 |
| 2:25.5 to 3:35.5 | final chorus, full and long; peaks 2:42, 2:52 to 2:54, 3:06 to 3:09, 3:17 | -8 to -1 |
| 3:35.5 to 3:39.4 | the last chord dies away | -12 to -56 |

These agree with the coordinator's measurements and with the design's studio measurements (the studio take is 2 s longer; its big sections start within a second of these).

## The picture on the music

| Song time | Music | Picture |
|---|---|---|
| 0:00 to 0:16 | opening | a frosted pearl and rose morning lake, low sun at the left in haze, frost glitter on the far ice, a thin line of light dividing the ice; nine comets drift slowly high in the sky |
| 0:03.5 to 0:12.6 | opening | the title "I'm Sorry, Please Forgive Me" (readable 0:04.6 to 0:11) |
| 0:13 | | the small signature fades in, bottom left, and stays to the end |
| 0:16 | | two sisters of gold light form, one on each side of the line, half turned from each other |
| 0:31 | verse 1 begins | the first sister turns, sees her sister, lays a hand on her heart |
| **0:39.8 to 0:51.2** | verse 1, the apology line | **APOLOGY**, read 0:40.8 to 0:50.4 (9.6 s): she offers both open hands toward her sister; nothing else moves |
| 0:51.8 to 0:55.6 | | she crosses first; a warm pool glows under each step |
| 0:56.4 to 0:61 | | her hand offered; her sister turns and takes it |
| 1:01 to 1:15 | building | she kneels and bows; her sister lays a hand on her head; the line in the ice fills with gold from the middle out |
| 1:15 | chorus 1 | she is helped up; the two turn side by side toward the low sun and hold hands; the sky warms |
| 1:20 to 1:32 | loudest 1:25 | the golden breath of Heavenly Mother's love (light only, never a figure) rolls across the ice from the sun and gathers round them as a glittering mist; the ice melts in a wide circle; a gold path runs from them toward the sun |
| 1:32 to 1:41 | | the breath rises and thins |
| 1:42.2 | the drop | the sisters dissolve into sparks; the picture cools a little (the hurt sister's memory); the camera glides round to the other shore |
| 1:44 to 1:46 | verse 2 | the sisters form again, seen from the hurt sister's side |
| **1:45.2 to 1:55.8** | verse 2, "I thank you" | **GRATITUDE**, read 1:46.2 to 1:55 (8.8 s): the hurt sister lays a hand on her heart while her sister waits across the ice |
| 1:54 to 1:57.4 | | the first sister walks across to her, warm footprints toward us |
| **1:57 to 2:08** | verse 2, the embrace | the embrace; **INCLUSIVENESS**, read 1:58 to 2:07.2 (9.2 s) while they hold each other; rose light warms the hurt sister |
| 2:08 to 2:25 | verse 2 continues, lifting | they keep holding each other, swaying very slightly; the warmth returns |
| 2:25.5 | final chorus | a soft bloom: the two stand side by side hand in hand on the gold path facing the sun |
| 2:26 to 2:42 | | the whole lake thaws from the middle out; the line in the ice stays gold for good |
| 2:36 to 3:26 | | lanterns rise across the lake |
| 2:46 to 2:58 | | people of light gather out of sparks on the water round them: families, children, an older couple, friends; none touching (the owner's rule), gently swaying |
| 3:23 to 3:33 | | everyone dissolves into rising sparks, the sisters last |
| 3:33 to 3:39.4 | closing chord | one small warm light rests on the water where they stood, sending a gentle ring every few seconds |
| 3:39.4 to 3:54.4 | silence | calm warm hold: the still lake, the low sun, the gold path, the small light, slow comets |

The three expressions are in the order the organisers asked for (3 Apology, 2 Gratitude, 4 Inclusiveness), with the exact `words.EXPRESSIONS` wording and website colours (Apology #F6CE46, Gratitude #F2B25E, Inclusiveness #5ABA5A), each readable 8.8 to 9.6 s, in the upper middle of the picture, flat to the screen, nothing crossing them (comets, mist and the path dim inside their reading boxes), never mirrored in the water.

## Lyric times are estimates

No transcript could be made in this session. The expression times follow the measured sections and the design's lyric estimates (apology line in the first verse at about 0:41, "I thank you" at the start of verse 2, "embrace" a few seconds later). If a rehearsal or transcript shows other times, the words move by editing `T` at the top of `tools/s04_full/song04.py` (and the matching gestures in `people.py`).

## If a rehearsal recording arrives (a cappella, choir only)

Places that can stretch or shrink without harming the story, in order of ease:

1. **The opening (0:00 to 0:31):** a calm establishing shot; any length from about 20 s works. Shift every later time by the difference.
2. **The final chorus (2:25.5 to 3:35.5, 70 s):** the gathering, the lanterns and the slow camera rise can be lengthened or shortened freely; keep the dissolve (10 s) at the end of the singing.
3. **Verse 2 after the embrace (2:08 to 2:25):** the held embrace can run longer or shorter.
4. **Chorus 1 (1:15 to 1:42):** the breath can be retimed to the loudest moment of the new recording.
5. **The calm hold** after the music can be any length (nothing new happens in it).

Harder to change: verse 1 (the walk, the offered hand and the kneel are timed together) and the three reading windows (keep each at least 8 s).

## Owner rules kept

Warm, never dark or cold (the frozen morning of the design is a frosted pearl and rose dawn); no white-outs; only warm gold glitter people, whole, faceless; every touch is between the two sisters (two women); Heavenly Mother only as the low sun and its golden breath of light; calm camera (slow glides, no cuts), calm bottom third (calm water and reflections only); a small signature; no lyrics on screen; frame 0 is a lit morning, never black.
