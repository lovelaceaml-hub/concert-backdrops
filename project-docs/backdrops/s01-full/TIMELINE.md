# 01 All You Stars of Zion: full-length backdrop (pilot)

Status: stills for Anthony's review (2026-11-18). No full render yet; it waits for his OK.

Stills (1280x720, 12 landmarks plus 2 extras, rendered in the cloud session, checked at full size): Drive "Videos/01 All You Stars of Zion/backdrop stills", https://drive.google.com/drive/folders/1jkvApQ43Jdf_IkLig0fr7UjuuI4fcPRH

Open points for review: the people's reflections reach into the bottom third during the verse and the morning (their feet sit just below it); the light ring at the 1:40 peak crosses the lower lake for a few seconds; the heavenly city is left out as decided.

## The audio (kept in Drive only)

Owner decision 2026-11-18: the song stays in Drive only and is never committed to this repository. It is the church's brass ensemble version (the same performance as youtu.be/YuBYZDgmf0I).

Download it into `work/s01_full/` (ignored by git) before preparing:

```sh
mkdir -p work/s01_full
curl -L -o work/s01_full/s01-ensemble.mp3 "https://drive.usercontent.google.com/download?id=1wmWrkUIuIU_zE1Hogp_hPUFYBH0J5YJR&export=download&confirm=t"
```

SHA-256 `2ef650dcf9b2fab141c72a2ce9a3301265326d2b6fe2ec807dcbe3dddd177a01` (checked by `s01_prepare.py`).

Measurements (`engine/analyze.py`, pinned engine d928ff9):

- Length 187.97 s. Key B-flat major (A# major in the analyzer, 0.96 confidence).
- Beat grid 0.418 s (the analyzer reports 143.6; the felt pulse is about 99 BPM, as measured before).
- Natural fade 3:03 to 3:08 (loudness falls from about -19 dB to -38 dB in the last 4 s).
- Loud hits refined to the nearest measured onset: 7.11, 30.60, 77.18, 87.33, 106.39, 125.04, 131.54, 141.48, 147.77 (largest), 177.35.
- Loudest stretch 1:39 to 1:43. Quiet interlude about 1:53 to 2:05 (down to -35 dB).
- Structural segment boundaries (k=8): 0.0, 31.0, 51.7, 61.4, 110.0, 143.3, 148.2, 170.9.

## Approved timeline (owner: "Approve as proposed", 2026-11-18)

One continuous video, 30 fps, 1920x1080, 203 s (187.97 s of music plus a 15 s calm hold).

| Time | What happens |
|---|---|
| 0:00 to 0:07 | Soft opening: luminous starry lake, warm, never dark; gold morning star on the horizon; nine dim seeds of the arch. |
| 0:07.1 | First big brass hit: the song title forms as a constellation; the arch of nine lights draws across the sky at about 0:11. |
| 0:19.5 to 0:25 | Soft: the title settles into the small signature; the nine coloured comets begin to fall. |
| 0:25.5 to 0:55 | Verse: the comets land on the shore as gold glitter people; the morning star flares on the 0:30.6 lift. COMPLIMENT acted from 0:38 by two young women; words fully readable 0:42 to 0:52. |
| 0:55 to 0:58 | Breath: the lake stills to a mirror; Compliment's star lights in the arch. |
| 0:58 to 1:24 | Chorus: "like a torch"; the flame passes hand to hand; torches lift; beams of glory lean toward Heavenly Mother, far on the shore and seen only from behind (never a face); the sky flushes rose gold. |
| 1:24 to 1:27 | Breath: light falls gently onto every torch. |
| 1:27 to 1:53 | Chorus again, peak 1:39 to 1:43: the young people walk out on the lake; light spreads over the whole world; a golden net of light lands on the peak. |
| 1:53 to 2:05 | Quiet interlude: blue hour, close on the shore, "dew of the dawn" written in light. |
| 2:05 to 2:27 | The tree of life grows from the dew; blossoms drift on the 2:21 hit. |
| 2:27.8 | The sun rises and "Arise" stands up out of the lake. |
| 2:36 to 2:55 | Final section: ENCOURAGEMENT acted, one young man helps another rise (same gender); words fully readable 2:41 to 2:52. |
| 2:55 to 2:57 | Breath: the words go to Encouragement's star in the arch. |
| 2:57 to 3:08 | Final fanfare, fade from 3:03: torch flames lift as sparks to the arch. |
| 3:08 to 3:23 | Silence: calm radiant morning hold, two lit stars, still lake, gently alive. Never black. |

## Other owner decisions

- Look: the approved Nine Colours Revision 3 (warm gold glitter people, cream Cormorant serif phrases with coloured capsule labels, nine coloured comets, warm heavenly light) applied to the song design.
- Expression colours are the website colours: Compliment #364E96, Encouragement #9E6AF6. Exact wording from the campaign.
- The faint heavenly city is left out.
- Backdrop rules: calmer camera than the promo (performers stand in front), calm bottom third, expression phrases readable from the back of the hall, small signature, no lyrics on screen beyond the three short fragments ("like a torch", "dew of the dawn", "Arise").
- Every touching moment is same gender (parent and child excepted); refined natural movement; no realistic faces.
- Stars at the end: 9 Compliment and 7 Encouragement lit (arch numbered left to right in campaign order).

## How it is built

- Branch `backdrop/s01-full`, from tag `film10-revision3-approved-2026-11-16`. The approved promo files are not changed.
- Song file: `tools/backdrop_s01/songs/s01_full.py`, read into the pinned Film 10 engine (d928ff9) with Claude Final v1 words, bodies and light effects (f43f451), exactly as Revision 3 does.
- `tools/backdrop_s01/s01_prepare.py`: restores the pinned engines, checks the audio, measures it, makes the score (song plus 15 s of silence).
- `tools/backdrop_s01/s01_render.py`: stills or frame ranges, 30 fps.

```sh
python tools/backdrop_s01/s01_prepare.py
python tools/backdrop_s01/s01_render.py --stills 3,12,22 --scale 0.5 --outdir <dir outside the repo>
```

Render only in the cloud. Never commit the song, stills, frames or videos.

## Next (after Anthony approves the stills)

The full 30 fps render, split across parallel cloud machines (`--range` parts), joined with the score, checked for length (203 s, 6,090 frames), sync and frames, then delivered to Drive "Videos/01 All You Stars of Zion/". The GitHub "Render" workflow or anything paid is not dispatched without his explicit OK.
