# Ten-second promo design example

An isolated design proposal requested by Anthony on November 20, 2026, following
the repeatable video pipeline setup. It demonstrates a more detailed luminous
Earth, controlled colored light, spatial occlusion, flowing motion and readable
typography using the approved Nine Colours promo as its reference.

## Design and references

- Reviewed sampled frames from the actual approved Film 10 Nine Colours Revision
  3 phone export, not just its source code. Its SHA-256 is
  `ad4b4e7fe861ae34eb80e8b921ee747efc477c08bb89ec981f1b588a0b3c0af5`.
- Retains the exact existing campaign logo, nine expression symbols, campaign
  colors, Cormorant Garamond/Jost typography and concert wording.
- Uses the existing public-domain Natural Earth land mask for the globe. Clouds,
  illumination, stars, geometry and ribbons are computed by code. No generated
  imagery, stock footage, traced photos or new music is used.
- The continuous camera arc uses the new `pipeline.motion.CameraTrack` API.
  Three groups of three streams gather into inclined orbits with continuous
  easing, foreground passage, and correct depth testing against the globe.
- Symbols appear gradually. All concert text is present from the first frame.
  The clouds and light remain gently alive at the end, without a black fade.
- Music is seconds 50 through 60 of the existing `concert-medley.mp3`, with an
  80 ms entry fade. The existing musical release is preserved. The source is
  unchanged. The final authored accent is at sample time 8.11 seconds.

This is a proposed ten-second design, not an alteration or new approval of the
66-second film. It focuses on the Earth finale and concert identity; it does not
demonstrate finished character acting or new church models.

## Renderer and output

The scene runs through ModernGL/EGL on Mesa llvmpipe in the cloud CPU workspace.
It uses the shared camera foundation and delivery validator from the new stack,
with a purpose-built stylized raster scene. This example does not depend on the
blocked browser or live Blender GUI bridge and is not a Cycles speed benchmark.

Each output frame has two real scene evaluations across a half-frame shutter.
Rendering uses floating-point intermediate buffers; the viewing export is
8-bit H.264 High, Rec.709 SDR, at a native 60 fps clock. No frame interpolation or
upscaling is used. The supplied resolution determines the native drawing size.
This sample does not claim 10-bit or HDR delivery.

## Reproduce

From the repository root after the locked bootstrap, on a cloud CPU:

```bash
uv run --frozen --extra legacy python tools/promo_design_example/build.py \
  --workers 2 --width 1920 --height 1080 \
  --directory work/promo-design-example/final
```

The full native 4K version uses the same scene and timeline:

```bash
uv run --frozen --extra legacy python tools/promo_design_example/build.py \
  --workers 2 --width 3840 --height 2160 \
  --directory work/promo-design-example/4k
```

The isolated assembly recipe retains its original `1080p60` working basename
even when custom dimensions are supplied. `delivery.json` records and validates
the actual dimensions. User-facing copies are named for their verified size.
The final media lives under ignored `work/`, not Git.

The builder renders four independent 150-frame parts. It verifies source hashes,
can reuse complete matching parts, extracts the music without changing the
source, concatenates the picture and audio, and checks the finished streams.
Reuse cached parts only in the same locked dependency and renderer environment:
the receipt does not fingerprint runtime versions. Use a fresh `--directory`
for each new review round and preserve completed delivery copies separately.
The working movie paths are overwritten during assembly, so a failed rebuild
can leave a partial working file. Worker counts are bounded to four. Darwin
execution is rejected so the recipe does not accidentally start rendering on
the owner's Mac.

For a native frame inspection:

```bash
uv run --frozen --extra legacy python tools/promo_design_example/render.py \
  --width 1920 --height 1080 --stills 0,5.11,8.11,9.983 \
  --out work/promo-design-example/stills
```

## Review scope

Inspect the resulting movie at its actual playback rate. The builder checks
the finished stream metadata, dimensions, frame rate and audio. The independent
delivery review additionally decoded all frames, checked their timestamps,
measured decoded audio, ran `pipeline.temporal.scan_motion`, and compared a
decoded keyframe with its native source. Those additional checks are recorded
below; they are not automatically rerun by this isolated builder and do not
decide artistic quality. The source film, its audio, shared scene/acting modules
and the paid Render workflow are preserved. No cloud GPU provider is configured.

The delivery measurements and visual review are recorded in
`VERIFICATION.md` after the completed export checks.
