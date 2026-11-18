# Song 03 "I Reminisce About Your Love": concert backdrop v2 timeline

Concert item 4, Sunday December 6, 4:30 PM, Las Vegas. Design: project-docs/designs/03 I Reminisce About Your Love.md ("The Lake of Memory"). Code: tools/s03_full2/. Branch backdrop2/s03-full (from tag film10-revision3-approved-2026-11-16). This replaces the first run (branch backdrop/s03-full), which was timed to the full 5:55 recording at 30 fps and used the nine comets.

## Length

- Live length 5:13 = 313.0 s (DESIGN-SYSTEM section 4 and 12a.10). Then a 15 second calm hold. Stage video 328.0 s, 19,680 frames at 60 fps, 1920x1080.
- Music part 0 to 313.0 s; the music itself fades out by 309.0 s; 313.0 to 328.0 the calm hold (the dawn lake keeps breathing: petals, motes, the arch, the signature).

## The reference and how it was fitted to 5:13 (an estimate until a rehearsal recording exists)

- Reference: the church's upload youtu.be/TH_p9g7Eu30, 355.09 s, kept as s03.mp3 on Anthony's private Artifact page (SHA-256 c86a81c76aef1af7ae351b0b02eb2109bba78b43beaa3e8f9b329b4e49f9f485). Never in the repo.
- Measured with the pinned engine's engine/analyze.py, a half-second loudness profile, a chroma and timbre self-similarity search and a beat track (0.3755 s per beat in chorus 2).
- The reference is 42.09 s longer than the live length. It holds one repeated passage in chorus 2: the music at 4:32.74 and at 5:14.79 is the same (best chroma and timbre match of every 40.5 to 44 s lag in the song; both points on the beat grid, 112 beats apart). The live version is taken to sing that passage once, so the 42.05 s between those points are removed with a 40 ms crossfade on the beat (tools/s03_full2/prepare.py). The result is 313.04 s; the last 0.04 s of the silent tail is trimmed. Nothing is sped up or slowed down, because it is within 1 s of the live length.
- So live time = reference time up to 4:32.74, and reference time minus 42.05 s after it. If the live arrangement shortens something else (for example the introduction), the operator cues below absorb it; the times are estimates until a rehearsal recording exists.

| Live time | Section (measured) | Reference time |
|---|---|---|
| 0:00 to 0:24.9 | orchestral introduction, swell 0:15.5 to 0:19 | same |
| 0:25 to 1:11 | verse 1 first half, quiet ("Mother, to save my life", "Gathering my memories") | same |
| 1:12 to 1:35 | verse 1 second half, rising ("With a warm and gentle smile", "She cleansed me") | same |
| 1:36 to 2:53 | chorus 1 ("engraved deep in my heart" about 1:55 to 2:14; "Mother is my ev'rything" from 2:14.8) | same |
| 2:53.5 | sudden drop | same |
| 2:53.5 to 3:41 | verse 2 first half (storm, "Mother comforted my heart" 3:06, "Her warm hands" 3:18) | same |
| 3:42 to 4:01 | verse 2 second half, building ("Putting Her hands together", "In my frail and feeble heart") | same |
| 4:01.3 | chorus 2 arrives (sunrise) | same |
| 4:32.74 | the conform join (the repeated passage is sung once) | 4:32.74 / 5:14.79 |
| 4:40.95 | loudest moment | 5:23 |
| 4:49.95 to 4:51.85 | grand pause, near silence | 5:32 to 5:33.9 |
| 4:51.85 to 5:09 | closing "I love You Mother", soft, then fade | 5:33.9 to 5:51 |
| 5:09 to 5:13 | silence (end of the live length) | |
| 5:13 to 5:28 | calm hold | |

Hits used for the sync check: 0:26.63, 3:01.35, 4:02.21 (the strongest note onsets in those sections).

## What is on screen (stage video seconds)

| Time | Picture | Words |
|---|---|---|
| 0.0 to 25 | The home night lake from song 02: indigo sky full of stars, a rose-violet glow on the horizon, the home star resting just left of centre, arch lights 7 and 9 lit (7 with its ring from song 02), the view low over the water. A faint indigo aurora rises with the swell 14 to 22; a soft rain (Her hidden pain) 19 to 27.6. | Opening lockup, whole from frame 0 to 8.6 s, gone by 10.2 s: the campaign logo, HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (italic), a gold hairline, "I Reminisce About Your Love" large. Signature from 10.0 (whole by 11.6) to the last frame. |
| 25.6 to 40.8 | APOLOGY acted (ACTING.md): two women of warm gold glitter light on the far shore, one sitting with her head bowed, the other kneeling beside her with a hand laid gently on her back. The rain stops as the words are written: the lake is a mirror (the stillness that Mother's words bring). | APOLOGY (#F6CE46): written left to right 26.8 to 28.6, readable 28.6 to 38.0 (9.4 s), centred 0.335 of the height. Then the letters let go as sparks that collapse into light 3, which lights for the first time at 40.6 with a wave of light. |
| 29.6 to 41 | The Apology's symbol (a face with a tear) traced by yellow sparks in the sky at the right, outside the reading box, then gone. Yellow hearts drift up from the two women 38.3 to 47. | |
| 47 to 98 | The sky cracks into drifting glass of forgotten memories (high in the sky); from 76 the welcome: aurora and a warm bloom, gold seams heal the cracks 84 to 95, the sky warms to rose. | none |
| 95 to 176 | Chorus 1: the mended moon held by gold seams over a rose dusk lake (plate mended_moon_predawn, slow push). First rose petals 160 to 173. | "engraved deep in my heart" carved in gold by a pen of light that throws sparks, 116.0 to 119.6, readable to 126.0, gone by 127.5. |
| 173.5 to 201 | Verse 2: the storm (plate frozen_rain_lanterns), rain to 186.6; time stops: the drops hang as gold lanterns, lanterns rise 186 to 216. | none |
| 198 to 224 | Her warm hands: violet aurora and sky lanterns (plate aurora_hands_night). Heavenly Mother's cupped hands of light (no figure, no face) gather 204.5 and drift away as light by 212.5. | "Her warm hands" revealed as a frost haze melts from the middle outward, 199.0 to 203.5, readable to 209.5 (a slow warm pulse), gone by 211.0. |
| 221.4 to 236.6 | Her prayer: one column of light from the horizon, a mirror lake (plate prayer_mirror). ENCOURAGEMENT acted: two women of warm gold light, one kneeling in prayer, the other with a hand on her shoulder, both heads bowed. | ENCOURAGEMENT (#9E6AF6): written 222.6 to 224.4, readable 224.4 to 233.8 (9.4 s). The letters collapse into light 7, relit at 237.0 (a brief flare and one new thin ring). |
| 225.4 to 237 | The praying hands symbol traced by violet sparks at the right; violet hearts drift up from the two women 234.1 to 243. | |
| 238 to 244 | The seed of courage falls into the far water; the sky turns predawn rose. | none |
| 240.5 to 328 | Chorus 2 and the hold: the rose dawn (plate rose_dawn: the sun over the mountains where the home star rested, a faint city of light in the clouds, the pale moon), rose petals; a gentle warm bloom as the sun breaks through at 242. The petals hold still at the grand pause (289.95). Lights 3, 7, 9 stay visible on the bright sky. | "I love You Mother": rose petals fly in from the far shore and gather into the words 292.3 to 296.0 (navy on the bright sky), readable to 312.0, then petals lift off the letters and drift down, gone by 315.5. |
| 313 to 328 | The calm hold: the dawn lake breathing, petals, motes, the arch, the signature. The last frame is the morning lake for song 04. | signature only |

Arch: starts with 7 (one ring from song 02) and 9 lit. Lights 3 at 40.6 (Apology). Relights 7 at 237.0 (Encouragement: flare and one new ring). Ends with 3, 7 and 9 lit (3 drawn slightly brighter on the dawn). The arch is a compact arc high in the middle of the sky (x 0.30 to 0.70), kept clear of the signature.

## Hand-offs (design section 12, Designs/CONCERT-OVERVIEW.md)

- From 02 The Rose: 02 ends on the home night lake, deep indigo with a faint rose-pink glow low on the horizon, the home star just left of centre, arch 7 and 9. This video opens on that lake and those lights. Change from the design: the design wrote the title out of a petal's ripple at 0:03; the brief requires the opening lockup readable from frame 0, so the lockup is whole on frame 0 and the petal is left out.
- To 04 I'm Sorry, Please Forgive Me: this video ends on the soft rose dawn lake, sun just above the mountains where the home star rested, the pale moon, rose petals, arch 3, 7 and 9. Change from the design: no "I love You Mother" reflection in the water (the brief: no words mirrored in water), and the moon is the plate's pale moon upper right rather than upper middle.

## Changes from the design and why

- No comets (song 01 only now). The chorus 1 "whole life" comet and the chorus 2 comet spiral are gone; the moon, petals and lanterns carry those sections.
- The 2D spark figures of the first run (Mother from behind, the child on the rock, the shore people) are gone: "fewer people, more light", and only the approved look (warm gold glitter people of the 3D layer). Heavenly Mother appears only as cupped hands of light.
- The expressions are acted by the campaign's everyday acts (two women each), not by the design's grown child and Mother: Heavenly Mother is never shown as a figure with a face, and the acting table of PHASEB 6 gives these acts.
- The design's "glimpse of heaven" at reference 4:30 to 4:51 mostly falls in the removed repeated passage; the faint city of light stays painted in the dawn plate.
- "I love You Mother" is navy on the bright dawn (the rule for bright skies) with rose petals, not rose letters.
