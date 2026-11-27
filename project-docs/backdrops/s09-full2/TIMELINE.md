# Song 09 "Let's Save the World": concert backdrop version 2, timeline

Concert item 10, Sunday December 6, 4:30 PM. Live: piano solo, 4:36. Nothing is sung live, so the picture and the few words on screen carry the meaning. Design: `project-docs/designs/09 Let's Save the World.md` ("The Shore of Calling"). Code: `tools/s09_full2/`. Version 2 supersedes the first run (branch `backdrop/s09-full`).

## Length and timing

- **Live length rules** (DESIGN-SYSTEM 4 and 9): 4:36 = 276.0 s of music, then a 15 s calm hold (gently alive, never black). Stage video = **291.0 s, 17,460 frames at 60 fps**, 1920x1080.
- **Reference** (timing only): the church's "Soloist" upload (youtu.be/O_Ym8-sy9xo), Drive MP3 id 1u4LgRODeqrMaKpdMDjkAVinLjF9QW2-l, SHA-256 `0b276d665905dfc32ef6509035246fa94f81760bf72daad299bce050ed5b7e97`. Measured length **275.736 s**: within 1 s of the live length, so its section times are used **as they are** (no scaling). The review copy plays it untouched from 0 and pads 0.264 s of silence to reach exactly 276.0 s, then the 15 s hold is silent.
- These times are an estimate of the live solo until a rehearsal recording exists. Every section ends in a calm scene, so an operator can hold (see CUES.md).

## Measurements (engine/analyze.py onsets and loudness, re-run on this file; same as the first run)

| Time | Music |
|---|---|
| 0:00 to 0:02.3 | silence |
| 0:02.3 to 0:22 | soft opening, small swell at 0:14.5 |
| 0:22 to 0:28 | soft dip |
| 0:28 to 0:47 | first melody, swell 0:30, accent 0:43.9 |
| 0:50 to 1:08 | verse 1 builds (loud 0:59 to 1:03) |
| 1:10 to 1:32 | fuller, accents 1:13.5 and 1:20.3 |
| 1:32 to 1:59.5 | full, first chorus (peak 1:34) |
| 2:00 to 2:22 | soft interlude (quietest 2:12 to 2:18) |
| 2:22 to 3:04.5 | verse 2, short dips 2:31 and 2:32.8 |
| 3:04.5 to 3:48 | the climax build (loudest 3:20 to 3:47) |
| 3:48 to 3:50 | sharp dip: the pause |
| 3:50 to 4:06 | final chorus line, peak 4:02 |
| 4:06.5 to 4:20 | soft |
| 4:20 to 4:36 | quiet ending; the last note sounds to about 4:31 |

Hit points used for the sync check: 0:59.5 (the call), 2:28.8, 4:02 (the peak). Every piano note (786 onsets) may drop a bead of light; at most one per 0.55 s, rings kept small and far out near the horizon.

Lyric line times (from the sung guide, design section 4): verse 1 0:47 to 1:48 ("God called us" about 1:24), chorus 1 1:48 to 2:13, verse 2 lines at 2:30, 2:42, 2:55.5, 3:08, 3:23, chorus 2 3:34, final chorus 3:50 to 4:06.

## Sections

| Time | Section | Picture | Words on screen (readable) |
|---|---|---|---|
| 0:00 to 0:08.6 | Opening | Song 08's closing frame: still rose-gold dawn lake, wide eye level, all nine arch stars lit, no people. The lockup sits on calm sky: logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), gold hairline, "Let's Save the World" large, navy on the pale dawn. | Lockup readable 0:00 to 0:07.6 (7.6 s), then it crumbles into glowing dust. Signature fades in top left from 0:07.9. |
| 0:08.6 to 0:47 | 1. The lake before dawn | Wind rises, mist gathers, the light cools to a luminous teal Galilee before dawn; three small boats drawn in warm lines with lanterns; each piano note drops a bead of light and the water calms round it. Slow push low over the water. | none |
| 0:47 to 1:11 | 2. The calling | Close to the nearest boat: two fishermen of light (two men). At 0:59.5 a road of gold light runs across the water from the horizon to their boat; the water on it goes still. One rests a hand on his companion's shoulder; both lift their heads to the light. | none |
| 1:11 to 1:48 | 3. As many as the sand | The camera rises: a shore of countless warm grains of light curving away to both horizons. A beam lifts one grain; from 1:24 people of light rise along the shore one by one, joined by fine gold threads; the sand behind them stops flickering. | "God called us": written by the grain's thread of light (pen), navy letters readable 1:22.5 to 1:31.5 (9 s) |
| 1:48 to 2:13 | 4. Mother is life, the first dawn | Pearl and pale gold dawn, shafts of light. Heavenly Mother on the shore, only from behind, arms opening slowly; the water round her becomes a widening mirror; the people open their arms too. | "hope for all humankind": the people's lights gather into the words, navy letters readable 1:55.5 to 2:04.5 (9 s) |
| 2:13 to 2:55 | 5a. The early church | A luminous sea-green twilight in mist (never dark), warm at the horizon. A procession of saints with small lamps walks along the far water's edge, then stops and turns to us, lamps lifted (2:42). | "hardships as honor": the forge, sparks stitch ember-orange letters that become navy letters with an ember-gold glow, readable 2:37.5 to 2:45.5 (8 s) |
| 2:51 to 2:55.5 | (symbol) | The Encouragement symbol (praying hands) is traced by violet sparks in the sky over the saints' lamps, then goes. | none |
| 2:55.5 to 3:10 | 5b. **Encouragement** | Violet flames drift from the lamps over the water to the near shore. A tired woman kneels with head bowed; a friend (another woman) kneels beside her and rests a hand on her shoulder. As the words complete she lifts her head and turns to her friend, her glow strengthens, the water round them goes still; the two rise together. The words collapse into star 7 (3:07.5 to 3:10); violet hearts drift off them; star 7 flares and gains one new thin ring (3:10). | ENCOURAGEMENT (violet capsule) and "I'll pray (or root) for you. Everything will go well." in cream serif, readable 2:58.5 to 3:07.5 (9 s), nothing else in its box |
| 3:10 to 3:34 | 5c. The glory that waits | The mist parts into warm white-gold glory, shafts behind the mountains; the saints walk on; a faint city of light appears in the clouds (from 3:20). | none |
| 3:34 to 3:48 | 6. The world wakes | Full sunrise. People along every shore (waving, bowing, hand on heart); the threads between them carry the colours of the Words of Mother's Love. Heavenly Mother again from behind. | none |
| 3:48 to 4:06 | 7a. The net of light | After the pause, a fisherman of light in the near boat's bow casts a great net (3:49.3): it flies up from his hands and opens across the sky, a diamond mesh of fine gold threads with knots in the nine colours; on the peak (4:02) it flashes and sends threads down to the people. | "Let's save the world": the net weaves the words, navy letters readable 3:52.5 to 4:01.5 (9 s) |
| 4:06 to 4:36 | 7b. Peace settles | The net drifts down like dew; the lake becomes a perfect mirror; the boats lie out on the water with a figure of light at each bow; single beads ring out with the last notes. | none |
| 4:36 to 4:51 | Hold (15 s) | The calm mirror morning, gently alive: a slow ripple about every 6 s, a few sparks rising toward the arch; the sun lowers a little into a warm rose-gold low sun. Never black. | none |

Only one text reads at a time; no fragment is on screen with the expression (nearest: "hardships as honor" ends 2:46.7, the Encouragement starts forming 2:56).

## Arch of nine lights

- At the start: all nine lit (songs 01 to 08 lit them: 01 lights 9 and 7, 03 lights 3, 04 lights 4, 05 lights 8 and 6, 06 lights 5, 07 lights 1, 08 lights 2).
- In this song: star 7 (Encouragement) is **relit**: a brief flare and one new thin ring at 3:10. No star is lit for the first time.
- At the end: all nine lit, star 7 freshly ringed.

## Hand-offs (design section 14, Status/09, CONCERT-OVERVIEW)

- **From song 08:** 08's closing frame: home lake still and golden, wide eye-level view, first rose-gold dawn low behind the mountains, all nine stars lit, no people. Song 09 opens on that look and cools to teal over its introduction.
- **To song 10:** the pearl and pale gold morning sea as a mirror, full arch (star 7 freshly ringed), boats with a figure at each bow, a faint net over the land, a faint city of light in the clouds, camera wide and still. The agreed hand-off has the sun sinking into one warm star and a deep blue dusk at the very end; version 2 ends instead on a **warm low rose-gold sun** so the last frame is never dark (brief: "Never dark, cold, empty"). Song 10 should open on this warm low sun. Flagged in the report.

## Differences from the design doc (and why)

- One continuous file with section cues instead of seven separate operator clips (CUES.md lists the holds).
- Song title in the opening lockup readable from frame 0 (brief and DESIGN-SYSTEM 7) instead of the design's lantern-written title.
- The fragments on bright skies are navy (DESIGN-SYSTEM 7); each fragment still forms with its own effect in light (pen, gathering lights, forge stitch, net weave) and hands over to crisp navy letters for reading.
- The net is cast by a fisherman from the boat (design section 8); the first run's nine coloured comets are gone (they belong to song 01 only).
- The early-church night is a luminous twilight, not a dark night.
- People are warm gold glitter people only (the project handbook: the crystal look is not yet approved).
