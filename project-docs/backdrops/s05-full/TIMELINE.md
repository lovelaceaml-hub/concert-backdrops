# 05 God Bless You!: full backdrop timeline

Concert item 6, Sunday December 6. Organisers' note: "This song shows examples of how we can practice words of Mother's love. (Number 7: Earnestly, with my hands together, I pray for him with all my heart.) (Number 8: how can I help my brother/sister?)". So the two expressions are **Encouragement** (7, prayer) and **Consideration** (8, a helping hand).

## The audio

- Source: the organisers' reference (Drive id 1sc19zSxMPDEI5bxaaoiCVx7rndRY-F_D, M4A, mono 48 kHz), SHA-256 dbfc1a9f5b8118ab76bcabf16d9b0e30bfe07bea140d4405ff4087b6d2ea8781. Never committed.
- Length 153.15 s (2:33.15). Sound ends about 151.5 s (a quick fade to silence by 152).
- Video: 153.15 s of music, then a 15 s calm hold: 168.17 s, 5045 frames at 30 fps.

## How it was measured

- `engine/analyze.py` (pinned engine d928ff9): 123 bpm beat grid, onsets, loudness bands (kept in `work/s05_full/features.npz`, not committed).
- Half-second loudness curve (librosa RMS).
- Repeat analysis (chroma cross-correlation): **16 to 52 s repeats almost exactly at +70 s (86 to 122 s)**, similarity 0.94 to 0.99. So the two verses are the same music 70 s apart: verse 1 (brother) starts about 13.5 s, verse 2 (sister) about 83.5 s. After 52 s / 122 s the two halves part (verse 1 winds down, verse 2 builds to the ending).
- Lyric lines are placed by that structure and the loudness shape, matched against the ver.3 recording's line lengths in the design doc (verse 1 there was 73 s; here each verse is about 70 s). Not confirmed by ear against the sung guide (it could not be downloaded here); the two quiet dips before each verse's line 3 (35.5 s and 105.5 s) and the soft stretch before each line 4 (55.5 s and 126.5 s) anchor the expression moments.

| Time | Loudness | Music | Lyric line (estimated) |
|---|---|---|---|
| 0:00 to 0:07.5 | soft | short intro | |
| 0:07.5 to 0:13.5 | full | intro swell | |
| 0:13.5 to 0:25 | soft | verse 1 begins | line 1: the blessing for my brother |
| 0:25 to 0:36 | soft (dip 35 to 36) | | line 2: "Earnestly, with my hands together..." |
| 0:36.5 to 0:55.5 | full, peaks 48 and 51.6 | | line 3: his bright smiling face, Father's love |
| 0:55.5 to 1:03 | soft | breath | line 4: "How can I help my brother" |
| 1:03 to 1:15 | rising, full 1:08.5 | | line 5: Heavenly Father, fill him with Your love |
| 1:15 to 1:23.5 | soft | | line 6: let him bear good fruit |
| 1:23.5 to 1:35.5 | soft | verse 2 begins | line 1: the blessing for my sister |
| 1:35.5 to 1:46 | soft (dip 1:45 to 1:46) | | line 2: prayer for her |
| 1:46.5 to 2:06.5 | full, peaks 1:56 to 1:58 and 2:01.5 to 2:06 | | line 3: her tender voice, Mother's kind love |
| 2:06.5 to 2:16 | soft | breath | line 4: "How can I help my sister" |
| 2:16 to 2:22 | full, peak 2:20.5 | | line 5: Heavenly Mother, Jerusalem |
| 2:22 to 2:31.5 | full, last swell 2:28 to 2:30 | ending | line 6: let her bear good fruit |
| 2:31.5 to 2:33.15 | fades out | end | |

Sync check points used after the render: the swell at 0:07.5 to 0:08, the hit at 0:51.5, the hit at 1:58.0 and the last swell at 2:28.

## The picture, second by second

Look: the approved Revision 3 style (warm gold glitter people, cream Cormorant serif phrases with coloured capsule labels, the arch of nine lights) applied to the song's design: a golden spring afternoon over a mirror lake (songs 04, 05, 06 pass through one day: morning, afternoon, evening). Calm camera: slow drifts only, bottom third water and reflection.

| Song time | What happens | Words on screen |
|---|---|---|
| 0:00 to 0:13.5 | Song 04's hand-off: warm late morning, a small warm light on the water drifts to the shore and becomes the seed of hope. The light warms to a hazy afternoon. | "God Bless You!" (song title) 0:03.6 to 0:10.2 |
| 0:13.6 | The seed touches the shore: one wave of peace crosses the lake; a mound of golden grass light appears; a sprout. | |
| 0:14 to 0:25 | The one who prays (a young man) forms beside the tree; the brother forms alone on the far left, bowed under a soft grey load. | "God bless you!" (fragment, falls as light) 0:17.4 to 0:21.6 |
| 0:24.4 to 0:37.6 | He kneels and prays; the lake becomes a mirror; violet light crosses the water and rests on the brother's shoulders like a cloak; he lifts his head. | **ENCOURAGEMENT** readable 0:26.4 to 0:35.4, then gathers into star 7, which flares at 0:37.6 |
| 0:37.6 to 0:55 | Wave of peace from the brother. He straightens; his glow warms to bright gold; the sapling grows to a person's height. | "Father's great love" (fragment) 0:45.4 to 0:51.2 |
| 0:55.2 to 1:09 | The one who prays rises, walks out on stepping stones of light (one per step), offers his open hand; the two clasp hands; the load breaks into sparks and blows away as light. | **CONSIDERATION** readable 0:57.4 to 1:06.4, gathers into star 8 (lit for the first time) at 1:08.6 |
| 1:08.8 | Wave of peace. | |
| 1:09.6 to 1:17 | The two walk back to the tree. | |
| 1:16.8 to 1:23.5 | The brother lays his hand on the young tree; it blossoms. | "good fruit" (fragment) 1:18.0 to 1:22.4 |
| 1:19 | The sister appears, sitting alone on the far right shore, knees drawn up, worn out. | |
| 1:23.6 to 1:35.5 | A young woman forms beside the tree. The afternoon brightens. The brother reaches toward his sister; a scatter of gold drifts across to her. | |
| 1:34.6 to 1:47.4 | All three kneel and pray; violet light comes down from star 7 through their hands and crosses to the sister like a shawl; she lifts her head. | **ENCOURAGEMENT** readable 1:36.0 to 1:45.6, back to star 7 at 1:47.4 |
| 1:47.2 to 2:06 | Wave of peace; the sister rises. Her tender voice as soft halos of light (light only). Petals in the air; fruits begin to swell. | |
| 2:05.8 to 2:19.6 | They rise; the young woman crosses on stepping stones and the two women clasp hands. | **CONSIDERATION** readable 2:08.0 to 2:17.0, back to star 8 at 2:19.0 |
| 2:19.2 to 2:28 | Wave of peace; the two women walk back to the tree; the fruits ripen into the nine colours. | |
| 2:26.4 to 2:33 | Climax: the sun breaks through the haze, rays, a storm of petals, everyone opens their arms, the far shores fill with countless small lights of people, a road of light rises from the tree toward the arch. | none (the picture is the answer) |
| 2:33.2 to 2:48.2 | The hold: warm late afternoon, calm mirror, the four stand together with hands softly cupped; seeds of light drift down to rest on the water (song 06's grain). | **ENCOURAGEMENT** above and **CONSIDERATION** below, together, from 2:35.6 to the last frame |

Arch of nine lights: lit at the start 3 Apology, 4 Inclusiveness, 7 Encouragement, 9 Compliment; 8 Consideration lit at 1:08.6; 7 flares again at 1:47.4 and 8 at 2:19.0. Lit at the end: 3, 4, 7, 8, 9.

## Changes from the design doc (and why)

- **Respect is not placed.** The organisers name only expressions 7 and 8 for this song, and the design itself called the Respect placement an exception awaiting Anthony. The sister's tender voice is shown as light only. Star 6 therefore stays dark at the end (the design's hand-off to song 06 had 6 lit).
- **Casting for the touch rule.** Every touch is between two people of the same gender: in verse 1 a young man helps his brother; in verse 2 a young woman takes the sister's hand, while the two men pray beside her without touching.
- **No Heavenly Mother hands.** The owner's later rule (no hands at the end; hands found "extremely weird") overrides the design's sheltering hands. The fruits ripen in the warm light instead.
- **No fragment 5** ("God bless you!" to the hall) in the hold: the 15 s hold carries the two expressions instead, to be read 12 s or more.
- **No little scenes inside the stepping stones** (an elder's bag, shared papers): too small to read from the back of a hall; the stones are plain rose gold light.
