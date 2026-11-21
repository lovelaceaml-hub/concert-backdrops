# Song 04 I'm Sorry, Please Forgive Me: status (full backdrop, version 2)

Board fields (for Status/04.md in Drive; the coordinator copies them):

- **Live length:** 3:40 (220.0 s). Stage video 3:55.0 (220.0 s of music, then a 15 s calm hold), 14,100 frames, 1920x1080, 60 fps.
- **Stars lit at start:** 3, 7, 9 (star 7 with two thin rings from songs 02 and 03).
- **In this song:** relights 3 Apology at 0:39.9 (a brief flare and one new thin ring); lights 4 Inclusiveness for the first time at 1:08.9 (the line between 3 and 4 grows).
- **Stars lit at end:** 3, 4, 7, 9.
- **Opening frame:** the opening lockup (logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, "I'm Sorry, Please Forgive Me") on the calm pale sky over a frozen pearl lake, a low cold sun at the left in haze, song 03's rose petals faintly frozen in the ice, arch 3, 7, 9.
- **Closing frame:** the thawed lake in warm apricot morning light, low bright sun, a thin gold path across the water toward the sun, one small warm light at the centre sending a gentle ripple, no figures, camera level and centred a little above the water, arch 3, 4, 7, 9, the signature top left.
- **Expressions:** APOLOGY reads 0:29.0 to 0:38.6; INCLUSIVENESS reads 0:58.8 to 1:07.8. No Gratitude words ("I thank you" acted only).
- **Fragments:** "truly humbled", "opened her heart", "with compassion", "one in your love".
- **Branch / code:** backdrop2/s04-full, tools/s04_full2/; docs project-docs/backdrops/s04-full2/ (TIMELINE, CUES, CHECKLIST, this file).

## Log

- 2026-11-18: version 2 started on the binding brief ("Just do a new one"). Read the Drive rule files (via a helper), the campaign pages, the design and the first run.
- 2026-11-18: reference audio fetched from the private Artifact page, SHA-256 verified; conformed 219.435 s to 220.0 s (atempo 0.997430, pitch kept); measured (analyze.py, loudness, onsets); a word level transcript placed every lyric moment (kept in work/, not committed). Found this choir version sings verse 1 (both sisters), an instrumental interlude and verse 3, not the design's estimated verse 2.
- 2026-11-18: built the scene on the approved Revision 3 tag: pale frozen morning to apricot thaw, the two sisters of gold light, Apology and Inclusiveness with the arch, four fragments, the opening lockup and the top left signature. Stills reviewed in six rounds (people size and contrast, bottom third, arch, washed out warm sky fixed).
- 2026-11-18: full render in this cloud session, 16 parts on 4 cores (about 1 h 40 min; the container restarted once during the last part, which was re-rendered in four pieces). 14,100 frames joined.
- 2026-11-19: encoded and checked (export.py); contact sheet "04 backdrop v2 stills.jpg" uploaded as a new file to Drive Status; the three videos attached in the session chat for the coordinator.
- 2026-11-19, fix 1 (coordinator notes): (1) bottom third: every particle set, including the world's dust, floats and lanterns, now passes Clear() (nothing below 0.34 of the height, full only from 0.40, no particle reflections), and the near water mirrors less of the sun's glow, so the sparkles at 0:20, 0:34, 0:45, 1:03, 1:55, 2:45, 3:12 and the pink glow at the bottom 2:45 to 3:12 are gone; (2) the gold path, the dividing line, footprints and the closing light now also pass Clear() with a wider box padding, and the verse 1 camera sits a little further back and lower so the sisters stay below the words (0:34, 0:45, 0:51, 1:03); (3) the second half sky and water deepened (warmer apricot, rose and deeper blue water). The fixes touch the whole length (world particle sets and colours), so all 16 parts were re-rendered in this cloud session (about 1 h 30 min), rejoined (14,100 frames), encoded and checked again. New contact sheet "04 backdrop v2 stills fix1.jpg" uploaded as a new file to Drive Status; the first sheet is kept.

## Delivered files (fix 1, not in git)

| File | Size | SHA-256 |
|---|---|---|
| 04 I'm Sorry, Please Forgive Me - Backdrop v2 - stage 1080p60.mp4 (silent, CRF 16) | 120.0 MB | 39cc492e64df84d9de4eb054199bf678ff6dd9bbc13fcb8d88b0f0ee36814666 |
| 04 I'm Sorry, Please Forgive Me - Backdrop v2 - review 1080p60.mp4 (music, AAC 320k, CRF 20) | 73.8 MB | 059e3a38a94bc20b82c8aecbed043994d3164f6d0238f4464a68c84a3480e5b7 |
| 04 I'm Sorry, Please Forgive Me - Backdrop v2 - phone 720p60.mp4 (music) | 24.1 MB | 66cc4afcfa4bf242b37024d20f3ce99511672fefc5486339ae2a99e9caaf6407 |

The first delivery (before fix 1) had stage e83dcbc8..., review edf6aeca..., phone 38a46615...; those files are replaced by the ones above.

## Checks (export.py, fix 1)

- All three: 14,100 frames, 60 fps, 235.000 s; stage and review 1920x1080, phone 1280x720; yuv420p.
- No near black and no near white frames (frame means 122 to 193 of 255); no repeated frames; no frozen second.
- Signature present on every frame after 0:11 (its letters never deviate more than 21 of 255 from their median picture; the largest change is the sky warming behind it, nothing crosses it).
- Music in sync at 0:27.4, 1:25.0 and 2:42.0 (0 ms offset in the review and phone files).
- First frame: the opening lockup on the pale sky. Last frame: the calm hold with the signature.

## Known weaknesses

- On the deeper apricot sky of the second half, the small pink "HEALING CONCERT · LAS VEGAS" line of the signature has less contrast than on the pale sky (the date line stays strong navy).
- The gold path passes close beside the people in the last part (it never enters a reading box).

## Where the Drive files and the brief differ (read 2026-11-18)

The Drive rule files are older (DESIGN-SYSTEM.md and PHASEB modified 2026-11-17) than the brief's owner decisions of 2026-11-18, so the brief was followed where they differ: 60 fps (DESIGN-SYSTEM 4 still says 30), live length plus a 15 s hold (the design planned about 80 s), the five-line signature in the top left (PHASEB has no song title in it), the website colours (PHASEB Update 9, newer than DESIGN-SYSTEM's older palette), and the campaign logo in the lockup and signature (PHASEB Update 9; DESIGN-SYSTEM 10 still says no logos).
