# Song 11 delivery and reviewed host assembly

These tools assemble and check the complete **Almighty God Knows the Future** recreation. Assembly and automated checks do not constitute visual or owner creative approval.

## Recover the finished film first

The complete film has been rendered and checked. Use the saved files in
[Deliveries](../../project-docs/production-system/DELIVERIES.md) and verify the
exact identities in [the final delivery record](../../project-docs/production-system/evidence/s11-renewed-final-delivery.json).
The full-HD delivery and smaller 720p copy are complete 275-second movies.
The original 911,865,528-byte native master is preserved without re-encoding
in two ordinary ZIP archives; its successful restoration is recorded separately.
A missing ignored `work/` directory in a fresh checkout is not an unfinished
render queue.

To recover the exact original master, put both saved ZIP files in one directory,
extract `restore_master.py` from either ZIP, then run:

```bash
python3 restore_master.py --archive-dir .
```

The embedded standard-library script verifies each chunk and the complete
master SHA256 and refuses to overwrite an existing output. No renderer or
third-party Python package is needed for recovery. Keep both archives intact.

## Exact scope of the reviewed host route

`assemble_reviewed.py` applies only to producing commit `eec8d16519ea82309ef851975792e9dfc548da03`, GitHub Actions run `45108198761`, and request `s11-renewed-20261123-master`: 40 parts, 16,500 native 1920×1080 frames at 60 fps, two temporal samples, and a 275-second result.

Two hosted runner images produced different complete runtime fingerprints. The recorded source, request, dependencies, renderer, and render controls match; only the recorded image version and platform string differ. The persisted [review](../../project-docs/production-system/evidence/s11-host-cohort-review.md) explains the evidence and its limits. The [policy](../../project-docs/production-system/evidence/s11-host-cohort-policy.json) enumerates the two exact accepted fingerprints and hashes its supporting evidence. It permits assembly for mandatory final QA; it does not claim byte-identical runtimes or completed visual acceptance.

The assembler loads its request, source manifest, and adapter hashes from the immutable producing commit, not current HEAD. The checkout must contain that Git commit. Original full fingerprints and per-part assignments remain in the assembled receipt. All 40 authenticated picture artifacts, the corresponding private recovery key, and the verified original prepared score are required locally. Do not commit the private key, original recording, prepared score, or decrypted picture artifacts.

## Assemble this reviewed request

Run from the repository root after all 40 encrypted artifacts have been collected. Use a new output name if an existing output or extraction directory is present; existing output is preserved.

```bash
.venv/bin/python -m tools.s11_delivery.assemble_reviewed \
  --encrypted work/s11_cloud/downloaded-master \
  --key work/s11_cloud/private/recipient-private.pem \
  --policy project-docs/production-system/evidence/s11-host-cohort-policy.json \
  --out work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60.mp4
```

This authenticates and checks the artifacts, preserves their original identities, copies the encoded pictures without another picture encode, and adds the verified local score once as AAC at 48 kHz. Its receipt explicitly leaves technical, cross-cohort join, and story/costume QA pending.

## Finalize the original audio with headroom

The initial AAC assembly had a small number of decoded samples above full
scale. The delivered master uses a separate 1 dB attenuation, encoded directly
from the unchanged prepared original score. This step preserves the already
prepared fade/hold and applies no additional offset or picture delay.

```bash
.venv/bin/python -m tools.s11_delivery.finish_audio \
  --video work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60.mp4 \
  --score work/s11_full2/score.wav \
  --out work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60_final.mp4 \
  --receipt work/s11_cloud/audio-headroom-finalization.json
```

It verifies all 16,500 compressed picture payload hashes, PTS, DTS, durations
and sizes against the initial assembly. The actual final stereo sample peaks
were 0.940574 and 0.928012, with no decoded samples at or above full scale.
These measurements are sample peaks, not oversampled true peaks. The initial
assembly and its stage-specific pending checks remain historical evidence;
[final QA](../../project-docs/production-system/evidence/s11-renewed-final-qa.json)
records their completion and the exact final master identity.

## Check the encoded master

```bash
.venv/bin/python tools/s11_delivery/verify.py \
  --video work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60_final.mp4 \
  --score work/s11_full2/score.wav \
  --out work/s11_cloud/final-master-encoded-check.json
```

The check covers the complete decode, dimensions, frame rate, color tags, frame count, presentation timestamps, audio correlation against the original prepared score, and silent ending. A successful receipt is technical evidence; it does not evaluate costume coverage or graceful movement.

## Prepare and perform visual review

```bash
.venv/bin/python tools/s11_delivery/story_review.py \
  --video work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60_final.mp4 \
  --parts 40 \
  --out work/s11_cloud/master-story-review
```

Inspect the extracted sheets and selected native frames. Review before and after every render-part join, and dense short motion intervals across cross-cohort joins, especially joins within the same camera shot. Confirm the story, titles, costumes, compositions, representative performance motion, and ending. Extraction alone is not review. Record observed findings and resolve anomalies before marking final QA passed. Distinguish sampled visual inspection and complete technical decode from uninterrupted playback of the entire film.

The selector balances its FFmpeg expression so the full 311-frame extraction
does not exceed the parser's nesting limit. The actual completed extraction
and all 13 sheets were reviewed; this was a delivery utility repair, with no
change to frozen picture source.

## Make practical complete delivery copies

Preserve the native master before encoding smaller copies. The full-HD copy
keeps every frame at its native 1920×1080 dimensions and 60 fps, with a bounded
H264 bitrate suitable for a single-file download:

```bash
ffmpeg -v error -n \
  -i work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60_final.mp4 \
  -map 0:v:0 -map 0:a:0 -c:v libx264 -threads 4 -preset medium \
  -crf 18 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -g 120 \
  -fps_mode passthrough -color_primaries bt709 -color_trc bt709 \
  -colorspace bt709 -color_range tv -c:a copy -movflags +faststart \
  work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60_delivery.mp4
```

For the 720p60 review copy, use the same finalized master with
`-vf scale=1280:720:flags=lanczos`, `-crf 21`, and no bitrate cap. Keep
`-c:a copy` so each copy retains the exact finalized audio. The actual 720p
encode was made before audio finalization and then remuxed with that exact
final AAC stream; its recorded packet comparison verifies the relationship.
Run `verify.py` for each completed copy with its actual width and height,
inspect representative native output frames for legibility, and record new
file hashes. A smaller encode has its own identity; it does not replace the
original master identity.

## Preserve an exact large master

`archive_master.py` packages consecutive source bytes in ordinary ZIP files,
with a shared manifest, checksums, restoration instructions and a portable
restore script. It executes that script and independently hashes the fully
restored movie before reporting success. It never re-encodes video or audio.

```bash
python3 tools/s11_delivery/archive_master.py \
  work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60_final.mp4 \
  --output-dir work/s11_cloud/master-archive \
  --archive-prefix Almighty_God_Knows_the_Future_Native_Master \
  --chunk-bytes 480000000 --archive-limit-bytes 500000000 \
  --expect-size 911865528 \
  --expect-sha256 c553b2a51f3917d389adc51ee6dc97c96e6b6e9e306a9bfd2bfbe38a89b34c55
```

Use the exact expected source size and SHA256 when packaging. Both completed
archives and the round-trip result are bound in
[the archive receipt](../../project-docs/production-system/evidence/s11-renewed-master-archive.json).
The saved native master is the highest-quality retained render; the smaller
full-HD and 720p versions are convenient delivery encodes of the same film.

The assembler's validation tests are:

```bash
.venv/bin/python -m unittest tools.s11_delivery.test_assemble_reviewed -v
```

## Future requests

Use the original strict `tools.s11_cloud.assemble` route by default. The reviewed route deliberately rejects every new request or unknown full fingerprint, including a new host whose normalized fields otherwise match. A future mismatch requires its own evidence and explicit compatibility review; do not broaden this policy merely to make an assembly pass. Keep the producing picture source separate from later delivery documentation or maintenance commits.
