# Song 08 backdrop, version 2 (Out of Heaven, Favor From God)

One continuous stage video: 225.0 s (live length 210.0 s, then a 15 s calm hold), 60 fps, 1920x1080. Plan, cues, checks
and status: `project-docs/backdrops/s08-full2/`.

- `s08_full2.py`: the song module (music times `M`, word times `WT`, camera keys, the arch, point sets, people, looks).
- `lockup.py`: the opening lockup and the top left signature, drawn over the finished picture (engine/titles.py timing).
- `render.py`: stills and frame ranges on the pinned Revision 3 engine (run `tools/nine_colours_minor/prepare.py` first).
- `finish.sh`: joins the parts and makes the stage, review and phone files.
- `check.py`: length, frame, signature and sync checks on the finished files.

Setup: `project-docs/backdrops/HANDOFF-FULL-BACKDROPS.md` (apt packages, pip packages, fonts). The recording goes in
`work/s08_full2/s08.mp3` and its features in `work/s08_full2/features.npz` (`engine/analyze.py` on the recording padded
to 210.0 s); neither is committed. Render in the cloud only, never on the Mac.

    python tools/s08_full2/render.py --stills 4,64,92 --scale .5
    python tools/s08_full2/render.py --range 0 3375 --out out/s08_full2/parts/p00000.mp4   # four such parts at once
    tools/s08_full2/finish.sh out/s08_full2/parts work/s08_full2/s08.mp3 out/s08_full2/final
    python tools/s08_full2/check.py out/s08_full2/final work/s08_full2/s08.mp3
