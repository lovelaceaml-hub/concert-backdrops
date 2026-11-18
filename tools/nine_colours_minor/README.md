# Film 10, Revision 3

This isolated creative revision implements the owner's three requests after approving Revision 2:

- The original nine colored comets flow into the luminous Earth. A continuous camera arc replaces the old finale cut. Each comet joins the path of its own expression symbol; the symbols orbit in three dimensions, pass behind the Earth, illuminate it and disperse as it becomes the logo.
- All nine expressions use Claude Final v1's glowing capsule labels and cream Cormorant serif phrases, with its camera-facing placement and clean departures. Original reading times remain except small overlap corrections. Hoops and comets dim within the reading bounds.
- Respect uses the reference's two warm gold women, refined offer/listen gestures, hair and garments, in a wider moving shot of the lantern lake. This replaces Revision 2's light flower.

The approved six-second lead-in, opening card and burst, small signature, original concert medley and 66-second duration remain. The closing card is fully readable from 59 seconds through the last frame. Both delivery files are native 60 fps. The other original people, original aerial loop and pre-finale camera ride remain.

## Exact references

Film 10 render 1: run 43726203825, commit `d928ff9eafe02ac3150f0c646bdcc497fe5a7278`.
Claude Nine Colours Final v1: run 43855882765, commit `f43f4514e4bc42dc25166e90160d98219f5a0db4`, share artifact 14222872749.
Prior approved version: draft PR #70, commit `3c88a7942c381d07e77d1ff9f89dfb920200910d`.

The complete original render engine stays pinned. Claude's words, body/acting and symbol-orbit modules are read from a second private pinned snapshot in a separate Python package. Their public value types are mapped to the original renderer's API. This leaves every shared/protected song, acting, master, music and workflow file untouched. No paid services or workflow dispatch are used. The PR stays draft and unmerged.

## Reproduce locally

From the repository root, with the existing fonts and Python dependencies:

```sh
python tools/nine_colours_minor/prepare.py
python tools/nine_colours_minor/render.py --stills 0,10,16,43,55.7,56.8,57.7,59 --outdir work/nine_colours_revision3/stills
python tools/nine_colours_minor/check_fidelity.py
python tools/nine_colours_minor/export.py --workers 4 --parts 8
python tools/nine_colours_minor/verify.py out/nine_colours_revision3/Film-10-Nine-Colours-Revision-3-1080p60.mp4 out/nine_colours_revision3/Film-10-Nine-Colours-Revision-3-phone-720p60.mp4
```

`prepare.py` restores Git objects into `work/nine_colours_minor/render1` and `work/nine_colours_revision3/claude-final`. Fetch the two source commits if they are absent locally. It creates analyzed audio features and a 66-second PCM score: the approved lead-in track with four extra seconds of silence. It does not modify any audio source.

All private snapshots, caches, logs and validation files live under `work/`. Renders live under `out/nine_colours_revision3/`. Both folders are untracked. Clear Revision 3 caches by deleting its `work/nine_colours_revision3` folder, then run preparation again. Retain earlier output folders to keep previous deliveries. Export hashes its source, reference assets, fonts and score, and refuses to reuse parts after an input change.

The fidelity script tests fresh-process forward/reverse render order. Creative changes intentionally alter pixels, so it does not claim equality with the previous video. `verify.py` checks duration, native frame rate, every timestamp, repeated frames, audio levels and release, and reports motion statistics for visual review. See VALIDATION.md for final evidence and limits.
