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
- 2026-11-19: encoded and checked (export.py, checks below); contact sheet "04 backdrop v2 stills.jpg" uploaded as a new file to Drive Status; the three videos attached in the session chat for the coordinator.

## Delivered files (not in git)

| File | Size | SHA-256 |
|---|---|---|
| 04 I'm Sorry, Please Forgive Me - Backdrop v2 - stage 1080p60.mp4 (silent, CRF 16) | 119.0 MB | e83dcbc804cd7b04e0c446881c05e5203e3d48685f0d3d31d7cdd7399e621250 |
| 04 I'm Sorry, Please Forgive Me - Backdrop v2 - review 1080p60.mp4 (music, AAC 320k, CRF 20) | 73.5 MB | edf6aeca1d0cd336207f15b1d4ee35b699aef85961884af880382b50fcb1a6e4 |
| 04 I'm Sorry, Please Forgive Me - Backdrop v2 - phone 720p60.mp4 (music) | 24.2 MB | 38a4661522811b940f0b20ebc03d541d8c3d0ebb4b1a8e8a2ab15e5d1474b6e8 |

## Checks (export.py)

- All three: 14,100 frames, 60 fps, 235.000 s; stage and review 1920x1080, phone 1280x720; yuv420p.
- No near black and no near white frames (frame means 153 to 193 of 255); no repeated frames; no frozen second.
- Signature present on every frame after 0:11 (its letters never deviate more than 15 of 255 from their median picture).
- Music in sync at 0:27.4, 1:25.0 and 2:42.0 (0 ms offset in the review and phone files against the conformed music; the picture runs on the same 60 fps clock as the music).
- First frame: the opening lockup on the pale sky. Last frame: the calm hold with the signature.

## Where the Drive files and the brief differ (read 2026-11-18)

The Drive rule files are older (DESIGN-SYSTEM.md and PHASEB modified 2026-11-17) than the brief's owner decisions of 2026-11-18, so the brief was followed where they differ: 60 fps (DESIGN-SYSTEM 4 still says 30), live length plus a 15 s hold (the design planned about 80 s), the five-line signature in the top left (PHASEB has no song title in it), the website colours (PHASEB Update 9, newer than DESIGN-SYSTEM's older palette), and the campaign logo in the lockup and signature (PHASEB Update 9; DESIGN-SYSTEM 10 still says no logos).
