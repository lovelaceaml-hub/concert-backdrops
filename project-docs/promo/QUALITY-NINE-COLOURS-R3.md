# Film 10 Revision 3: clean UHD delivery

**One native 4K60 master is complete and checked; Drive transfer is pending.** The owner reported grain in both older exports and requested one highest-quality file. This quality-only export preserves the approved 66-second cut and exact compressed music stream. It removes added composite grain and renders real 3840x2160 frames at 60 fps through a floating-point composite into 10-bit HEVC. Download the original for full quality; Drive preview can be lower resolution. The 318,834,702-byte original exceeds the 104,857,600-byte connector upload limit. No smaller copy was made; the original is available in the Codex workspace and chat. The new quality delivery awaits owner review. The earlier approved files and source tag remain archived. Draft PR #73 is unmerged.

## Exact file

- Name: `Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4`
- Drive status: Drive transfer pending: connector rejects files larger than 104,857,600 bytes.
- Workspace file: `out/nine_colours_quality/Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4`
- Size: 318,834,702 bytes
- SHA-256: `6ed17b8cd9a0fd5031cd857c517696ebe5f24514e019abf038be736714f186a2`
- Picture: 3840x2160, native 60 fps, 3,960 frames, 66.000 seconds.
- Encoding: HEVC Main 10, hvc1 MP4, BT.709 SDR, CRF 12, no bitrate or file-size cap.
- Audio: exact approved AAC stream copied without another encode.

The master uses high-quality lossy video compression for practical phone and screen playback.
It is not mathematically lossless or HDR. No lower-resolution viewing copy was created.
Stars, glitter people, sparkles, soft light and motion blur are intentional scene elements;
they have not been removed with a denoiser or altered to make the picture artificially sharp.

## Owner direction and preserved edit

On 2026-11-16 the owner reported low quality and grain in both the phone and 1080p files,
then requested one highest-quality delivery: "I want it super clear ultra hd no pixelation".
This supersedes the small phone-copy target for this cut. It does not request a new edit.
The approved Revision 3 remains the creative source: extended opening and burst,
cream expression text with capsules, golden listening pair, swirling light becoming Earth
with orbiting symbols, signature, official closing card and original Film 10 score.

The approved source is `46df53b98a43f58e51a78d40ee5794108a68e13c`, tag
`film10-revision3-approved-2026-11-16`. The renderer wrapper is pinned by the
private `quality-manifest.json`; rendering started with quality code at `2c95ee0`.
Delivery metadata correction and QA code are included through `dd8f0f5`.
Implementation: [draft PR #73](https://github.com/lovelaceaml-hub/concert-backdrops/pull/73),
branch `quality/nine-colours-clean-master`, based on draft #71. Nothing was merged.

## Validation

- All 3,960 frames decoded without errors; zero consecutive repeated frames.
- Every frame presentation timestamp checked against native 60 fps. Maximum error:
  0.000000333 seconds.
- Exact approved compressed audio packets match by SHA-256.
- Five fresh stills match full-range source frames exactly, and fresh forward/reverse
  processes match at 3, 16, 43, 56.8 and 62 seconds.
- Eighteen encoded samples compared with their exact RGB48 source frames: RGB PSNR
  43.34 to 49.99 dB; mean absolute channel error per sample
  0.320 to 0.763/255.
- Full-film contact sheet and native output details visually reviewed before upload.
- Local master SHA-256 recorded. Drive upload failed before the action was invoked;
  no new Drive video ID exists and no remote verification is claimed.

The precision probe preserved 832 sampled sky blue-channel levels at 10-bit versus
213 at 8-bit. This avoids discarding gradient detail before encoding. Grain removal
alone changed matched samples by at most 2/255 per channel; this was intentional
image cleanup, not the earlier pixel-identical performance task.

## Reproduce and hand off

See `tools/nine_colours_quality/README.md` on the quality branch. Restore the pinned
Revision 3 inputs described in `tools/nine_colours_minor/README.md`, then render,
assemble and verify with the quality scripts. Three workers fit the 16 GB cloud
workspace. Four workers can exceed memory during UHD encoding.

Generated files live under `out/nine_colours_quality/` and validation/input manifests
under `work/nine_colours_quality/`. Neither folder is committed. The prior approval
record and original uploads remain unchanged for history. Protected engine and song
files and music sources were not edited. No paid service or GitHub Render workflow
was used.
