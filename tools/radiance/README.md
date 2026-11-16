# The Light That Reaches You

An independent 62-second Astra revision, built in the existing Python and
moderngl engine. It follows light from a pair of luminous hands through nine
human encounters, along a reflected river and a flowing veil, then rises to a
world lit by the acts of kindness. The world becomes the campaign logo and a
living end card.

The saved-film review is in
`project-docs/promo/astra/VISUAL-REFERENCE-REVIEW.md`. The Wave, The Relay,
Ascension and Masterpiece supply visual references, not pre-rendered footage.
Every final frame is rendered locally from the engine.

## Scope and provenance

This is a separate entry point under `tools/radiance`. It changes no shared song,
acting, masterpiece, music asset, workflow or renderer file. `master_astra` from
the earlier independent comparison supplies existing human performances; these
are restaged and retimed by `Performance`. Two standing performances from the
previous Astra treatment are retained in `actors.py`. Cloud, globe, symbol,
word and title APIs are reused unchanged. The previous static camera, garden,
opaque-hand studies and lotus renderer are not used.

The branch is based on `creative/a-world-made-gentle` at 6050921. A draft PR
against that branch isolates the new revision. This is not approval of that
rejected film and is not a proposal to merge it into the shared masterpiece.

The independent seven-song edit is retained from the earlier Astra treatment:
09, 08, 04, 05, 11, 01, 03. `music.py` rebuilds it from read-only concert clips,
with a common 112 bpm pulse, pitch-preserving timing, harmonic excerpt selection,
six 2.143-second overlaps, bass handoffs and controlled levels. Its final chord
is at 57.5 seconds, with the tail settling by 61.8. No music is generated.

## Local build

Use the repository's existing dependencies and font setup. From the repository
root:

```sh
python tools/radiance/music.py
python engine/analyze.py work/radiance/score.wav work/radiance/features.npz
python tools/radiance/render.py --stills '1,10.5,22,30,41.5,47,50,57' --outdir out/radiance/stills
python tools/radiance/probe.py
python tools/radiance/export.py --workers 4 --parts 8
python tools/radiance/verify.py out/radiance/The-Light-That-Reaches-You-1080p60.mp4 out/radiance/The-Light-That-Reaches-You-review-720p60.mp4
```

Both exports have 3,720 independently sampled frames at 60 fps. The phone copy
retains the frame rate and uses H.264, AAC, yuv420p and faststart. Export reuse is
allowed only when the input manifest and decoded part frame counts agree.

Private outputs are under `out/radiance/`. Audio, features, logs, the source
manifest and caches are under `work/radiance/`; removing these folders clears
only this revision's local products. No generated media or caches belong in Git.
Do not dispatch the paid Render workflow.

## Review limits

Frame-order hashes, camera measurements, frame difference scans, audio level
measurements and frame strips are technical evidence. They do not establish
emotional impact, natural acting in every frame, or musical quality by listening.
The owner judges the finished film. Delivery validation is recorded separately.
