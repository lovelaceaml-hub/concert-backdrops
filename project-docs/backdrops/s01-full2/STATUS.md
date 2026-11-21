# Status 01: All You Stars of Zion, backdrop version 2

| Field | Value |
|---|---|
| Stage video | delivered 2026-11-19 (version 2, supersedes the first run) |
| Live length | 3:08 = 188.0 s (reference 187.97 s, within 1 s, used as is) |
| Video length | 203.0 s = 188.0 s of music + 15 s calm hold; 12,180 frames, 1920x1080, 60 fps |
| Stars lit at start | none (nine dim seeds, drawn at 0:10.6) |
| Stars lit at end | 9 Compliment (lit 0:58) and 7 Encouragement (lit 2:57) |
| Opening frame | starry night lake, navy and violet, gold morning star on the horizon; the concert lockup whole from frame 0: logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, All You Stars of Zion |
| Closing frame | radiant gold morning (sky #173A74 / #8C7282 / #FFC47C), sun low at the centre, still lake, the pair and four companions with torches, tree of light at the left, stars 9 and 7 lit, signature top left |
| Expressions | Compliment readable 0:42 to 0:52 (two young women, applause); Encouragement readable 2:41 to 2:51 (two young men, a hand on the shoulder of one kneeling, then helped up) |
| Fragments | "like a torch" 1:02 to 1:07; "dew of the dawn" 1:57 to 2:02; "Arise" 2:27.8 to 2:31.8 |
| Branch | backdrop2/s01-full (code tools/s01_full2/, docs project-docs/backdrops/s01-full2/) |

## Deliveries (attached in the build session's chat; not in git)

| File | Bytes | SHA-256 |
|---|---|---|
| 01 All You Stars of Zion - Backdrop v2 - stage 1080p60.mp4 (silent, H.264 CRF 16, yuv420p, faststart) | 152,956,265 | b6b482a652591a481da23f1ee6b457f7cddd4cebfd2fbb8bf635fab143a26b1c |
| 01 All You Stars of Zion - Backdrop v2 - review 1080p60.mp4 (reference music untouched, AAC 320k, CRF 20) | 92,868,702 | f1e0dd40670655855888e1e51e3286707f806ee4e5cf2228e839e7edd19a1f03 |
| 01 All You Stars of Zion - Backdrop v2 - phone 720p60.mp4 (with music) | 18,922,337 | 11eb73f54faa9e30048006ebb6f55c248d3fbdbbb999585c60a0bc71723789d0 |

Contact sheet: Drive "Concert Backdrops - Songs/Status/01 backdrop v2 stills.jpg" (15 landmarks from the final render).

## Checks on the finished files

- All three: 203.000 s, 12,180 video frames, 60/1 fps, yuv420p; audio 203.000 s on review and phone.
- No black stretch (blackdetect), no frozen stretch of 0.3 s or more (freezedetect).
- Sync against the source recording at 0:07.11, 2:27.77 and 2:57.35: 0.0 ms offset each. The hold is silent.
- Signature present in every sample from 0:08.8 to the last frame (2 per second, 388 samples).
- First frame: the opening lockup whole. Last frame: the calm gold morning with the signature.

## Log

- 2026-11-18: version 2 started on the coordinator's go-ahead (Anthony: "Just do a new one"). Rule files in Drive read; the first run's code reused and fixed (see TIMELINE "What changed").
- 2026-11-18: four rounds of landmark stills; fixes: words kept clear of the signature, no reflections in the bottom third, ring removed, 1:40 peak a warm gold bloom, morning people deeper gold and bigger, morning sun moved below the words, symbol places, hearts.
- 2026-11-18 to 19: full render in this cloud session (8 ranges on 4 cores, about 1.6 s per frame); a container restart cost two ranges, re-rendered; the 0:07 brass flash changed to a small warm gold bloom after the motion strip showed a white haze behind the lockup (range 1 re-rendered).
- 2026-11-19: joined, checked, delivered.

## Still weak (honest)

- "Arise" reads as pale cream gold on the bright sunrise rather than deep gold; large and legible, but not as rich as the night words.
- At the 1:40 peak the people are small and far out on the lake (light carries that moment).
- In the calm hold the people are modest in size and soft; the hold is mostly sky, sun and the tree.
- Sections are timed to the reference recording (which is the live length); a rehearsal recording would confirm the hits.
