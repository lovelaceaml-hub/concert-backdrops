# 01 All You Stars of Zion: backdrop version 2, timeline

Written 2026-11-18 by the song 01 cloud session (version 2 build, on the coordinator's go-ahead: Anthony, "Just do a new one"). Code: `tools/s01_full2/` (`s01_full2.py` the song module, `words.py` the words on screen, `render.py` the stage clock, opening and signature, `prepare_s01.py` engines, features and score, `export.py` the joined render, the three deliveries and the checks). It supersedes the first run (`backdrop/s01-full`, 30 fps, title as a constellation, no hearts or symbols).

## Length and the time map

- Live length (DESIGN-SYSTEM 4): **3:08 = 188.0 s**, brass ensemble, no singing live.
- Reference: the church brass ensemble recording (the performance of youtu.be/YuBYZDgmf0I), Drive file 1wmWrkUIuIU_zE1Hogp_hPUFYBH0J5YJR, SHA-256 `2ef650dc...7a01` (checked by `prepare_s01.py`), **187.97 s**.
- The reference is within 1 s of the live length (0.03 s short), so it is **used as is**: stage time = song time. The music part of the stage video is exactly 188.0 s (the last 0.03 s is silence), then the **15 s calm hold** (Anthony's choice, 2026-11-18): **203.0 s, 12,180 frames at 60 fps**, 1920x1080.
- The review copy's music is the reference untouched (padded with silence to 203.0 s).

## Measurements (engine/analyze.py on the reference, pinned engine d928ff9; confirmed from the first run)

- Key B-flat major. Felt pulse about 99 BPM (beat grid 0.418 s at double time).
- Loud hits, refined to the nearest onset: 7.11, 30.60, 77.18, 87.33, 106.39, 125.04, 131.54, 141.48, **147.77 (largest)**, 177.35.
- Loudest stretch 1:39 to 1:43. Quiet interlude about 1:53 to 2:05 (down to -35 dB). Natural fade 3:03 to 3:08 (-19 dB to -38 dB).
- Structural boundaries: 0.0, 31.0, 51.7, 61.4, 110.0, 143.3, 148.2, 170.9.
- Sync points used to check the render: 7.11, 147.77, 177.35.

## Timeline (stage time = song time)

| Time | Section | On screen |
|---|---|---|
| 0:00 to 0:07.0 | opening | The opening lockup, whole and still from frame 0 on the calm starry night lake: campaign logo (its lines draw a glint over 0.1 to 1.3 s, the logo is whole throughout), HEALING CONCERT, The Words of Mother's Love / *That Bring Peace*, a gold hairline, **All You Stars of Zion** large; warm white with gold accents on the night sky. The gold morning star waits on the horizon; nine arch seeds are not yet drawn. |
| 0:07.0 to 0:08.8 | first brass hit (7.11) | The lockup shrinks and glides into the top left corner and becomes the signature (whole from 8.8 s to the last frame, never flashing). A soft warm flash at the morning star on the hit. |
| 0:10.6 to 0:13.2 | | The arch of nine lights draws across the sky as a hair-thin line with nine dim seeds (no star lit). |
| 0:19.6 to 0:30 | | Signature effect: **the nine coloured comets** (song 01 only) fall from the nine seeds, one after another; six land on the shore and unfold into warm gold glitter people (each forms over 1.8 s), three fall into the lake and wake its glints. |
| 0:30.6 | verse lift hit | The morning star flares once. |
| 0:38 to 0:55 | verse | **COMPLIMENT** acted by two young women (see ACTING). Words form 39.0 to 42.0, **fully readable 42.0 to 52.0 (10 s)**, upper middle, nothing else near them. The Compliment symbol (clapping hands with confetti) is traced in sparks high in the night sky at the right, 40 to 55. |
| 0:52 to 0:58 | breath | The words loosen into a cloud of their colour and rise into **star 9** of the arch; navy-blue hearts drift up from the words and from the two women; the lake stills to a mirror. **Star 9 lights at 0:58** (flare, then steady). |
| 0:58 to 1:24 | chorus 1 | The flame passes hand to hand along the six people (59.4 to 65.2); fragment **"like a torch"**: a line of fire runs along and lights each letter (60 to 62), **readable 62 to 67**, the letters let go as rising embers (67 to 69). Torches lift on the chorus; soft beams of glory lean from the torches toward Heavenly Mother, far on the shore, seen only from behind (68 to 86). The sky flushes rose gold. |
| 1:24 to 1:27 | breath | Gentle light falls onto every torch. |
| 1:27 to 1:53 | chorus 2 | The young people walk out on the lake (87.7 to 104). Peak 1:39 to 1:43: a golden net of light drifts down far ahead and settles on the lake; a soft warm gold bloom (version 2: no pink-white haze, the scene stays visible). |
| 1:53 to 2:05 | quiet interlude | Blue hour, the camera close on the shore; fragment **"dew of the dawn"** stitched in a fine thread of silver light (114.6 to 117), **readable 117 to 122**, its threads drift down to the lake; silver dew falls where the tree will grow. |
| 2:05 to 2:27 | | The tree of light grows from the dew (from the 2:05 hit), blooms on 2:11.5; blossoms drift on the 2:21.5 hit. |
| 2:27.8 | biggest hit (147.77) | The sun rises; fragment **"Arise"** stands up out of the lake letter by letter, whole on the hit, **readable 147.8 to 151.8**, then its letters stretch into the first sunrise rays. |
| 2:32 to 2:56 | last section | Morning. Four companions form in deep gold (152 to 154) round the pair, torches lit. **ENCOURAGEMENT** acted by two young men (see ACTING). Words form 158 to 161, **fully readable 161.0 to 171.0 (10 s)**. The Encouragement symbol (praying hands): a flock of violet morning birds passes high at the right and, for a moment (about 165.5), stands in its shape. |
| 2:51 to 2:57 | breath | The words loosen and rise into **star 7**; violet hearts drift up from the words and from the two young men. **Star 7 lights at 2:57** (flare, then steady). |
| 2:57.35 to 3:08 | final fanfare | Torches lift; their flames rise as sparks to the arch. The music fades from 3:03. |
| 3:08 to 3:23 | calm hold | Calm radiant gold morning (the agreed hand-off colours: sky top #173A74, middle #8C7282, horizon #FFC47C), still lake, stars 9 and 7 lit, the people quietly present, dust drifting: gently alive, never black. Signature on. |

## The arch

- Start: **no star lit** (nine seeds drawn at 0:10.6).
- 0:58 **star 9 Compliment** lights; 2:57 **star 7 Encouragement** lights. Arch numbered left to right in campaign order (1 Greeting ... 9 Compliment).
- End: **9 and 7 lit**, steady, seven dim seeds. Never any other star.
- Colours: the website colours lifted 35 percent toward white so the deep Compliment navy still reads as a lit star.

## Hand-offs

- Before: song 01 is the first song of the night (item 1 is the existing sing-along video). It opens on its own starry lake with the lockup.
- To song 02 (design 01 section "Handing off to song 02", song 02 v2 TIMELINE): 01 ends on the radiant gold morning with 9 and 7 lit; song 02 opens in these gold morning colours with the arch fixed and darkens to its winter night. Signature in the top left in both.

## Owner and design decisions kept from the approved first-run timeline

Compliment acted by two young women; Encouragement by two young men (one helps the other rise, same gender); the three fragments only ("like a torch", "dew of the dawn", "Arise"); Heavenly Mother only from behind; no heavenly city.

## What changed from the first run (version 2)

1. 60 fps, live length 188.0 s plus a 15 s hold (203.0 s).
2. The opening lockup is readable from frame 0 for 7 s and then becomes the signature (the constellation title is gone).
3. Signature in the top left from 8.8 s to the last frame, the same layout as the other songs' version 2.
4. Morning people (after 2:27) deeper gold, less white, and bigger (camera closer: about 8 m instead of 12 m).
5. Compliment and Encouragement words a little narrower and lower, so they keep more than 40 px clear of the signature; they rise to their real arch stars.
6. The 1:40 peak is a warm gold bloom on a visible scene (haze and the peak flash cut by half, no pink-white).
7. Hearts drift off both expressions; both expression symbols appear in the world.
8. Bottom third calm: no reflections of people, torches, comets or hearts in the lake, the lake ring at 1:39 removed, motes calmed low in the frame.

## ACTING plan

| Expression | Acted by | Look | What they do | Framing |
|---|---|---|---|---|
| Compliment (9) | two young women (w1, w2) | warm gold glitter, garments of light (dresses) | 38.2 on: w1 turns to her friend and speaks with an open, explaining hand; 45.5 to 53.5 she applauds softly (gentle claps at chest height). w2 lays her hand on her heart and nods slowly as the words warm her. Four friends stand a little apart, swaying gently. | wide, eye level, the pair centred about 8.5 m away below the words; whole figures about a quarter of the frame high |
| Encouragement (7) | two young men (helper, tired) | warm deep gold glitter, tunics of light | One has sunk to one knee, worn out; his friend lays a hand on his shoulder (158 to 163.2, kneeling with a hand on the shoulder, PHASEB 6), then offers his hand and helps him rise (164.6 to 166.6); they stand side by side, torches lit. Four companions (two women, two men) stand round them with torches low, then lifted. | the camera closer than in the first run (about 8 m), the pair centred below the words |

Movement: the refined gestures of Claude Final v1 (master_acting), eased, natural hands; no touch between people of different genders.
