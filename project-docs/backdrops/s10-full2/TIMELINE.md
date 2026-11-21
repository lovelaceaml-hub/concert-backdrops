# Song 10, Our Mother Saves the World: backdrop version 2, timeline

Version 2 rebuilds the first run (branch `backdrop/s10-full`, 2026-11-18) to the project rules. Design: project-docs/designs/10 Our Mother Saves the World.md, "The Lamp on the Shore". Code: tools/s10_full2/. Times are STAGE VIDEO times (m:ss) unless marked "ref".

## Length and timing

- Live length (DESIGN-SYSTEM 4): 3:31, choir and orchestra. Stage video: 3:31.00 of music, then a 15 s calm hold = **3:46.00 (226.0 s), 13,560 frames at 60 fps, 1920x1080**.
- Reference: the shared recording, Drive file 1NbsvsPQO_wMWEl9OzJNFH6ZQAs_qg6WG, M4A mono 48 kHz, 211.605 s, SHA-256 9c0ad27bfc0cabe1e1881098539649fc0d24ffc81acce3d4d4a13e061f1f991b. Not in the repository.
- Mapping: the reference is 0.605 s longer than the live length (within 1 s). The song block asks for exactly 211.0 s, so the review music is the reference conformed with ffmpeg atempo 1.002869 (pitch kept), and the whole picture timeline is scaled by the same factor (211.0 / 211.605): video time = ref time x 0.99714 during the music. Every section keeps its proportional place. This is an estimate until a rehearsal recording of the live arrangement exists.
- Measured (engine/analyze.py of the pinned engine; librosa loudness in 1 s and 5 s means; onset peaks; first-run chroma repeat pass reused): soft introduction rising from about -30 dB; theme A full 0:10 to 0:24; near silence 0:24 to 0:25; hit 0:25.3; theme A again 0:29 to 0:49 (loud peak about 0:38); near silence 0:49.5 to 0:51.8 (-35 dB); hit 0:51.9; theme B 0:52 to 1:57 with short dips; soft 1:57 to 2:06; theme A returns 2:06 to 2:30 (loudest second 2:09); soft 2:30 to 2:40; new material then theme A 2:40 to 3:23; last hit 3:24.5; final chord rings out by about 3:28.7; music file ends 3:31.0.
- Hits used for sync checks: 0:25.26, 0:51.89, 3:24.52.

## No lyrics yet

The project has no lyrics for this song. The five expressions below are **illustrative** placements: each sits on a phrase whose music fits the act and on the design's own list of likely acts (design section 3: a line where Mother prays for or comforts Her children, reaches out to help, or where we thank Her). They must be checked against the lyrics when they arrive (Astra round 1, finding 14). **No lyric fragments** are shown: the design names none (section 6 is PENDING).

## Sections and picture

| Video time | Music | Stage (design) | Picture | Camera |
|---|---|---|---|---|
| 0:00 to 0:08.2 | soft introduction | A, the restless night | Opening lockup, whole from frame 0, held 8.2 s on calm night sky above the horizon: logo, HEALING CONCERT, The Words of Mother's Love / *That Bring Peace*, gold hairline, **Our Mother Saves the World**. Behind it: the night lake, the arch of nine lights lit, the lamp a small warm star at the centre of the horizon, three small warm lights far out (song 09's boats). The lockup crumbles to glowing dust 8.2 to 9.8. | wide, still, looking slightly up |
| 0:09.0 to the end | | | signature top left (logo mark, title, The Words of Mother's Love That Bring Peace, DEC 6 · 4:30 PM, HEALING CONCERT · LAS VEGAS) | |
| 0:10.5 to 0:24 | theme A | A | the night widens: restless water, scattered dim lights | slow rise (13.5 s) |
| 0:25.3 | hit | B, the lamp is lifted | the star swells softly (small warm bloom) | |
| 0:26.4 to 0:51.4 | theme A again | B | Heavenly Mother, only from behind, robed and veiled, forms at the water's edge, large in frame (about 45 percent of the height); hands cupped, then She lifts the lamp in both hands (0:32.9 to 0:36.1) and the horizon star rises with it to stand behind the lamp; its light falls on the water and the nearest dim lights warm. Midnight blue sky, gold only at the centre (version 1's all-over gold is gone). | down behind Her, slow push |
| 0:51.9 | hit | C, the words go out | | |
| 0:51.4 to 1:08.8 | theme B | C | rescue thread (red) drawn out of the lamp to two men; GREETING | medium, held |
| 1:08.8 to 1:25.3 | theme B | C | rescue thread (pink); CONSIDERATION | medium, held |
| 1:25.3 to 1:42.9 | theme B | C | rescue thread (green); INCLUSIVENESS | medium, held |
| 1:42.9 to 1:51 | theme B | C | wide: lights warming all over the lake, rings of still water | slow move out |
| 1:51 to 2:09.3 | soft section | C | rescue thread (violet); ENCOURAGEMENT | medium, held |
| 2:09.3 to 2:38 | theme A returns, loudest | D, peace across the world | high and wide; every remaining light warms in a wave from the middle out; the GOLD WEB: fine gold threads join the warmed lights, drawn from the middle out (the paths of passed words); the water calms; a deep gold band on the horizon; gold motes rise. No comets. | slow crane up (8.4 s), slow drift |
| 2:38 to 3:11 | soft, then new material | E | down to the water road; six people of light (warm gold) gather facing the lamp, seen from behind, gently swaying | low behind them, slow drift |
| 3:11.5 to 3:24.2 | theme A | E | GRATITUDE | medium, held |
| 3:24.0 to 3:28.7 | final chord | E | all nine lights of the arch glow together (a soft swell, no new star) | |
| 3:30.4 to 3:46.0 | ring out, then 15 s hold | E, night of peace | home view: deep indigo, stars, the lamp resting as a warm star with a faint glow, calm mirror water, all nine lights steady; the people fade softly. The agreed hand-off frame to song 11. Gently alive (twinkling stars, drifting motes, slow camera breath), never black. | slow move home, then still |

## The five expression moments (illustrative)

Exact wording from words.EXPRESSIONS at the approved tag; cream Cormorant serif with the coloured capsule label, block centred about a third of the way down; people below; nothing else in the reading box (other light dims inside it); then the words stream into their own star.

| Expression | Thread and words arrive | Readable | Words reach the star (relight) | Readable time |
|---|---|---|---|---|
| Greeting "How are you?" #EA5A5E | 0:55.8 | 0:57.3 to 1:06.6 | 1:08.6 | 9.3 s |
| Consideration "Can I give you a hand with anything?" #EE62A6 | 1:12.4 | 1:13.8 to 1:23.1 | 1:25.1 | 9.3 s |
| Inclusiveness "It's okay. I understand." #5ABA5A | 1:29.9 | 1:31.3 to 1:40.7 | 1:42.7 | 9.4 s |
| Encouragement "I'll pray (or root) for you. Everything will go well." #9E6AF6 | 1:56.7 | 1:58.2 to 2:07.1 | 2:09.1 | 9.0 s |
| Gratitude "Thank you. It's all thanks to you. You've worked hard." #F2B25E | 3:11.5 | 3:13.1 to 3:22.0 | 3:24.0 | 9.0 s |

After each reading: small hearts drawn in sparks of the expression's colour drift up from the pair, and the expression's symbol (brand_symbols, the campaign's icon redrawn as strokes) is traced subtly by sparks beside the pair, small and faint, never over the words.

## Acting plan (PHASEB update 6; all warm gold glitter people, clothed in garments of light, faces soft and artistic; same gender for every touch)

| Expression | Campaign sense (heavenlymotherslove.org) | What is acted | By whom | Framing |
|---|---|---|---|---|
| Greeting | the first phrase to peace: greet the people you pass every day | each gives the other a slight, warm bow, then a small nod | two men | steady medium shot, turned 24 degrees so the lamp is beside them |
| Consideration | notice who needs a hand and offer practical help | one reaches down and helps the other to his feet | two men | steady medium shot |
| Inclusiveness | forgiving a fault: "it's okay" to someone who made a mistake | an embrace; she holds her friend who is sorry | two women | steady medium shot |
| Encouragement | sincere support to someone facing a hard moment | a hand laid on the shoulder of a friend kneeling in prayer | two women | steady medium shot |
| Gratitude | thanks for a kindness, naming it | one clasps the other's offered hand in both hands and bows | two women | steady medium shot |

Heavenly Mother: only from behind, fully robed and veiled; hands of light lift the lamp. Never a face.

## The arch of nine lights (DESIGN-SYSTEM 12a)

- Start: all nine lit (lit in songs 01 to 08). Song 10 lights nothing new.
- Relights (a brief flare and one new thin ring that stays as a faint halo): Greeting (1) 1:08.6, Consideration (8) 1:25.1, Inclusiveness (4) 1:42.7, Encouragement (7) 2:09.1, Gratitude (2) 3:24.0.
- Final chord 3:24 to 3:28.7: all nine glow together (no new light).
- End: all nine lit and steady.

## Hand-offs

- From song 09 (design 7, CONCERT-OVERVIEW, status 10): song 09's morning dims to deep blue dusk, the sun becomes the warm horizon star, the full arch stays lit. Song 10 opens on the night lake with the arch lit, the lamp-star on the horizon, and three small warm lights far out on the lake (song 09's boats). The lockup sits over this frame for 8 s.
- To song 11 (agreed frame): home night lake, deep indigo sky with stars, the warm horizon star with a faint glow, calm mirror water, wide steady camera, all nine lights steady; no closing card.

## Water

Restlessness (0 = mirror): 0.85 to 0:25, 0.68 by 0:50, 0.5 by 1:45, 0.4 by 2:08, 0.18 by 2:30, 0.1 by 3:10, 0 by 3:31.

## Changes from version 1 (first run)

- 60 fps (was 30), music part exactly the live length 211.0 s (was the 211.6 s reference), 226.0 s in all.
- The nine comets are gone (song 01 only). In their place, song 10's own effects from its design: rescue threads from the lamp, rings of still water, the gold web.
- The lamp section: midnight blue sky with gold only at the centre (lamp light, glow and bloom all reduced). Heavenly Mother more than twice as large in frame (about 45 percent of the height, was under 20).
- Opening lockup as the brief (logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, title), on sky, 8.2 s. Signature moved to the top left with the full line set.
- Gold people only (version 1 mixed in a crystal-seam variant; PHASEB says only gold glitter is approved). Gratitude acted as clasped hands and a bow (was a gift).
- Words now stream into their own stars (were a fade); hearts and symbols in the expression colour.
- Calm bottom third: no star glints, arch, people or lake-light reflections there; lights, rings and threads fade out below a third of the height.
