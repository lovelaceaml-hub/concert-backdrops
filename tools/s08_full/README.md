# Song 08 full backdrop (Out of Heaven, Favor From God)

One continuous 224.1 s video (music from 0, then 15 s calm hold), 30 fps, 1920x1080, in the approved Revision 3 look.

- `s08_full.py`: the song module (timeline tables `M` and `WT`, camera keys, words, point sets, people, world looks).
- `render.py`: stills and frame ranges on the pinned engine (run `tools/nine_colours_minor/prepare.py` first).
- `finish.sh`: joins the parts, adds the music padded with silence, makes the master and the share copy.

Setup and the recording are described in project-docs/backdrops/HANDOFF-FULL-BACKDROPS.md and project-docs/backdrops/s08-full/TIMELINE.md. The audio goes in work/s08_full/s08.mp3 and its features in work/s08_full/features.npz (`engine/analyze.py`); neither is committed. Render in the cloud only, never on the Mac, and never with the paid Render workflow without Anthony's OK.

    python tools/s08_full/render.py --stills 64,92 --scale .5
    python tools/s08_full/render.py --range 0 840 --out out/s08_full/parts/p0000.mp4   # 8 such parts, 4 at a time
    tools/s08_full/finish.sh out/s08_full/parts work/s08_full/s08.mp3 out/s08_full/final
