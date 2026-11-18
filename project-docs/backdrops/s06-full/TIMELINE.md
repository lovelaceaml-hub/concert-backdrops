# Song 06 "Heavenly Mother Tells Us to Be Grains": full backdrop timeline

Concert item 7, Sunday December 6. Design: `project-docs/designs/06 Heavenly Mother Tells Us to Be Grains.md`. Code: `tools/s06_full/`. Written 2026-11-18 by the song 06 backdrop session.

## The recording, measured

- Audio: the link-shared concert recording (M4A, mono, 48 kHz), SHA-256 `b0b0de6a6f29a6dfc9dbdab935f8049360f05e77896f89cb52b68365f6f61d71`. Kept outside the repo; `tools/s06_full/prepare.py` downloads and checks it.
- Length 134.85 s (2:14.85). It is loud almost from the first note (about -21 dB RMS by 0.25 s) and stops abruptly at full strength at about 134.3 s (the last 0.5 s falls from -14 dB to -40 dB). So the picture makes the ending: a soft warm bloom on the last note, then the calm hold settles.
- Engine analysis (`engine/analyze.py`): tempo about 123 bpm, beat every 0.464 s, key D sharp major.
- Repeat analysis (chroma similarity at every lag): verse 2 is verse 1 played again exactly **62.5 s** later (similarity 0.98 to 1.00 from 10 s on). The stretch 0 to 10 s (introduction) only loosely matches 62.5 to 72.5 s (the interlude), so verse 1 starts at about 10.0 s and verse 2 at about 72.5 s. The last 6 s (128.9 to 134.85) repeat the interlude music and are cut off at full strength.
- Quarter-second loudness confirms the coordinator's map: soft dips at 17.5 to 19.5 (deepest 18.2), 35 to 43, 66.5 to 67.5, 80.0 to 80.5 (the same breath as 18.2, plus 62.5 s), 97 to 104.5 (the same as 35 to 43, plus 62.5 s). Loudest moments: 64.0 s (-10.4 dB), 88.6 s (-9.8 dB), 126.25 s (-11.0 dB), and a strong final stretch 124 to 134.

Line times are the guide recording's line times (design doc section 4) scaled to this recording's verse length (62.5 / 56.0 = 1.116) from each verse start. They are estimates placed between measured breaths, not checked against sung words (the lyrics are not used on screen beyond the design's five short fragments).

## Section timeline (song time, seconds)

| Time | Music | Picture |
|---|---|---|
| 0.0 to 8.6 | introduction | The home lake in the late afternoon handed over from song 05, the title "Heavenly Mother Tells Us to Be Grains" with HEALING CONCERT and the concert title, readable from frame 0. The grain of light hangs over the middle of the lake, held in the horizon star's warm halo (a slow heartbeat). The light ripens into a long amber harvest evening. |
| 7.5 to 8.6 | | The title crumbles into golden dust; the small signature (bottom left, as Revision 3) stays from 8.8 s to the last frame. |
| 9.2 to 10.0 | | The halo lets the grain go; it falls and touches the water at 10.0 with no splash, one ring of light runs to every shore. |
| 10.0 to 17.3 | verse 1, line 1 (grains) | The grain dims as it gives its light away; fine gold roots race out across the lake bed. Fragment "grains who will sacrifice" readable 11.8 to 16.4, then its letters fall into the lake. |
| 17.3 to 25.6 | breath at 18.2, line 2 | A mother, her grown daughter and a small child form out of sparks on the near shore; a loaf of light is shared. Fragment "Love one another" readable 19.6 to 24.6. |
| 25.6 to 31.0 | line 3 | No words. Their light deepens; golden rings spread from their feet; the mother's arm rounds the child. |
| 31.0 to 41.4 | line 4, soft 35 to 43 | The camera rises high over the plain of homes in long shadow (deep ember dusk, warm, waiting). A beam of the horizon star falls across the plain (39 s). |
| 41.4 to 48.8 | line 5, brightening from 42 | Windows light from the beam outward, home by home. Fragment "the world brightens up" readable 42.8 to 47.6. |
| 46.3 to 66.4 | lines 6 and 7, first refrain, peak 64.4 | The roots rise: golden wheat of light grows across the shores in waves on the strong beats; a few people of light among it; lanterns lift (57.5 s on). At the peak the field bows and rises like a breath and the horizon star blooms gently. |
| 66.4 to 72.5 | interlude | Ember dusk. A second grain falls on the dry wilderness (67.0 to 68.4) and the ground wakes. The camera comes down to the narrow path by the water. |
| 70.9 to 82.0 | verse 2, line 1 (grains) | **CONCESSION "Please, after you."** forms 70.9, readable 72.1 to 80.6 (8.5 s), leaves 80.6 to 82.0 as star 5 lights for the first time (81.9). Acted: a man in a hurry stops short (72.0), a hand to the heart for one long breath, steps aside (74 to 75) and opens his hand toward the way; an elder walks past bowing in thanks (76.6 to 79.2). |
| 82.2 to 94.2 | breath at 80.6, lines 2 and 3 | **INCLUSIVENESS "It's okay. I understand."** forms 82.2, readable 83.3 to 92.8 (9.5 s), leaves to star 4, which flares again with one new ring (94.1). Hushed: the field dims and stills. Acted by two women: the young one kneels at the water's edge, head bowed, the lantern dark on the water; the older one kneels beside her, a hand on her shoulder, relights the lantern (87.4), places it back in her hands, they rise (88.4) and embrace (90.2 to 94.8). |
| 94.2 to 101.4 | line 4 | Living water: gold fills the cracks of the wilderness like the veins of a leaf, a spring wells up, green gold shoots rise. Fragment "waters this wilderness" readable 95.9 to 100.4. |
| 101.4 to 109.0 | line 5, soft 97 to 104.5 | Blossoms open; a rose gold wind of fragrance crosses the field and bends the wheat. Fragment "the fragrance of Her love" readable 103.2 to 107.8. |
| 108.8 to 134.35 | lines 6 and 7, final refrain, peak 126.3 | The camera rises to the highest view of the song: one land of light, lanterns lifting all together (119.5 on), the horizon star's gentle bloom at the peak, the field breathing on the beats, pairs of people of light walking. |
| 133.9 to 134.35 | the last note, at full strength | A soft warm bloom swells on the last note and releases as the music stops. |
| 134.35 to 149.87 | silence (15 s hold) | The camera glides down to the near shore, low and wide. A warm evening settles (amber to blue violet at the top), the field barely sways, one ripe grain falls (136.6 to 138.4) exactly where the first fell and one slow ring widens, the small lantern on the near shore glows a little brighter than the rest (hand-off to song 07), the arch shows stars 3 to 9. Gently alive to the last frame; never black. |

Arch of nine lights (behind and above everything, dimmed inside the words while they are read): stars 3, 4, 6, 7, 8, 9 lit from the start; 5 Concession lights at 81.9; 4 Inclusiveness flares again at 94.1.

## Sync checkpoints

- 10.0 s: the grain touches the water on the verse 1 downbeat.
- 18.2 s and 80.6 s: the two identical breaths (verse 1 and verse 2); the family forms at the first, Inclusiveness begins after the second.
- 126.3 s: the loudest hit of the final refrain (horizon star bloom).
- 134.35 s: the music stops; the hold begins.

## Totals

4,496 frames at 30 fps = 149.867 s: 134.85 s of music, then 15.0 s of silence.
