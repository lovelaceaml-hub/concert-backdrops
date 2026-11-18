# Song 06 "Heavenly Mother Tells Us to Be Grains": backdrop v2 timeline

Concert item 7, Sunday December 6, 4:30 PM. Design: `project-docs/designs/06 Heavenly Mother Tells Us to Be Grains.md` ("The Field That Grew From One Grain"). Code: `tools/s06_full2/`. Written 2026-11-18 by the song 06 v2 session. Supersedes `project-docs/backdrops/s06-full/TIMELINE.md` (first run).

## Length (DESIGN-SYSTEM 4 and 9)

- Live length (DESIGN-SYSTEM 4): **2:17 = 137.0 s**, choir and orchestra.
- Stage video: 137.0 s of music part + **15.0 s calm hold** = **152.0 s**, **9,120 frames at 60 fps**, 1920x1080.
- All times below are **live (stage video) times** unless marked "ref".

## The reference recording, measured

- Audio: the link-shared concert recording (Drive id 1YqFkD3lQprvotC32xRfC8Dqno0I24hqs, M4A, mono, 48 kHz), SHA-256 `b0b0de6a6f29a6dfc9dbdab935f8049360f05e77896f89cb52b68365f6f61d71`. Kept outside the repo; `tools/s06_full2/prepare.py` downloads and checks it.
- Decoded length **134.847 s** (the container reports 134.89 s). It is loud almost from the first note and stops abruptly at full strength at about ref 134.35 s.
- Engine analysis (`engine/analyze.py` of the pinned engine): tempo about 123 bpm, beat every 0.464 s.
- Repeat analysis (chroma similarity, first run, re-used): verse 2 repeats verse 1 exactly **62.5 s** later (similarity 0.98 to 1.00). Introduction ref 0 to 10.0; verse 1 from ref 10.0; interlude ref 66.4 to 72.5; verse 2 from ref 72.5; the last 6 s repeat the interlude music and are cut off at full strength.
- Loudness (quarter seconds, first run, re-used): soft dips at ref 17.5 to 19.5 (deepest 18.2), 35 to 43, 66.5 to 67.5, 80.0 to 80.5 (the same breath as 18.2, plus 62.5 s), 97 to 104.5. Loudest: ref 64.0, 88.6, 126.25.

## Live-length mapping (an estimate until a rehearsal recording exists)

The reference (134.85 s) differs from the live length (137.0 s) by 2.15 s, more than 1 s, so it is conformed. With no rehearsal recording there is no evidence which sections run longer live, so **every section is scaled by the same factor, 137.0 / 134.847 = 1.01597**, and every hit keeps its proportional place. In code: the song module keeps reference time; `render.py` maps each live frame `t` to ref `t / 1.01597` in the music part, and to ref `134.847 + (t - 137.0)` in the hold (normal speed). The conformed music is `ffmpeg atempo=0.984285` (pitch kept): 136.99 s, then silence to 152.0 s. **This is an estimate**: re-time from a rehearsal recording when there is one.

| Section | Ref start | Live start |
|---|---|---|
| Introduction | 0.0 | 0.0 |
| Verse 1 (the grains line) | 10.0 | 10.16 |
| First refrain (lines 6 and 7) | 46.3 | 47.04 |
| Interlude | 66.4 | 67.46 |
| Verse 2 (the grains line) | 72.5 | 73.66 |
| Final refrain | 108.8 | 110.54 |
| Last note (music stops) | 134.35 | 136.50 |
| Calm hold | 134.85 | 137.00 to 152.00 |

## Section timeline (live seconds)

| Live time | Music | Picture |
|---|---|---|
| 0.00 to 8.74 | introduction | Hand-off frame from song 05: the home lake on a warm late afternoon, blue sky, sun low over the far mountains, calm mirror water, camera wide and level, tilted up so the horizon is low and the sky calm behind the letters; the arch with stars 3, 4, 6, 7, 8, 9 lit. **Opening lockup whole from frame 0 and fully readable to 7.62 s**: logo, HEALING CONCERT, "The Words of Mother's Love" / *That Bring Peace*, the song title large. The light ripens into the long amber harvest evening. The grain of light hangs above the middle of the lake in the horizon star's warm halo (a slow heartbeat). The lockup crumbles into golden dust 7.62 to 8.74. |
| 8.74 to 152.00 | | **The signature**, top left, on every frame to the end. |
| 9.35 to 10.16 | | The halo lets the grain go; it touches the water at 10.16 with no splash; one ring of light runs to every shore. |
| 10.16 to 17.88 | verse 1, line 1 | The grain gives its light away as it sinks; gold roots race out across the lake bed. Fragment "grains who will sacrifice" readable 11.99 to 16.66, then its letters sink into the lake. |
| 17.27 to 26.01 | breath 18.49, line 2 | A mother, her grown daughter and a small child (gold glitter, whole, clothed) form out of sparks on the near shore; a loaf of light is shared. Fragment "Love one another" readable 19.91 to 24.99. |
| 26.01 to 31.50 | line 3 | No words. Their inner light deepens; golden rings from their feet; the mother's arm rounds the child. |
| 31.50 to 42.26 | line 4 | The camera rises over the plain of homes in long shadow (deep ember dusk, warm, waiting). A beam of the horizon star falls across the plain (39.62). |
| 42.26 to 49.58 | line 5 | Windows light from the beam outward. Fragment "the world brightens up" readable 43.48 to 48.36, then it rises. |
| 47.04 to 67.46 | lines 6 and 7, first refrain, peak 65.43 | Golden wheat of light rises across the shores in waves on the strong beats; lanterns lift (58.42 on); at the peak the field bows and rises like a breath and the horizon star blooms gently. |
| 67.46 to 73.66 | interlude | Ember dusk. A second grain falls on the dry wilderness (68.07 to 69.49) and the ground wakes. The camera comes down to the narrow path by the water. |
| 72.03 to 83.31 | verse 2, line 1 (grains) | **CONCESSION "Please, after you."** forms 72.03, **readable 73.25 to 81.89 (8.6 s)**, collapses into star 5, which lights for the first time (83.21). Sky blue embers trace the Concession symbol in the air over the wheat to the right (75.8 to 78.9); sky blue hearts drift off as the words leave (81.8 to 83.7). |
| 83.51 to 95.70 | breath 81.89, lines 2 and 3 | **INCLUSIVENESS "It's okay. I understand."** forms 83.51, **readable 84.63 to 94.28 (9.7 s)**, collapses into star 4, which flares again with one new thin ring (95.60). Hushed: the field dims and stills. Green petals settle into the Inclusiveness symbol beside the two women (87.0 to 93.6), then blow on; green hearts drift off as the words leave. |
| 95.70 to 103.02 | line 4 | Living water: gold fills the cracks of the wilderness like the veins of a leaf; a spring wells up; green gold shoots. Fragment "waters this wilderness" readable 97.43 to 102.00. |
| 103.02 to 110.74 | line 5 | Blossoms open; a rose gold wind of fragrance crosses the field and bends the wheat. Fragment "the fragrance of Her love" readable 104.85 to 109.52, then carried off on the wind. |
| 110.54 to 136.50 | lines 6 and 7, final refrain, peak 128.32 | The camera rises to the highest view of the song: one land of light, lanterns lifting all together (121.41 on), the horizon star's gentle bloom at the peak, the field breathing on the beats, pairs of people of light walking far off. |
| 136.50 to 137.00 | the last note | A soft warm bloom on the last note, released as the music stops. |
| 137.00 to 152.00 | **calm hold (15 s)** | The camera glides down to the near shore, low and wide. A warm evening settles (amber to soft violet at the top); the field barely sways; one ripe grain falls (138.75 to 140.55) where the first fell and one slow ring widens; the small lantern on the near shore glows a little brighter than the rest (hand-off to song 07); the arch shows stars 3 to 9. Gently alive to the last frame; never black. |

## The expressions

| Expression | Exact words (words.EXPRESSIONS) | Colour | Lyric moment | Forms | Readable | Into the arch |
|---|---|---|---|---|---|---|
| Concession | "Please, after you." | #62B2FA | verse 2, line 1, "grains who will sacrifice" (DESIGN-SYSTEM 12a, a provisional exception) | 72.03 | 73.25 to 81.89 (8.6 s) | star 5 lights for the first time, 83.21 |
| Inclusiveness | "It's okay. I understand." | #5ABA5A | verse 2, line 2, Mother says pardon one another | 83.51 | 84.63 to 94.28 (9.7 s) | star 4 flares again with one new thin ring, 95.60 |

The block is centred about a third of the way down (36 percent), upper middle, cream Cormorant serif with the coloured capsule label (the approved Revision 3 word style). Nothing competes inside the reading box: every light in the scene, the arch included, is dimmed inside the box while the words are up.

## Acting plan

| Expression | What is acted | By whom | Look | Framing |
|---|---|---|---|---|
| Concession | Stepping aside with an open palm. A man in a hurry on the narrow path stops short (73.1), one hand to his heart for a long breath (73.1 to 75.1), steps aside toward the wheat and opens his right hand toward the way (76.3 to 81.2); an elder man walks past and bows his head in thanks (77.8 to 80.5). | Two men | Warm gold glitter people, whole, clothed (tunic, robe) | Low at the water, camera at eye height 0.95 m, people mid-frame below the words, feet above the bottom third |
| Inclusiveness | An embrace of two women. A young woman kneels at the water's edge, head bowed, the family lantern dark on the water; an older woman walks to her, kneels at her level, lays a hand on her shoulder (85.3 to 88.2), relights the lantern from her own (88.80), gives it back into her hands, they rise (89.81) and embrace (91.64 to 96.3). | Two women | Warm gold glitter people, whole, clothed (dress, robe with a veil) | Closest framing of the song, low and hushed; the field dims around them |

Other people: the family of three (a mother, her grown daughter, a small child; touch only between the mother and her child) in verse 1, and a few small walkers far off in the refrains (no touching).

## Lyric fragments (5, from the design; never on screen with an expression)

| Fragment | Readable | Effect |
|---|---|---|
| "grains who will sacrifice" | 11.99 to 16.66 | Sown letters: written above the lake as the grain sinks; the letters sink into the water like seeds |
| "Love one another" | 19.91 to 24.99 | Over the family of three as the loaf of light is shared; fades into their warm inner light |
| "the world brightens up" | 43.48 to 48.36 | Over the plain as the windows light; rises with the light |
| "waters this wilderness" | 97.43 to 102.00 | Over the wilderness as liquid gold fills the cracks |
| "the fragrance of Her love" | 104.85 to 109.52 | Carried off sideways on the rose gold wind of fragrance |

## The arch of nine lights

- Start: stars **3, 4, 6, 7, 8, 9** lit (from song 05).
- 83.21: star **5 Concession** lights for the first time (a calm blue star).
- 95.60: star **4 Inclusiveness** flares again with one new thin ring.
- End: stars **3, 4, 5, 6, 7, 8, 9** lit (1 Greeting and 2 Gratitude still dark, for songs 07 and 08).

## Hand-offs (design section 10 and Designs/CONCERT-OVERVIEW.md)

- From 05 "God Bless You!": the home lake on a warm late afternoon, blue sky over a pale gold horizon, sun low and softly golden, calm bright mirror, camera wide and level, arch 3, 4, 6, 7, 8, 9 lit. The seed of light becomes this song's grain. (The blossom petals of 05's frame are not drawn in v2: noted as a gap.)
- To 07 "May No One Ever Feel Lonely": the lake after the harvest, golden wheat of light on the shores, a slowly widening ring at the lake's centre, camera low and wide at the near shore, arch 3 to 9 lit, one small lantern on the near shore a little brighter than the rest, a warm early evening sky.
- Conflict noted: CONCERT-OVERVIEW.md's table lists song 06 only as "Inclusiveness (4) again" and proposes Concession first lit in song 11; DESIGN-SYSTEM 12a (provisional decision 1), the 06 design and this brief place Concession here. This build follows 12a.

## Sync checkpoints (live)

- 10.16: the grain touches the water on the verse 1 downbeat.
- 18.49 and 81.89: the two identical breaths; the family forms at the first, Concession's words finish reading at the second.
- 128.32: the loudest hit of the final refrain (the horizon star's bloom).
- 136.50: the music stops; the hold begins at 137.00.

## Totals

9,120 frames at 60 fps = 152.000 s: 137.0 s of conformed music, then 15.0 s of calm hold.
