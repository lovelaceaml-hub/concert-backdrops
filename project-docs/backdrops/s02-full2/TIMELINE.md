# 02 The Rose: backdrop version 2, timeline

Written 2026-11-18 by the song 02 cloud session (version 2 build). Code: `tools/s02_full2/` (rose.py the song module, render.py the stage clock, opening and signature, export.py the render, deliverables and checks). It supersedes the first run (`backdrop/s02-full`, timed to the recording at 30 fps).

## Length and the time map

- Live length (DESIGN-SYSTEM 4): **4:00 = 240.0 s**. Stage video: 240.0 s of music time plus a **15 s calm hold** = **255.0 s, 15300 frames at 60 fps**, 1920x1080.
- Reference: the organisers' recording, Drive file 1UoGwToBnpl-jlEJDRfqMnHMfluupGOhO (M4A), 212.29 s, SHA-256 45ba01ba...19f9. It is 27.7 s shorter than the live length, so it was conformed.
- **Conform (an estimate until a rehearsal recording exists):** every section of the reference is scaled by the same factor, 240 / 212.29 = 1.1305, so stage time = song time x 1.1305. All hits stay proportionally placed. A uniform scale was chosen because nothing in the recording shows where the live trio adds time (an introduction, a repeat or a slower tempo); when a rehearsal recording exists, the per section anchors in rose.py (dicts `T` and `WT`, in song seconds) can be re-mapped section by section without redesigning.
- The review copy's music is the reference stretched with ffmpeg atempo 0.884533 (pitch kept) to exactly 240.0 s, then 15 s of silence.

## Measurements (made in this session)

engine analyze.py features (the picture reacts to them), plus loudness in 8 s windows and onset peaks (librosa):

- Loud from the first seconds: no long piano introduction.
- Softer stretches: 1:04 to 1:12 (about -30 dB against -24 dB around it), 1:36 to 1:44, 2:40 to 2:48; the music fades from about 3:24 and is very soft (about -35 dB) from 3:20 to the end at 3:32.3.
- Onset peaks: 0:25.3, 0:32.3, 1:05.1, 1:21.0, 1:24.3, 1:51.0, 2:02.3, 2:39.8, 3:24.8, 3:30.4. Accents used as hit points (from the first run's measurement, confirmed in the loudness map): 0:39.8, 0:44.5, 1:06.0, 2:16.4, 2:23.6, 2:47.5, 3:13.6.
- Form (first run's chord repeat map, reused): verse 1 about 0:02 to 0:46, verse 2 about 0:46 to 1:46, verse 3 from 1:46 with a key change near 2:00, the last half of verse 3 sung again as the finale from about 2:39, a soft ending. The words cannot be heard by this session, so moments are placed by the measured form, not by ear.

## Timeline (stage time; song time in brackets)

| Stage | Song | Section | On screen |
|---|---|---|---|
| 0:00 to 0:07.0 | 0:00 to 0:06.2 | opening | the opening lockup, whole from frame 0: logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, The Rose; navy on song 01's pale gold morning sky (the hand-off), camera looking up into calm sky |
| 0:07.0 to 0:08.6 | | | the lockup dissolves into glowing dust; the signature fades in at the top left (8.0 to 9.6) and stays to the last frame |
| 0:08.6 to 0:18.7 | 0:07.6 to 0:16.5 | dusk | the morning passes through dusk into the silver blue winter night; the camera tilts slowly down to the lake; first snowflakes |
| 0:18.7 to 0:45.0 | 0:16.5 to 0:39.8 | verse 1 | night lake, snow in three depths, the warm home star on the horizon, arch with 9 and 7 lit, three thin ribbons of light (the trio) high in the sky |
| 0:45.0 to 0:50.3 | 0:39.8 to 0:44.5 | hit points | the home star leaves the horizon and glides down to the near shore: the seed; a warm glow stays under the ground |
| 0:52.6 to 1:54.2 | 0:46.5 to 1:41.0 | verse 2 | a young woman of light holds a small warm light (her heart) against her chest; frost grows across the lake |
| 0:58.8 to 1:14.6 | 0:52 to 1:06 | | a point of gold light skates on the new ice in long loops (no words); the snow almost stops in the quiet breath |
| 1:37.2 to 1:54 | 1:26 to 1:41 | end of verse 2 | she lifts her cupped hands, her light rises above her palms and then into the sky; she fades softly (whole) |
| 1:49.7 to 1:58 | 1:37 to 1:44.5 | the longest night | the frozen lake becomes a mirror of the stars |
| 1:58.1 to 2:14.5 | 1:44.5 to 1:59 | verse 3 | a traveler of light (a woman, hooded robe) crosses the ice with a small lantern, footprints glowing behind her; fragment **"too lonely"** readable 2:03.7 to 2:11.8; she kneels at 2:14.5 |
| 2:16.2 to 2:24.3 | 2:00.5 to 2:07.6 | key change, choir | the snow on the ice lights flake by flake like candles; the Encouragement symbol (praying hands) appears as a violet constellation among the stars, top right |
| 2:21.9 to 2:26.6 | 2:05.5 to 2:09.6 | | the three ribbons pour down and become three women of light |
| 2:27.6 to 2:42.3 | 2:10.6 to 2:23.6 | climax | **ENCOURAGEMENT**, "I'll pray (or root) for you. Everything will go well." readable **2:30.1 to 2:40.1 (10.0 s)**; acted (see ACTING below); everything else almost still |
| 2:40.1 to 2:42.3 | 2:21.6 to 2:23.6 | | the words rise into star 7: a brief flare and one new thin ring; star 9 glimmers once; violet hearts drift up from the words, then from the women |
| 2:42.3 to 3:00.7 | 2:23.6 to 2:39.8 | | a violet wave across the ice; the traveler rises with their help; the camera glides to the seed under the ice; fragment **"the seed"** readable 2:51.4 to 2:58.4 (written in roots) |
| 2:59.8 to 3:33.4 | 2:39 to 3:08.8 | finale | pearl and blush dawn, rays, the ice melts from the far side, blossoms of light open on the far shores, a stem of light rises from the seed, a bud, the rose opens (3:31.4 to 3:42.7) |
| 3:33.4 to 3:47.5 | 3:08.8 to 3:21.2 | last line | fragment **"becomes the rose"** readable 3:35.7 to 3:45.2, navy ink on the pale dawn sky, the rose at the left beside it |
| 3:46.7 to 3:55.7 | 3:20.5 to 3:28.5 | soft ending | a small warm light lifts from the rose and floats home to the horizon; the four women fade softly into light |
| 4:00.0 to 4:15.0 | (hold) | calm hold | the rose on the shore, the sky cooling to the home night; the Encouragement returns once, readable **4:02.2 to 4:10.5 (8.4 s)**, then settles softly into star 7 (a gentle glow, no second ring); from 4:12.0 one apricot petal lifts from the rose and floats up (it lands in song 03) |

Arch: start 9 and 7 lit (from song 01), seven dim seeds. 02 lights nothing new and relights 7 once (2:42). End: 9 and 7 lit. No Greeting (DESIGN-SYSTEM 12a.3). No comets (song 01 only).

## Hand-offs (design section 16, Status/02, CONCERT-OVERVIEW: 01 to 02 and 02 to 03 are agreed)

- From 01: 02 opens in 01's gold morning colours with the arch fixed (9 and 7 lit), then darkens through dusk into the winter night.
- To 03: the hold ends on the home night lake (deep indigo, a faint rose glow low on the horizon, the home star back at the left of the horizon, arch 9 and 7 lit and calm); one apricot petal lifts from the rose in the last seconds and floats up out of frame.

## ACTING plan

| Expression | Acted by | What they do | Look | Framing |
|---|---|---|---|---|
| Encouragement (2:30.1 to 2:40.1) | four women of warm gold glitter light: the kneeling traveler and three women of the trio | the PHASEB 6 act "a hand on the shoulder of someone kneeling" and "kneeling in prayer": one woman lays her hand on the kneeling traveler's shoulder; one kneels beside her and holds her light to the traveler's lantern; one kneels behind with hands folded in prayer; at 2:34.6 the traveler lays her hand over the kneeling woman's hand on the lantern and both lights brighten | gold glitter (handbook: only warm gold glitter people), clothed in coats and a hooded robe of light, faces soft and featureless | low, close and still, the group below the words (feet above the bottom third) |
| Encouragement again (hold, 4:02.2 to 4:10.5) | acted by light alone: the open rose glowing at the left, the word returning | none (calm hold) | | wide, calm |

Every touch is between women. Heavenly Mother does not appear as a figure (the star that became the seed and the sunrise carry her love).

## Fragments (3, from the design)

| Fragment | Readable | Its effect |
|---|---|---|
| "too lonely" | 2:03.7 to 2:11.8 | appears in the lantern's breath, then the wind carries it away |
| "the seed" | 2:51.4 to 2:58.4 | written in the seed's roots under the ice |
| "becomes the rose" | 3:35.7 to 3:45.2 | gathered from the dew of the rose, navy ink on the dawn sky, falls back as petals |

None is on screen with an expression.

## Changes from the first run

- Timed to the 4:00 live length (was the 3:32 recording); 60 fps (was 30); 15 s hold.
- New opening lockup (logo, HEALING CONCERT, concert title, song title) readable from frame 0 for 7 s; the signature at the top left from 0:08 to the last frame with the song title and the date line (was a bottom left signature switching between palettes).
- Nine coloured comets removed (song 01 only); the seven unlit seeds stay dim all song.
- Hearts in the Encouragement violet drift off the words and the women; the Encouragement symbol appears in the sky as a constellation.
- The frost now shows (the first run marked it static and it never appeared), at a quiet strength.
- Bottom third kept calm (snow, frost, candles, blossoms, footprints and the dancer fade below a third of the height).
- Verse nights lifted to silver blue; dawn camera moved so the rose stands clear of the words; the hold ends at night for song 03.
