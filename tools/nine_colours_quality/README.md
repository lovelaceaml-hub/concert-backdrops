# Nine Colours: clean UHD master

The owner reported grain and low quality in both Revision 3 deliveries, then
requested one highest-quality version instead of multiple viewing copies.
This is an image-quality export of the approved edit, not a new creative cut.

## What changes

- Render the scene at a real 3840x2160 and native 60 fps. No upscale or generated
  intermediate frames are used.
- Disable the pinned composite shader's synthetic film grain in this wrapper
  only. The shared engine, its snapshot on disk and the approved renderer are
  not edited. Scene particles, stars, sparkles and materials stay intact.
- Retain the final composite in half-float, then send 16-bit RGB directly to
  the 10-bit encoder. This avoids prematurely rounding smooth sky gradients
  to 8-bit. Exact RGB48 samples are saved losslessly for validation. No older
  compressed video is used as an image source.
- Encode HEVC Main 10 in an MP4 with the Apple-compatible hvc1 tag, BT.709 SDR,
  CRF 12 and no bitrate or file-size cap. This is a very high-quality lossy
  delivery, not a mathematically lossless claim. Half-float scene precision
  feeds the 10-bit encode; the color and brightness remain SDR, not HDR.
- Copy the approved master audio stream without another audio encode. The
  exact 66-second edit, music, camera, animation, effects, cards and wording
  remain unchanged.

The existing approved source tag and uploaded files remain available. This
quality variant is subject to the owner's review. Nothing is merged and no
paid service or GitHub Render workflow is used.

## Reproduce

With the Revision 3 dependencies, fonts, pinned snapshots and approved master
already present, run from the repo root:

```sh
python tools/nine_colours_minor/quality.py --stills 3,16,43,56.8,62
python tools/nine_colours_minor/quality.py --all --workers 3 --parts 12
python tools/nine_colours_quality/deliver.py
python tools/nine_colours_quality/verify.py
```

The input restoration procedure is in `tools/nine_colours_minor/README.md`.
Use three workers on a 16 GB machine; four UHD renderers plus 10-bit encoders
can exceed memory during scene or encoder-buffer peaks.
The delivery script expects the exact approved master under
`out/nine_colours_revision3/` solely to copy its audio stream.

Private renders live in `out/nine_colours_quality/`. Logs, input hashes and
validation evidence live in `work/nine_colours_quality/`. These files are
untracked and must not be committed. A manifest prevents reusing completed
ranges after render inputs change. Remove or move both quality folders to
start a fresh export; this does not touch the archived Revision 3.

## Initial validation

Five matched times at both 1080p and native 4K isolate the grain removal:
3, 16, 43, 56.8 and 62 seconds. Maximum difference is 2/255 per channel, with
mean absolute difference between 0.315 and 0.382/255. This is intentional
noise removal across the image, not the old zero-pixel-change performance
task. Native 4K frames at these five times match exactly in fresh forward and
reverse processes.

An additional precision check at 56.8 seconds compared the half-float final
target with the old 8-bit target. Rounded to 8-bit for comparison, the largest
channel difference was 1/255 and the mean was 0.0207/255. A sampled sky region
retained 832 blue-channel levels at 10-bit versus 213 at 8-bit. This change
prevents grain removal from exposing coarse gradient steps.

## Completed master and validation

`Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4` is complete under the quality output
folder: 318,834,702 bytes, 66.000 seconds, 3,960 native 4K60 frames, HEVC Main 10.
SHA-256: `6ed17b8cd9a0fd5031cd857c517696ebe5f24514e019abf038be736714f186a2`.

All frames decode without errors; zero consecutive repeated frames were found.
The maximum timestamp error is 0.000000333 seconds. Approved audio packets
match exactly, and five fresh samples match their full-range source frames.
Across 18 encoded/source comparisons, RGB PSNR is 43.34 to 49.99 dB and
mean absolute channel error is 0.320 to 0.763/255. Full-film frames, Respect,
Earth details and the closing card were visually reviewed.

Drive video transfer remains pending. The connector rejected the 318,834,702-byte
file before action invocation because its limit is 104,857,600 bytes. The full
quality original is linked in the Codex chat; no smaller copy was created.
The [shared quality record](https://drive.google.com/file/d/1Naj7qe3t4kvS1KV8xYG2PrbYJcFc5On8/view)
records the exact file, source, checks and transfer limitation. The new quality
file awaits owner review, and draft PR #73 remains unmerged.

For full quality, download the original file. A Drive streaming preview can
use a lower-resolution transcode even when the uploaded original is 4K.
