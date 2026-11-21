# Local performance reference intake

Create timestamp-verified image references from a local video. This tool does not
download YouTube, reconstruct motion, authorize source use, or mark a performance
visually reviewed. It requires Python, Pillow, FFmpeg and ffprobe on PATH. Use the
project's existing Python environment; no GPU or new provider is required.

## Command

Run from the repository root with a local source acquired through an authorized
route. Keep source media and results in ignored `work/` paths:

```bash
python -m tools.performance_reference \
  --video work/reference-inputs/local-reference.mp4 \
  --source-url 'https://www.youtube.com/watch?v=REFERENCE_ID' \
  --reference-id reference-01 \
  --start 12.25 --end 24.75 \
  --samples 12 --columns 4 \
  --output work/reference-intake/reference-01-12.25-24.75-v1
```

Direct invocation also works:

```bash
python tools/performance_reference/intake.py --help
```

Use `--purpose pipeline_fixture` for a generated fixture or an existing project
movie used to check this pipeline. It prominently labels the contact sheet and
manifest so that test media cannot be mistaken for one of the owner's references.

An existing output directory is always refused, including an empty directory.
Choose a new versioned destination. Output inside this checkout must be ignored
by Git. The tool never changes `.gitignore`. External output directories are
allowed; keep those out of any media-forbidden repository too.

## Timestamp contract

- `--start` and `--end` are exact decimal seconds **relative to the first decoded
  video frame**, not the audio start, file's format start, or absolute source PTS.
  The interval includes start and excludes end: `[start, end)`.
- ffprobe enumerates decoded frame PTS. Samples are the nearest available frames
  to uniformly spaced interval centres, constrained to that interval. A tie
  chooses the earlier decoded frame. Sparse or variable-rate media can produce
  fewer unique frames than the requested sample count; all original target times
  remain in the manifest. No duplicate image is fabricated to fill a grid.
- The tool decodes sequentially and selects frame indices, with no approximate
  seek and no frame-rate resampling. FFmpeg `showinfo` timestamps must equal the
  selected ffprobe timestamps exactly as rational times. Nonzero/negative initial
  PTS and variable frame spacing are retained.
- Each sample records the requested target times, actual relative time, source
  integer PTS and time base, and independently decoded PTS. The source PTS offset
  is explicit. Read the exact rational fields when submillisecond precision
  matters; displayed timecodes are rounded to milliseconds.
- Missing PTS or non-monotonic decoded presentation timestamps are rejected.
  A range with no in-range frames is rejected. A range extending beyond the
  decoded coverage is rejected when the final frame's duration is reported.
  Without that duration, `known_coverage_end_seconds` is null and the requested
  end cannot exceed the last proven frame timestamp. The effective limit is
  recorded as `proven_request_end_limit_seconds`.

## Supported local media and bounds

Only self-contained MOV/MP4, Matroska/WebM, AVI, MPEG/MPEG-TS, FLV, Ogg, ASF, MXF
and NUT containers are supported. Both probing and decoding allow only the local
`file` protocol and that container allowlist. HLS, DASH, concat and other playlist
or segmented inputs are rejected, including local playlists: hashing a playlist
does not establish the identity of its dependencies. No URL is fetched.

The selected video must report square sample pixels, SAR `1:1`. Anamorphic SAR is
rejected so a dancer's proportions are not silently distorted. Unspecified SAR
is also rejected by default. If the source is independently known to have square
pixels, pass `--assume-square-pixels`; the manifest records a caller assertion,
not signaled geometry. This option never overrides a declared non-square SAR.
Otherwise prepare a separate, correctly converted square-pixel viewing copy and
record its provenance. Normal display rotation still applies. Raw PNGs keep
native decoded dimensions; narrow timecoded copies add side padding to make
labels readable without rescaling the raw frame.

The tool enumerates the full source before selecting frames. Use short local
clips: input is limited to 2 GiB, 1800 seconds of decoded video span and 120000
decoded frames. A reported video-stream duration over 1800 seconds is rejected
before enumeration; the actual span/frame limits are checked after enumeration.
Each external command has a 300-second timeout. These practical limits are not a
streaming decoder or a promise of fixed memory use for malformed media.

## Outputs and review

| Output | Purpose |
| --- | --- |
| `manifest.json` | Input SHA256, source URL/ID, exact segment, selected timestamps, output hashes, annotation slots and separate review states |
| `source-probe.json` | Original stream/format metadata from ffprobe |
| `frames/` | Native decoded PNGs, without timecode bands |
| `timecoded/` | Viewing copies with actual relative time and source PTS |
| `contact-sheet.jpg` | Readable overview for selecting poses and camera moments |
| `decode.log` | FFmpeg evidence used to verify actual decoded timestamps |

The tool hashes the input before and after processing. Its URL-to-local-file
relationship is caller-provided and remains explicitly unverified. Stream `v:0`
is sampled. FFmpeg's normal display rotation applies. PNGs and thumbnails are
viewing aids, not a color-mastering or HDR proof.

The manifest initializes shot, performer, contact and uncertainty annotation
arrays plus templates. Add observations in the same first-frame-relative clock,
with sample indices as evidence. Record obscured or ambiguous contacts instead
of inventing hidden motion. Do not promote a candidate contact into a measured
3D constraint from these 2D samples alone.

Acquisition, technical extraction, visual review and owner approval have separate
statuses. Successful extraction sets only the technical status to passed. Watch
the continuous selected passage before judging fluidity. The owner must approve
an exact output before recording owner approval. If a run fails after output
creation, `INTAKE-INCOMPLETE.txt` and `failure.json` identify the partial result;
retry into a fresh destination.

## Focused verification

```bash
python -m unittest tools.performance_reference.test_intake -v
```

The integration fixture is generated locally with five irregular frame times
and a source PTS start at five seconds. The checks exercise true VFR/nonzero-PTS
decoding, the exclusive range boundary, deduplicated sample targets, media
hashes, review-state separation, an empty-frame interval, protected code paths
refusal to overwrite an existing result, unknown final-duration coverage,
playlist rejection and non-square pixel rejection. No reference video is downloaded.
