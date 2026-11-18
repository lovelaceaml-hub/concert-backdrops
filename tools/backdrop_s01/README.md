# Song 01 full backdrop (pilot)

All You Stars of Zion, full length (203 s, 30 fps, 1920x1080), in the approved Nine Colours Revision 3 look.
The approved timeline, owner decisions and audio measurements are in
`project-docs/backdrops/s01-full/TIMELINE.md`.

- `s01_prepare.py`: restores the pinned engines (through `tools/nine_colours_minor/prepare.py`), checks the
  song's checksum, measures it with `engine/analyze.py`, makes the score with a 15 s silent hold.
- `s01_render.py`: stills (`--stills`) or a frame range (`--range A B --out part.mp4`), at 30 fps.
- `songs/s01_full.py`: the song file (scenes, people, words, light, camera), read into the pinned engine.

The song is kept in Drive only; download it to `work/s01_full/s01-ensemble.mp3` (see TIMELINE.md).
Render in the cloud only. Never commit the song, stills, frames or videos. The approved promo files in
`tools/nine_colours_minor/` are used, not changed.
