# Nine Colours, restored and upgraded

Anthony selected the original saved Film 10 video and its music, asking for
essentially the same film with the later model, animation, text and card upgrades.
This version restores that film directly instead of restaging its concept.

The reference is the Film 10 render 1 share copy from run 43726203825, whose source commit
is `d928ff9eafe02ac3150f0c646bdcc497fe5a7278`. `original.py` retains that exact
shot/light source with a provenance header and ASCII dash normalization. Its
historical cast builder and old card are overridden by `film.py` and `cast.py`.
No old dark, fragmented or mixed-gender touching cast is instantiated.

## Retained from the preferred film

- Original camera paths, sequence and geography through the spiral: prism, lake chase, blue gate,
  embrace helix, dancer orbit and half-loop, dive to parent and child, gratitude, two profiles,
  prayer and musical breath, rising braid, world of light becoming the campaign logo.
- Original comet paths, colours, light cues and music-section timing. The finale
  is the requested exception: globe, surrounding expression symbols and hearts,
  then the official logo and card, as specified in PHASEB UPDATE 20.
- Approved `audio/promo/concert-medley-leadin.mp3`, preserving the original
  eight-song medley with its two-second quiet lead-in and gentle entry fade.
  No song is replaced, reordered, pitch shifted or tempo adjusted. The soundtrack
  is the original eight-section edit, superseding the earlier Astra seven-song
  requirement under the owner's latest choice of this exact film and music.
- Original musical crescendo, final accent at film time 60.11 seconds and release.

## Applied upgrades

- Native 60 fps, including the phone copy.
- Whole warm-gold models, denser head/hand sampling, finer garment and hair detail,
  gentle gesture easing, same-gender contact and a two-woman embrace. Remove
  disperse, shards, dark windows and dissolving body effects. A standing prayer
  avoids the old kneeling skirt/shin intersection.
- Current exact expression wording, campaign-colour label pills and sharp type.
  All nine readings hold for at least 2.5 seconds. Just the first two readings
  move within the original chase/gate interval to clear the longer opening card.
- No isolated date in the musical breath. Date/time stay in the signature and
  full event cards, following PHASEB UPDATE 16.
- Reflections appear on departure, after the main phrase has been read, through
  the engine's real mirror pass. This avoids reflected letters crossing the
  reading during the parent-and-child approach. Reflection-only batches are implemented
  by this entry point's Layer subclass, with no shared renderer changes.
- Current opening, fully readable through seven seconds; a smaller continuous
  corner signature; official-style end card, whole from 55 seconds to the end.
  Moving perimeter fountains and comet arcs continue through the final accent.
- Reduce the source's full-frame flash strengths while retaining their cue times.
  The original free-flying half-loop and braid retain their explicit camera up.

## Reproduce locally

Use the repository's dependencies, fonts and software OpenGL. From the repo root:

```sh
python tools/nine_colours/music.py
NUMBA_CACHE_DIR="$PWD/work/nine_colours/numba" python engine/analyze.py work/nine_colours/score.wav work/nine_colours/features.npz
python tools/nine_colours/render.py --stills '1,8,11,17,20.5,24.5,27.8,31.2,34,38,45.8,49.8,53,57,61' --outdir out/nine_colours/stills
python tools/nine_colours/probe.py
python tools/nine_colours/export.py --workers 4 --parts 8
python tools/nine_colours/verify.py out/nine_colours/Nine-Colours-Restored-1080p60.mp4 out/nine_colours/Nine-Colours-Restored-review-720p60.mp4
```

`render.py` delays the entire original 3D timeline by two seconds, including its
camera, mirrors, birth times, world and light cues. Audio-reactive values read
the corresponding delayed features. Updated 2D titles use final film time.

Private files and caches live under `work/nine_colours/` and `out/nine_colours/`.
Delete these folders to clear them. No generated media belongs in Git. Export
reuse requires matching source manifests and complete decoded part frame counts.

The soundtrack check reports the original song joins rather than replacing the
owner's preferred edit to satisfy a threshold. Frame and audio measurements do
not establish artistic quality or replace a listening audition. Final delivery
validation is recorded separately after the finished exports are inspected.

All source changes are isolated under `tools/nine_colours/`; the final card's
perimeter animation reuses `tools/radiance/celebration.py`. Shared song, master,
acting, audio and workflow files remain untouched. No paid services or GitHub
Render workflow. Draft PR only; Anthony decides whether to merge.
