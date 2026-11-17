# Nine Colours: stopping point for November 16, 2026

Status: paused at the owner's request. The approved creative cut and the clean
4K60 quality master are saved. The remaining task is delivery to the owner's
actual computer, followed by confirmation that the owner can play and review it.
Do not start new renders, edits, encodes, paid services or workflows on resume
unless the owner asks for new work. Never merge on the owner's behalf.

## Preserve this exact file

- Name: `Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4`
- Size: 318,834,702 bytes.
- SHA-256: `6ed17b8cd9a0fd5031cd857c517696ebe5f24514e019abf038be736714f186a2`
- Picture: native 3840x2160, 60 fps, 10-bit HEVC Main 10, hvc1 MP4,
  BT.709 SDR, CRF 12, 66.000 seconds, 3,960 frames.
- Audio: the approved AAC stream copied without another encode.
- Workspace: `/workspace/light-that-reaches-you/out/nine_colours_quality/Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4`.
- The local file's full SHA-256 and byte size were rechecked at this stopping point.

The owner explicitly chose to preserve the exact 319 MB master. Do not reduce
resolution or bitrate to fit a service limit, make another viewing version, or
replace this with one of the older archived phone/1080p files. The video itself
uses high-quality lossy compression; transferring and joining its existing bytes
adds no quality loss. It is SDR, not HDR.

## Durable storage and download state

[Exact master package in the owner's Google Drive](https://drive.google.com/drive/folders/1_m5HLeo8brJgZMgdXleEbY7klrAGaxgS).
All seven files were present, downloadable and the expected sizes at closeout.
The folder is private and existing sharing has not changed.

| Part | Drive file ID | Bytes |
|---|---|---:|
| `Nine-Colours-4K60.part01` | `1VzugNMJKvnvciTN2pyETsP_IvFtYAecN` | 80,000,000 |
| `Nine-Colours-4K60.part02` | `1kYdkwVOpUGgMe5hZptWrWzh7CyEQ2Ucs` | 80,000,000 |
| `Nine-Colours-4K60.part03` | `1xOs7mo_HwXoRK-C5vxaohidn-0ZoVsS-` | 80,000,000 |
| `Nine-Colours-4K60.part04` | `1JhYLERNDuoqjtRBGiVc5R1dE5ktcjxCB` | 78,834,702 |

The other files are `Open-to-save-video.html`, `START-HERE.txt` and
`manifest.json`. The manifest records each part's SHA-256. These are four raw
byte pieces of one MP4, not independently playable clips or alternative versions.
The helper checks every part and saves the assembled original file.

Confirmed: a full-sized Chromium test on loopback HTTP restored the exact
318,834,702 bytes and full-file SHA-256, rejected a missing part, handled reversed
selection order, and made zero external requests. Not confirmed: downloading on
the owner's device, local file-URL opening on that device, or review of the new
quality file. Drive metadata readback is not a remote content hash verification.

## Delivery failures already investigated

1. Direct chat links to the workspace MP4 and the uncompressed ZIP failed on the
   owner's device with a cloud-file loading error. Repeating those links is not
   a verified fix.
2. The Drive connector rejected the single 318,834,702-byte upload before action
   invocation because its per-file limit is 104,857,600 bytes. All four parts
   uploaded successfully below that limit.
3. The owner explicitly approved uploading the exact video to a private GitHub
   draft release in this repository. Do not ask for that approval again.
   The asset upload returned HTTP 401 Bad credentials even though repository API
   access worked. Draft release ID `447617617`, tag
   `nine-colours-r3-uhd60-download-2026-11-16`, has no video asset as last checked.
   Do not present the empty draft as a working download or publish it.
4. This cloud session could see ambient browser-tab information but had no
   callable local browser-control tool or access to the owner's Downloads folder.
   A visible tab alone does not establish control. The owner asked for a local
   Codex prompt, and the prompt below was provided. Completion is not confirmed.

## Ready-to-use local handoff

Use in a Codex session running on the owner's computer. Confirm that local file
access is real before claiming a file was saved to Downloads. Ask only for the
specific sign-in or permission that is actually missing, then continue.

```text
Download my finished video and save it directly in my Downloads folder. Do the
work yourself, rather than giving me assembly instructions.

Google Drive folder:
https://drive.google.com/drive/folders/1_m5HLeo8brJgZMgdXleEbY7klrAGaxgS

Download Nine-Colours-4K60.part01, .part02, .part03 and .part04 using my connected
Google Drive or browser. Join their raw bytes in that exact order. Do not
re-encode, resize, rerender or modify the video or audio.

Save in my actual local Downloads folder as:
Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4

Verify size: 318,834,702 bytes.
Verify SHA-256:
6ed17b8cd9a0fd5031cd857c517696ebe5f24514e019abf038be736714f186a2

No paid services or repository changes are needed. Preserve existing files.
Confirm that you are working on my computer, not in a cloud workspace. Ask for
specific sign-in or file permission only if needed. After verification, open
Downloads with the completed MP4 selected and report its full local path.
```

## Saved source, validation and findings

- Approved creative source: `46df53b98a43f58e51a78d40ee5794108a68e13c`, tag
  `film10-revision3-approved-2026-11-16`, draft PR #71.
- Quality work: branch `quality/nine-colours-clean-master`, draft PR #73.
  Renderer started at `2c95ee0`, completed delivery and QA through `dd8f0f5`,
  exact-transfer helper at `58583071e9348ae3331b4d966aa87406baea3720`.
- Shared documentation: branch `docs/nine-colours-revision3-approved`,
  draft PR #72. Earlier transfer checkpoint is `e49c7b9`.
- [Quality record and full measurements](https://drive.google.com/file/d/1Naj7qe3t4kvS1KV8xYG2PrbYJcFc5On8/view).
- Full decode passed; zero repeated adjacent frames; all 60 fps timestamps
  within 0.000000333 seconds; exact compressed audio identity; five fresh frames
  equal full-range source frames and equal fresh forward/reverse renders.
- Eighteen encoded/source comparisons: RGB PSNR 43.34 to 49.99 dB and mean
  absolute channel error 0.320 to 0.763/255. Full-film sheets and native
  Respect/Earth/card details were visually reviewed.
- Removing composite grain changed matched samples by at most 2/255. The
  floating-point final target preserves gradient precision into 10-bit encoding.
  Existing stars, glitter, motion blur and effects are intentional and retained.
- Three UHD workers fit the 16 GB cloud machine; four exceeded memory. This is
  reproduction guidance, not an instruction to rerender the completed file.
- Private evidence remains under `work/nine_colours_quality/`: `final-qa.json`,
  `delivery-4K.json`, `transfer-browser-test.json`, `exact-transfer-upload.json`,
  `download-transfer-status.json`, render logs, manifests and samples. Generated
  files stay untracked. Never commit videos, frames, caches or audio features.
- Earlier performance and automatic-QA assignments remain separate work recorded
  in PR #55. This stopping point does not claim the original 2x speed target or
  every earlier engineering task was completed.

## Stop and resume boundary

No active render/encode job or helper agent was found at closeout. PRs #72 and
#73 were confirmed open, draft and unmerged. Protected engine/song/acting/music/
workflow files are unchanged by this closeout. Existing archived creative
approval is preserved and does not imply approval of the new quality export.

When the owner resumes, complete local delivery first. Record a verified local
path and successful playback confirmation before marking delivery complete.
Keep Claude informed through the authorized PR #55 thread. Do not start an
overnight job, make a scheduled task, merge, or change the approved film while
the owner has asked to stop.
