# Song 07 "May No One Ever Feel Lonely": full backdrop, version 2, timeline

Concert item 8, Sunday December 6, 4:30 PM. Code: `tools/s07_full2/`. Design: `project-docs/designs/07 May No One Ever Feel Lonely.md` ("No Light Left Alone"). Supersedes the first run (`backdrop/s07-full`), which was timed to the 4:07 recording at 30 fps.

## 1. Length (DESIGN-SYSTEM 4 and 9)

- Live length 3:58 = **238.0 s** (male duet or quartet, choir and orchestra). Stage video = 238.0 s of music + **15 s calm hold** = **253.0 s**, 15,180 frames at 60 fps, 1920x1080.
- Reference recording: the church's upload youtu.be/7piuHaCYnFM (Drive file 1wL9dyLETDn3q9ECkIXKrDb3UIt_eAgEA), SHA-256 `2fea173b...6266a`, 246.53 s, last sound at 243.8 s (silent from about 243.5 s). Kept outside git.
- The reference is 5.5 s longer than the live length (more than 1 s), so it is conformed: its music part 0 to 243.5 s is mapped evenly onto 0 to 238.0 s (factor 1.0231). Every section, hit and lyric keeps its proportional place. **This is an estimate until a rehearsal recording exists.** If the live performance differs, the operator holds or advances at the section cues (CUES.md).
- The scene is authored on the reference clock; `tools/s07_full2/clock.py` maps live time to reference time (`ref(t) = 1.0231 t` for the music, then 1:1 for the hold). The review copy uses the same mapping in audio: ffmpeg `atempo=1.023109` (pitch kept).

## 2. Measurements (this session, 2026-11-18)

Measured on the reference with `engine/analyze.py` (render features), a 4 s loudness profile and an onset scan (librosa).

| Section | Reference s | Live s | Loudness |
|---|---|---|---|
| quiet intro | 0 to 14 | 0 to 13.7 | -41 to -21 dB |
| verse 1 (soft, swells) | 14 to 53 | 13.7 to 51.8 | -20 to -13 dB |
| first big lift (chorus 1) | 53 to 77.5 | 51.8 to 75.7 | -12 to -10 dB |
| verse 2 (soft) | 77.5 to 98 | 75.7 to 95.8 | -17 to -15 dB |
| second lift (chorus 2) | 98 to 137.5 | 95.8 to 134.4 | -13 to -9 dB |
| the hush | 137.5 to 149 | 134.4 to 145.6 | -21 to -27 dB |
| verse 3 (building) | 149 to 174.5 | 145.6 to 170.6 | -18 to -13 dB |
| final lift (loudest 216.4) | 174.5 to 230.5 | 170.6 to 225.3 | -11 to -8 dB |
| ending, fade | 230.5 to 243.5 | 225.3 to 238.0 | -14 to -32 dB |
| calm hold | | 238.0 to 253.0 | silence |

Hits (onset peaks, reference s, live s in brackets): 26.9 (26.3), 31.9 (31.2), 38.3 (37.4), 53.4 (52.2), 90.3 (88.3), 96.8 (94.6), 130.5 (127.6), 161.4 (157.8), 186.0 (181.8), 198.2 (193.7), 231.6 (226.4). Tempo about 76 beats a minute (librosa reads 152, double time). The first run's list agreed within 0.1 s except 25.9 (now 26.9) and 185.2 (now 186.0).

## 3. Timeline (live seconds of the stage video)

| Live | Music | Picture | Words (readable) |
|---|---|---|---|
| 0 to 8.6 | quiet intro | Song 06's closing frame: a warm amber evening, camera low and wide at the near shore, big calm sky. It cools into blue dusk over 12 s. | **Opening card** from frame 0, whole to 7.3 s: logo, HEALING CONCERT, The Words of Mother's Love / *That Bring Peace*, gold hairline, **May No One Ever Feel Lonely**. It crumbles to dust by 8.6 s. |
| 8.0 to end | | **Signature** top left to the last frame. | |
| 6.8 to 13.7 | | The elderly traveler (a man of warm gold light, a little stooped) walks slowly in along the shore and stands alone. Two busy men pass the other way. The first stars begin to come out one by one. | |
| 13.7 to 26 | verse 1 | A man walks past behind him without noticing. | |
| 26.3 | hit | Mother's first wish: **footprints of light** appear one by one on the water from the horizon star to the lonely one; the horizon star glows. | "on the path to heaven" (27.7 to 35.6, pearl italic in quotation marks, stitched in step by step) |
| 37.4 to 48 | hit, swell | The man who passed stops, looks back (37.7), turns and walks back to him. | "our Mother's earnest wish" (39.5 to 46.5, gathered from small lights) |
| 51.4 to 63.3 | chorus 1 | **GREETING**: the two men face each other and each gives a slight warm bow (52.1 to 58.4). Coral hearts drift up between them. A Greeting **constellation** (the waving hand) comes out among the stars at the right. First **peace ring** spreads across the far water (52.8). | **GREETING "How are you?"** (52.8 to 61.8), then streams into star 1, **lit for the first time in the concert** (63.3) |
| 61.5 | | The weary traveler sinks onto one knee. | |
| 63.5 to 76 | | **CONSIDERATION**: the helper reaches down his hand; the traveler takes it and is pulled up to standing (65.7 to 67.4), then lays his other hand on the helper's shoulder. Rose hearts drift up; the Consideration symbol (open hands holding a heart) is traced by rose fireflies over the far water at the left. Second peace ring (62.6), third (74.7). | **CONSIDERATION "Can I give you a hand with anything?"** (64.9 to 74.1), then streams into star 8: **relit**, a brief flare and one new thin ring (76.0) |
| 70 to 82 | | The two walk on together toward the horizon star, at the traveler's pace, and fade into the dusk. | |
| 75.7 to 95.8 | verse 2 | Silver mist rises; seven lone lights drift far out on the water. Heavenly Mother, **seen only from behind**, robed in pearl gold, raises Her lamp toward the water (from 88.3, hit). | "please return" (78.7 to 86.8, pearl italic, carried off on the wind) |
| 95.8 to 120 | chorus 2 | The search: two lantern-bearers (men, side by side: the male duet) lead ten villagers with lights out over the misty water. The camera stays low (2.3 m) and well behind Heavenly Mother and looks out level, so everyone stays in the middle band (the first run's lower third problem from 1:38 to 2:17 is fixed; checked every 0.25 s by `check_people.py`). | |
| 120 to 134.4 | | The lost are reached: the bearers offer a hand to two men, who walk home with them; the other lone lights turn warm and come home. On the shore two women embrace; a mother holds her child close. Mother's lamp grows brighter with every return. Peace ring (123.7). | |
| 134.4 to 145.6 | the hush | Mirror lake, mist gone, stars doubled. The family gathered round Mother's lamp, still. Camera still. Peace ring from Mother (134.5). | none |
| 145.6 to 170.6 | verse 3 | A rose gold heavenly dawn; the camera tilts up to the gate of the kingdom and a city of light above the far hills. At the hit (157.8) the family raise their arms toward it. | "the eternal kingdom" (148.6 to 157.0, written down a shaft of light) |
| 170.6 to 191.6 | final lift | Warm and wide; lanterns rise over the far water. | |
| 191.6 to 225 | | The **bridge of light** rises from the shore to the gate; Heavenly Mother, from behind, walks first, lamp raised; the family follows; a procession of small lights walks up the bridge; at the loudest moment (211.5) the gate opens in a warm gold glow (no white-out). | "my heavenly home" (204.3 to 212.7, woven of light, leaving through the opening doors) |
| 225.3 to 238 | ending | Final peace ring across the lake (226.4, hit). The procession has passed into the light; the gate and bridge soften; the camera comes down to the closing frame. | none |
| 238 to 253 | calm hold | Deep navy night lake, perfectly calm, the warm horizon star at the centre, the arch with stars 1 and 3 to 9 lit and star 2 dark, slow drifting dust: gently alive, never black. The gate has faded out completely, so song 08 opens on this frame. | signature only |

## 4. The arch of nine lights (DESIGN-SYSTEM 12a)

- At the start: stars 3, 4, 5, 6, 7, 8, 9 lit; 1 and 2 dark.
- 63.3 s: star 1 (Greeting) lit for the first time in the concert (its line to star 2 does not grow; 2 is dark).
- 76.0 s: star 8 (Consideration) relit: a brief flare and one new thin ring.
- At the end: stars 1 and 3 to 9 lit; star 2 (Gratitude) dark, waiting for song 08.
- The arch keeps one place in the picture (across the top of the sky, under the signature line), whatever the calm camera does, so no star ever passes behind the signature (checked every 0.25 s by `check_layout.py`: closest 37 px).

## 5. Acting plan (PHASEB 6, 13, 15, 17)

All people are **warm gold glitter people**, whole and radiant, clothed in garments of light, faces soft and featureless. Fewer people, more light. Every touch is between two men or two women, or a parent and child. Heavenly Mother only from behind.

| Expression | What is acted | By whom | Look | Framing |
|---|---|---|---|---|
| Greeting (52.8 to 61.8) | The two face each other on the shore path; each gives a slight warm bow (18 degrees, eased, held, released). No handshake, no embrace. Coral hearts drift up between them. | the elderly traveler and the helper, two men | gold glitter | just below eye level, about 7.5 m away, a slow respectful arc of about 15 degrees; both full length in the middle band (about a quarter of the frame height), heads below the words, feet above the bottom third |
| Consideration (64.9 to 74.1) | The weary traveler has sunk onto one knee; the helper steps close and reaches down his right hand; the traveler takes it and is pulled up to standing (1.7 s rise), then lays his left hand on the helper's shoulder. Then they walk on together at his pace. | the same two men | gold glitter | the same framing, still while the hand is given |

The approved acting module's "help_up" pair casts a man and a woman; here both are men (same-gender rule).

## 6. Lyric fragments (five, never with an expression; each its own effect)

1. "on the path to heaven" (Mother's wish): stitched in step by step while the footprints of light land on the water.
2. "our Mother's earnest wish": gathered from small lights.
3. "please return" (Mother's wish): revealed, then carried off on the wind across the water.
4. "the eternal kingdom" (Mother's wish): written down a shaft of light from the gate.
5. "my heavenly home": woven of light over the bridge; it leaves through the opening doors.

## 7. Hand-offs (design section 11, CONCERT-OVERVIEW)

- **From song 06:** opens on 06's warm evening (amber sky, low gold light, camera low and wide at the near shore, arch 3 to 9), cooling into blue dusk over the first 12 s.
- **To song 08:** ends on deep navy night (#0B1530 at the top of the sky), lake perfectly still, warm horizon star at the centre, camera wide at eye level just above the water, arch 1 and 3 to 9 lit, star 2 dark, nothing carried (the gate is gone).

## 8. Simplified from the design (honest list)

- No village houses, bench or lamp post: people stand on the mirror lake.
- The bridge of light rises far out on the water (not from the path's reflection), and "my heavenly home" is woven of light rather than formed by the procession itself.
- Mother's wish quotation marks are typed with the words, not lit as separate candle flames first.
