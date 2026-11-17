# The Light That Reaches You

An independent 62-second Astra revision, built in the existing Python and
moderngl engine. The owner selected Film 10, Nine Colours as the principal visual
reference. White-cored coloured comets travel over a star-filled mirror lake,
visit nine human encounters, pass through blue hoops, wrap the embrace in a
double helix, then gather into a rising nine-colour braid. The flight revision adds banked
fly-bys over reflected words and a full climbing barrel roll through a 62 metre
column of light. Camera direction is interpolated separately from position; a
carried up vector prevents flips near the vertical. The colours reach a
world of light that becomes the campaign logo and a living end card.

The saved-film review is in
`project-docs/promo/astra/VISUAL-REFERENCE-REVIEW.md`. Film 10's handover and
source on `ten/10-nine-colours` informed the layered comet treatment. No saved
video is composited into the result. Every frame is rendered locally. The
intermediate cloud/veil export was stopped when the owner chose Nine Colours.

## Scope and provenance

This is a separate entry point under `tools/radiance`. It changes no shared song,
acting, masterpiece, music asset, workflow or renderer file. `master_astra` from
the earlier independent comparison supplies existing human performances; these
are restaged and retimed by `Performance`. Two standing performances from the
previous Astra treatment are retained in `actors.py`. Globe, symbol,
word and title APIs are reused unchanged. The previous static camera, garden,
opaque-hand studies and lotus renderer are not used.

The branch is based on `creative/a-world-made-gentle` at 6050921. A draft PR
against that branch isolates the new revision. This is not approval of that
rejected film and is not a proposal to merge it into the shared masterpiece.

The independent seven-song edit is retained from the earlier Astra treatment:
09, 08, 04, 05, 11, 01, 03. `music.py` rebuilds it from read-only concert clips,
with a common 112 bpm pulse, pitch-preserving timing, harmonic excerpt selection,
six 2.143-second overlaps, bass handoffs and controlled levels. Its final chord
is now at 60.2 seconds, with a crescendo and a brief release at the very end.
The owner explicitly requested a loud finale, replacing the prior quiet ending.
A linked stereo soft knee controls peaks. Nine colored fountains and comet arcs
continue around the invitation. No music is generated.

## Local build

Use the repository's existing dependencies and font setup. From the repository
root:

```sh
python tools/radiance/music.py
NUMBA_CACHE_DIR="$PWD/work/radiance/numba" python engine/analyze.py work/radiance/score.wav work/radiance/features.npz
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

## Reflected words and the loud ending

The latest owner direction replaces the handbook's earlier no-reflected-words
and quiet-final-second rules for this independent film. Expressions now occupy
fixed planes in the world. They hold for 2.6 seconds, then the camera banks over
their true water reflections. The engine mirror pass draws those reflections.
The final audio check requires a strong climax and a clean last 10 ms release,
not a quiet final second. Both policies are explicit in the verification report.

## Review limits

Frame-order hashes, camera measurements, frame difference scans, audio level
measurements and frame strips are technical evidence. They do not establish
emotional impact, natural acting in every frame, or musical quality by listening.
The owner judges the finished film. Delivery validation is recorded separately.
