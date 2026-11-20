# 4K and animation setup verification

Verified on November 20, 2026 (America/Los_Angeles), in a Linux x64 cloud CPU
workspace. This extends `setup/repeatable-video-pipeline` and draft PR #97. The
starting commit was `7d3dbdb373a4b504e34e2c2e53a00518efadda8f`.

The approved concert films, existing engine scenes, source audio and original
Render workflow are unchanged. No GPU provider, paid service, Mac rendering,
workflow dispatch or creative approval was added.

## Implemented and verified

| Area | Evidence |
|---|---|
| Python contracts | 62 focused tests passed. This includes source-change rejection, interrupted-chunk recovery, actual PNG bit depth, stale finishing inputs, archive protection, adapter bounds and timing validation. |
| JavaScript | 21 Node tests passed, including cross-language camera fixtures, signed roll parity, deterministic motion, musical envelopes and an actual H.264 color-conversion encode. |
| High-bit finishing | Real RGB16 sequences encoded as H.264 High, HEVC Main 10 and ProRes 422 HQ, including two-shot concat, 48 kHz audio, exact clocks and decoded metadata checks. |
| Finishing preservation | An intentionally wrong-fps re-encode was rejected while the preceding master, receipt and approval remained byte-identical. |
| Actual scene contract | Blender study accepted optional camera fields and empty parameters; direct and baked roll matched exactly. A musical cue carried over the cut with maximum hand-position error of 0.0000003385 m against the analytic pose. |
| Saved physics | A four-frame cloth and rigid-body example saved, reopened and supported late/early/late frame access. Four cloth cache files were present; the rigid-body cache was embedded in the blend file. |
| Source consistency | Source hashes are checked before and after each chunk. A source edit during a worker run is rejected rather than receiving a valid receipt. |

## Measured animation accuracy

The no-render Blender test evaluates real armature deformation and F-curves in
the pinned Blender 5.2.4 LTS runtime. These measurements describe the procedural
test rig and selected samples; they are not claims about a completed production
choir or arbitrary imported motion capture.

| Measurement | Largest observed error |
|---|---|
| Applied armature pose versus analytic source | 0.000000364 m |
| Subframe pose versus analytic source | 0.0000208 m |
| Subframe foot-contact drift | 0.000000268 m |
| Full-range versus chunk pose | 0 m |
| Camera subframe position versus analytic source | 0.0001033 m |
| Full-range versus chunk camera position | 0 m |
| Matching-skeleton retarget | 0.000000477 m |

The 10-second camera path was sampled at 120 Hz. Its maximum speed was about
1.355 m/s, maximum acceleration 0.491 m/s squared, and maximum sampled jerk
0.481 m/s cubed. Both endpoint speeds were zero; no configured trajectory review
threshold was exceeded. Cubic source paths are C2. Dense linear baked keys
approximate them and do not guarantee mathematically continuous jerk.

## Render evidence

The frozen-source render completed, and the resulting movie was decoded for
technical QA. No creative approval was recorded.

| Check | Actual result |
|---|---|
| Complete engineering preview | 320 x 180, 600 rendered frame times, 60 fps, 10.000 seconds, H.264 High, no audio |
| Delivered-movie scan | All 600 frames decoded; no technical errors, freeze warnings, flicker candidates or shimmer candidates under the configured heuristics |
| Native review frame 299 | 1920 x 1080 RGB16 PNG, 24 Cycles samples, 135.8301 seconds of worker frame time |
| Native 4K frame 299 | 3840 x 2160 RGB16 PNG, eight Cycles samples, 216.9212 seconds of worker frame time |
| Resume check | Same render command reused all 600 verified frames and rendered zero new frames |
| Archive check | Current master, matching QA, project files, lockfiles, render provenance and SHA-256 manifest archived successfully; creative review status remained `not_recorded` |

The two native-size presets have different sample budgets. Their timings are
individual measurements, not a controlled resolution-only speed comparison.
Only frame 299 was rendered at each native size in this check. The full final
preset uses 64 samples and has not been rendered as a complete movie.

Those measurements also showed that the original 30-frame/1800-second worker
budget was too short for a full native-size sequence on these CPUs. New cinematic
projects therefore start with one-frame chunks and a 7200-second timeout. The
recorded example manifest and its verified frame cache remain unchanged. This
factory-default change was checked with the focused cinematic contract tests;
it changes worker scheduling, not the verified scene or image generation.

The original native 4K PNG is 27,007,155 bytes. Its PNG IHDR identifies 16-bit RGB
pixels; this was checked directly rather than inferred from a filename or an
8-bit image viewer. The actual file was then encoded once with each delivery
profile:

| Profile | Verified video format | Decoded frames | Nominal and average FPS | Bytes |
|---|---|---|---|---|
| H.264 | High, `yuv420p` | 1 | 60/1 | 107,601 |
| HEVC | Main 10, `yuv420p10le` | 1 | 60/1 | 55,792 |
| ProRes | HQ, `yuv422p10le` | 1 | 60/1 | 1,861,618 |

All three outputs retained 3840 x 2160 dimensions and passed the actual stream
validator with no audio expected. They use Rec.709 SDR. The test duration was
one frame, 0.016667 seconds. These are encoder checks, not moving 4K films.

Native-frame thumbnails and a twelve-frame timeline sheet were inspected for
framing and continuity. The image is a simplified gold conductor in a procedural
pavilion with moving light ribbons. The mannequin has no detailed face or
articulated fingers. These checks do not establish natural performance, final
concert art or polished close-up quality, and real-time browser playback was not
verified in this environment.

Evidence hashes:

```text
10-second preview SHA-256:
afecad6802d26ac085901c90a4c3567429b5a478dfaec9b5629c5301181aa4b0

Native 4K RGB16 PNG SHA-256:
7c9e6b2e6935a565992232710e49a3dba4b4ea1c6c58e3dd5388f855d39e47ea
```

Private working reports are `work/pipeline/motion-study/benchmark.json`,
`motion-check/qa.json`, and `native-4k-encoding-check.json`. Generated frames and
videos are excluded from Git. Separate copies of the preview and native 4K PNG
are provided with the setup handoff.

## Reproduce the checks

```bash
uv run --frozen --extra legacy python -m unittest discover -s tests/pipeline -v
npm run test:motion
npm run typecheck
npm run build
.tools/blender-5.2.4-linux-x64/blender -b --factory-startup --python-exit-code 1 \
  --python tests/blender/check_animation.py -- --physics
.tools/blender-5.2.4-linux-x64/blender -b --factory-startup --python-exit-code 1 \
  --python tests/blender/check_study.py
./scripts/video validate motion-study
./scripts/video motion-qa motion-study
./scripts/video preview motion-study --quality motion-check
./scripts/video benchmark motion-study --qualities review 4k-check --frames 299
```

The full final preset is native 3840 x 2160 at the same 60 fps, 64 Cycles samples,
16-bit PNG output and a half-frame motion-blur shutter. `4k-check` uses eight
samples to check native resolution and source precision sooner. A full film at
the final sampling budget remains a separate production render.

## Remaining limits

- Chromium is installed, but this managed workspace's local Unix-socket
  restriction previously prevented browser launch. That blocked route was not
  retried or bypassed. Three.js capture, Remotion browser MP4 output and Workbench
  browser playback remain unverified here.
- The Blender MCP package and isolated add-on configuration are installed. Its
  live bridge still needs a permitted Blender GUI session. Dependency checks
  and offline rig rendering do not establish live MCP connectivity.
- The procedural character is a 16-bone stand-in with grouped fingers. Detailed
  hands, garments, instrument contact, complex interactions and final acting
  still require authored work. The existing MakeHuman/CMU asset was preserved,
  not converted into a finished Blender actor library.
- Retargeting was tested with matching synthetic skeletons. Different rest poses
  or proportions require explicit mapping, axis correction and contact review.
- No automatic deflicker, AI frame interpolation, new imagery or generated
  soundtrack was introduced. Temporal QA warnings identify review candidates.
- Output profiles are Rec.709 SDR. The ten-bit source/encode checks do not claim
  HDR. ProRes range metadata can be implicit even though its input conversion
  uses limited-range YUV.
- A GPU provider remains unconfigured. CPU capability does not imply practical
  turnaround for a long, densely detailed 4K60 production.

See [the operating guide](4K-AND-MOTION.md), [delivery details](VIDEO-DELIVERY.md)
and [animation API](../scenes/blender/animation/README.md).
