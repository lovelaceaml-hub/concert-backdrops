# 05 God Bless You!: full backdrop, version 2, timeline

Concert item 6, Sunday December 6, 4:30 PM, Las Vegas. Design: `project-docs/designs/05 God Bless You!.md` ("The Tree of Blessing"). Code: `tools/s05_full2/`. This version replaces the first run (`backdrop/s05-full`).

## Length (DESIGN-SYSTEM 4 and 9)

- Live length 2:39 = **159.0 s** (choir and orchestra). The music part of the stage video is exactly that, then a **15 s calm hold**: **174.0 s, 10,440 frames at 60 fps**, 1920x1080.
- Reference: the organisers' recording (Drive 1sc19zSxMPDEI5bxaaoiCVx7rndRY-F_D, M4A mono 48 kHz, SHA-256 dbfc1a9f...8781), 153.152 s. Never committed.
- The reference is 5.85 s shorter than the live length (more than 1 s), so it is conformed section by section. Nothing tells which sections the live choir takes slower, so **every section is scaled by the same factor K = 159.0 / 153.152 = 1.03818**; hits keep their proportional places. **This is an estimate until a rehearsal recording exists.** The review copy plays the reference stretched the same way (ffmpeg atempo, pitch kept).
- How the code does it: the scene is authored on reference time r; the frame at stage time t shows r = t / K (`tools/s05_full2/timing.py`). Stage times below are K x reference times.
- The sung guide ("05 God Bless You! (sung guide, for lyric timing).mp3", 2:22) could not be downloaded here (not shared by link; the Drive connector returns text only). Lyric lines are placed by the measured structure, as in the first run. Not yet confirmed by ear.

## Measurements (this session, on the reference)

- `engine/analyze.py` (pinned engine d928ff9): beat grid, onsets, loudness bands into `work/s05_full2/features.npz` (not committed); the picture's sky and lights react to it.
- Loudness (librosa RMS, 3 s means, dB): soft intro 0 to 6; swell 6 to 12; soft verse 1 opening 15 to 35; full 36 to 54 (peaks 45 to 53); soft 54 to 63; full 69; soft 75 to 106; full 108 to 125 (peaks 114 to 123); full 138; last swell 147 to 150; sound ends about 151.5, silence by 152.
- Strongest onsets: 51.43, 55.54, 60.84, 67.71, 70.84, 90.84, **111.48**, 130.8, 132.7, **137.67** s.
- Repeat (chroma correlation of 16 to 52 s against later): lag 70 s scores 0.63, lags 66, 68, 72, 74 score 0.03 to 0.12. **Verse 2 is verse 1's music 70 s later** (verse 1 from about 13.5 s, verse 2 from about 83.5 s).
- Sync check points used after the render (reference, then stage): hit 51.43 s = **53.39 s**; hit 111.48 s = **115.74 s**; hit 137.67 s = **142.93 s**.

## Sections (stage time)

| Stage time | Reference | Music | What is on screen |
|---|---|---|---|
| 0:00 to 0:14.0 | 0 to 13.5 | intro, swell | Opening card (logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, God Bless You!) whole from frame 0 to 7.4 s, lifts away by 9.0 s. Song 04's thawed apricot late morning warms into the spring afternoon; a small warm seed of light drifts to the shore. Signature fades in 8.4 to 9.8 s and stays to the last frame. |
| 0:14.0 to 0:25.3 | 13.5 to 24.4 | verse 1, line 1 | The seed touches the shore: a wave of peace, a sprout. The one who prays (a young man) forms by the tree; the brother stands alone on the far left, bowed under a soft grey load. Fragment "God bless you!" (petals). |
| 0:25.3 to 0:39.0 | 24.4 to 37.6 | line 2 | **ENCOURAGEMENT**: he kneels and prays; violet light crosses the water to the brother's shoulders; praying hands traced by violet fireflies in the sky above the brother; violet hearts from the praying hands. Words gather into star 7, which flares (relight). |
| 0:39.0 to 0:57.3 | 37.6 to 55.2 | line 3, full | The brother straightens and shines; the sapling grows. Fragment "Father's great love" (a shaft of sun writes it). |
| 0:57.3 to 1:12.3 | 55.2 to 69.6 | line 4 | **CONSIDERATION**: he crosses on stepping stones of light and offers his hand; the two men clasp hands; the load blows away as light; the symbol (two hands holding a heart) in rose petals; rose hearts. Words gather into star 8 (lit for the first time). |
| 1:12.3 to 1:26.8 | 69.6 to 83.6 | lines 5 and 6 | The two walk back to the tree; the brother lays his hand on it and it blossoms. Fragment "good fruit" (golden fruit ripen into the letters). The sister appears sitting alone on the far right shore. |
| 1:26.8 to 1:52.3 | 83.6 to 108.2 | verse 2, lines 1 and 2 | A young woman forms by the tree. The brother walks round behind the tree to his sister and kneels beside her. **ENCOURAGEMENT** again: all three pray; violet light comes down from star 7 through their hands to her; one light draws the praying hands above her. Star 7 relights. |
| 1:52.3 to 2:10.8 | 108.2 to 125.8 | line 3, "In her tender voice" | **RESPECT** (provisional, DESIGN-SYSTEM 12a.2): the brother, kneeling at her side, turns and leans in to listen; her voice rises as soft puffs of light toward him; a small flock of birds makes the hand cupped at the ear; indigo hearts. Words gather into star 6 (lit for the first time). |
| 2:10.8 to 2:32.0 | 125.8 to 146.4 | line 4 | **CONSIDERATION** again: the young woman crosses on stepping stones, offers her hand and helps the sister up; the symbol traced in rose sparks; rose hearts. Star 8 relights. The four walk back to the tree; the fruits ripen in the nine colours. |
| 2:32.0 to 2:39.0 | 146.4 to 153.15 | last swell, end | Climax: the sun breaks through the haze, a warm gold bloom on the visible scene, a storm of petals, everyone opens their arms, the far shores fill with countless small lights, a road of light rises from the tree toward the arch. |
| 2:39.0 to 2:54.0 | 153.15 to 167.6 | the calm hold (15 s) | Warm late afternoon, calm mirror, the four stand with hands softly cupped; seeds of light drift from the tree to the water (song 06's grain). Fragment "God bless you!" rises from the tree as seeds of light (2:44.0 to 2:50.7), then the scene rests, gently alive, with the signature, to the last frame. |

## Words on screen (stage time; each read with nothing competing)

| Moment | Arrives | Readable | Leaves by |
|---|---|---|---|
| "God bless you!" (fragment) | 16.0 | 18.1 to 22.4 | 24.7 (petals blow away) |
| ENCOURAGEMENT | 25.7 | **27.4 to 36.8 (9.3 s)** | 38.8 (gathers into star 7) |
| "Father's great love" (fragment) | 45.1 | 47.1 to 53.2 | 55.2 (rises as light) |
| CONSIDERATION | 57.9 | **59.6 to 68.9 (9.3 s)** | 71.0 (gathers into star 8) |
| "good fruit" (fragment) | 79.3 | 81.0 to 85.5 | 87.4 (falls as petals) |
| ENCOURAGEMENT | 98.0 | **99.7 to 109.0 (9.3 s)** | 111.1 (star 7) |
| RESPECT | 113.6 | **115.2 to 124.2 (8.9 s)** | 126.2 (star 6) |
| CONSIDERATION | 131.4 | **132.9 to 142.0 (9.1 s)** | 144.1 (star 8) |
| "God bless you!" (fragment, hold) | 161.7 | 164.0 to 170.7 | 172.5 (fades) |

Only one moment of words is on screen at a time (`words2d.Words.check()`). Exact expression wording comes from `engine/p3d/words.py` EXPRESSIONS at the approved tag, never retyped. Words are navy #1f2a6b with a soft white glow (bright sky), Cormorant Garamond italic phrases under a capsule label in the expression's website colour, block centred 0.38 of the frame height down; fragments 0.375 down.

## The arch of nine lights

- Lit at the start: **3 Apology, 4 Inclusiveness, 7 Encouragement, 9 Compliment** (song 04's end).
- 7 relights at 0:38.8 and 1:51.1 (brief flare, one new ring); **8 Consideration lit at 1:11.0**, relights at 2:24.1; **6 Respect lit at 2:06.2**.
- Lit at the end: **3, 4, 6, 7, 8, 9** (song 06's start, which relights 4 and lights 5).
- The arch spans the top of the sky (1080p: ends about (354, 369) and (1579, 363), top about (960, 206)). Like the sky it keeps its place while the camera drifts, so no light ever crosses the signature or a word (geometry searched against both boxes). Light colours are the website colours; Respect and Compliment use their lighter glow so they read on a bright sky.

## Hand-offs (design and Designs/CONCERT-OVERVIEW.md)

- From song 04: opens on 04's thawed apricot late morning over the mirror lake, arch 3, 4, 7, 9 lit; a small warm seed of light drifts to the shore.
- To song 06: closes on a warm late afternoon mirror (sky toward #3a6cb0 top, #9ab4d4 middle, #efd3a0 horizon), petals and seeds of light drifting, arch 3, 4, 6, 7, 8, 9 lit; one seed of light on the water becomes 06's grain.

## Changes from the design and the first run (and why)

- Timed to the live length 159.0 s plus 15 s hold at 60 fps (the first run used the 153.15 s reference at 30 fps).
- **Respect is now placed** at "In her tender voice" as the brief requires (provisional exception, DESIGN-SYSTEM 12a.2); the first run left star 6 dark. Acted without touch (brother and sister): he kneels beside her and leans in to listen.
- Casting for the touch rule: verse 1 a young man helps his brother; verse 2 a young woman helps the sister up. Brother and sister never touch.
- No hands of Heavenly Mother (owner's rule, no hands at the end); the fruits ripen in the warm light.
- No two expressions together in the hold (one expression at a time); the hold carries the fragment "God bless you!" instead.
- Bright spring afternoon look (DESIGN-SYSTEM 6, row 05) instead of the first run's dusky blue; navy words. No comets.
- People: warm gold glitter people, each grain also painted gold with a gentle warm light inside the shape, so they stay whole and radiant on the bright sky.
- The bottom third is calmed in the 2D layer (soft water, highlights held down) so performers stand in front of a quiet picture.
