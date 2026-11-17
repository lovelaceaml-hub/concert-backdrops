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

## Exact master download, 2026-11-16

The original 318,834,702-byte master is now in [this private Google Drive folder](https://drive.google.com/drive/folders/1_m5HLeo8brJgZMgdXleEbY7klrAGaxgS) as four byte parts plus an offline restore helper. This is one video, not four versions. No video or audio was re-encoded, and no quality was reduced.

On a computer:

1. Download the entire Drive folder and unzip it.
2. Open `Open-to-save-video.html` in Chrome, Edge or Safari.
3. Select all four `Nine-Colours-4K60.part01` through `.part04` files.
4. After verification, click **Save the 4K60 video** to save the original MP4 to Downloads.

Drive preview does not run the helper; download and open it locally. Each part is checked against its SHA-256 before saving. Full-sized Chromium testing over loopback HTTP produced the exact original MP4 and full-file SHA-256, rejected a missing part, handled reverse selection order, and made zero external requests. Drive confirms all seven package files are downloadable and their sizes match. Local file-URL opening and the owner's device download have not been verified.

The single-file Drive upload exceeds the connector's 100 MiB limit. The owner also authorized a private GitHub draft-release upload, but the asset endpoint returned HTTP 401; that draft has no video asset. Both direct workspace MP4 and ZIP links failed on the owner's device. The four-part package is the available transfer route. No public share permission, smaller encode, paid service or Render workflow was used.

Rebuild this transfer package without re-encoding:

```sh
python tools/nine_colours_quality/package_transfer.py
```

Parts, the generated HTML and the manifest live under
`work/nine_colours_quality/exact-transfer/` and must not be committed.
Only the generator is source-controlled. It pins the master to `final-qa.json`.
Draft PR #73 remains unmerged; the quality export awaits owner review.

## Session paused, November 16, 2026

The owner requested a stopping point. [Saved findings and local delivery
handoff](https://drive.google.com/file/d/1BdI-R2ceMFqyBe1nsxSdzBtM6dG5K9UN/view) include the ready-to-use local Codex prompt and exact
Drive part IDs. The original master hash and all seven Drive package file sizes
were rechecked. No render/encode job is active. PRs #72 and #73 remain draft.

The owner asked the assistant to save the video to Downloads, but this cloud
session has no local file or browser-control access. A local handoff prompt was
provided; successful download and owner review remain unconfirmed. Resume with
actual local delivery and full-file SHA-256 verification. Do not rerender,
re-encode, reduce quality, merge or schedule overnight work for this checkpoint.
