# Independent review of the Consideration studies

`consideration.py` checks two explicitly registered review masters. The profile
is selected by project ID, not inferred from the movie's duration. Both require
native 1920 x 1080, 60 fps, two temporal samples, RGB8 source frames, and the
established legacy display gamma SDR color contract.

| Project ID | Output | Visual source clock | Canonical WAV interval | Authored cuts |
| --- | --- | --- | --- | --- |
| `concert-kit-consideration` | 18 seconds, 1080 frames | Original frames 0 through 1079 | 0 through 18 seconds | Output frames 180 and 720 |
| `concert-kit-consideration-v2` | 15 seconds, 900 frames | Revised performance, original frames 180 through 1079 | 3 through 18 seconds | Output frames 234 and 540 |

Time intervals are start-inclusive and end-exclusive; listed frame ranges
include both endpoint frames. The v2 picture uses the
separate corrected motion wrapper; it is not just a trim of the old movie.
Its audio is a trim of the exact canonical WAV at unchanged speed, with no
additional gain or fades. That WAV already contains the documented original
gain and ending fade. V2 covers original Song 07 from 140.5 to 155.5 seconds;
v1 covers 137.5 to 155.5 seconds.

This is not a generic auditor for all concert songs, alternate durations or
other quality presets. A different contract needs an explicit profile and
appropriate source evidence. Unsupported scene, cut, audio or finishing
changes are rejected.

The tool reads sources, receipts, audio and media. It imports no scene renderer,
creates no graphics context, and does not rerender, re-encode, repair or replace
production output. Its new files stay under ignored
`work/production-system/final-qa/`.

## Prerequisites

Use the repository's locked Python environment, including NumPy, SciPy and
Pillow, and working host FFmpeg and FFprobe executables. The script uses
FFmpeg's `-fps_mode passthrough` and software `scale` filter. No GPU, Blender,
browser or connected account is required once private inputs exist locally.
It decodes the complete movie and several selected native frames, so allow
tens of seconds on a prepared cloud CPU machine. This is not a render job.

The full original recording and the prepared WAV are private inputs, not Git
files. Restore Song 07 and run `./scripts/concert prepare-study-audio` as
described in [START-HERE](../../project-docs/production-system/START-HERE.md).
Required inputs include:

- `work/concert-kit/consideration-score.wav`, canonical PCM24, 48 kHz stereo,
  864000 samples per channel. Expected file SHA256:
  `0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b`.
- `work/concert-kit/audio-provenance.json`, identifying the original Song 07
  source interval and unchanged playback speed.
- The selected registered project, its preparation record, shot receipts and
  checksummed source PNGs under `work/pipeline/<project-id>/`.

The final check also requires completed `master.mp4`, `master.json` and
`qa.json` in `work/pipeline/<project-id>/review/`. It does not poll for a
running production to finish.

## Freeze before the full render

For the corrected 15-second study, first produce and inspect the normal native
preview, then capture a baseline from its actual `contact` receipt:

```bash
./scripts/video produce concert-kit-consideration-v2 --quality review --frames 0
uv run --frozen --extra legacy python tools/concert_review/consideration.py --project concert-kit-consideration-v2 --freeze-only
```

This checks the exact project and audio contract, receipt fingerprint,
recorded source file bytes, and the prepared module's source clock. It writes
`work/production-system/final-qa/concert-kit-consideration-v2/frozen-inputs.json`
once and refuses to overwrite an existing baseline. The baseline captures
picture inputs, common provenance and the manifest's picture contract before
final assembly.

For a new reproduction of the original 18-second profile, use its project ID
in both commands. Omitting `--project` also selects that original profile.
Its baseline remains at `work/production-system/final-qa/frozen-inputs.json`.
The new profile never replaces the historical baseline or its audit runs.

The original completed 18-second movie and its audit belong to historical
source checkpoint `673f68785c36b57d55d05129ee5549efe6352c60`. Later changes to
the registered adapter intentionally make that old baseline fail against the
current tree. Use the matching checkout for historical reproduction, or an
isolated, newly frozen round. Do not relabel old receipts as current.

Do not regenerate a baseline to hide a source mismatch. For an intentional new
round, finish or stop the current round, preserve its audit directory under a
distinct ignored name, and create a fresh baseline from a current preview
receipt. Do not run font setup or change any frozen dependency during rendering.

## Audit the completed movie

```bash
./scripts/video produce concert-kit-consideration-v2 --quality review
uv run --frozen --extra legacy python tools/concert_review/consideration.py --project concert-kit-consideration-v2
```

The first command is the existing resumable production route. If the movie and
pipeline QA are already complete, run only the second command. In an already
prepared checkout, `.venv/bin/python` can replace `uv run --frozen --extra
legacy python` without synchronizing the environment.

Each audit creates a unique `run-<UTC timestamp>/` inside the profile's audit
directory. It contains `independent-qa.json`, selected native decoded PNGs, a
cut and batch boundary contact sheet, and the decoder error log. A failed
technical check returns a nonzero exit status. Review warnings and actual
pictures even when technical checks pass.

## What the evidence means

The audit checks full video decoding, every presentation timestamp at exact
1/60-second spacing, native dimensions, exact profile frame count and duration,
H.264 pixel format, and BT.709 primaries, transfer, matrix and limited-range
tags. It verifies the master hash, assembly identity, shot receipt coverage,
frozen source mapping and finishing inputs.

Audio checks include 48 kHz stereo, exact stream program duration, decoded
full-scale exceedances, the canonical 24-bit PCM payload, the profile's exact
sample offset, and correlation in three nonsilent windows spread across the
excerpt. They also bound amplitude differences from the unchanged canonical
excerpt. AAC priming is handled by normal FFmpeg demuxing and decoding; trailing
partial-frame padding is recorded separately from the logical sample count.
Sample alignment is technical evidence, not artistic or musical sync approval.

Selected encoded frames are compared with their checksummed source PNGs using
the inverse limited-range BT.709 matrix and range conversion only. No extra
gamma or transfer conversion is applied. Selection includes fixed performance
moments, eight repeatable random frames, and neighbors of actual cuts and
worker-batch boundaries. The generous mismatch bounds catch gross identity or
encoding errors; they are not a beauty score. Batch boundaries come from render
logs and remain distinguished from authored camera cuts.

The audit does not claim real-time playback, natural acting, distinct native
motion capture samples at every output frame, exact finger interlock, complete
visual review or owner approval. It rehashes selected source PNGs and verifies
full receipt coverage; the separate pipeline QA verifies the complete source
sequence.

## Separate numerical response regression

The motion change has an additional focused checker, owned separately from
the media auditor:

```bash
env PYTHONHASHSEED=0 uv run --frozen --extra legacy python tools/concert_review/response.py --out work/concert-motion-review/response-qa.json
```

It samples the actual paired skeleton and installed response at 120 Hz and
60 Hz, checks the release transition, earlier contact, order independence and
duplicate-install protection, and saves compact metrics plus separate full raw
data. It uses one CPU for roughly 80 seconds, without OpenGL, cloth or picture
rendering. Its numerical regression result does not establish natural acting
or replace inspection of the encoded movie. See its recorded method and source
identities before comparing different revisions.

## Independent natural dance audit

`dance.py` audits the registered `concert-dance-study` review master: one
continuous eighteen-second shot, 1080 native 1920 x 1080 frames at 60 fps, and
the complete canonical eighteen-second WAV at offset zero. It uses an empty
authored-cut list and the dance registration's own clock.

After `master.mp4`, `master.json` and the complete `performance` shot receipt
exist, run from the repository root:

```bash
env PYTHONHASHSEED=0 .venv/bin/python tools/concert_review/dance.py --movie work/pipeline/concert-dance-study/review/master.mp4 --audio work/concert-kit/consideration-score.wav --baseline project-docs/production-system/evidence/natural-dance-frozen-inputs.json
```

The tracked baseline is the existing frozen picture round, with its 197 source
hashes. `--baseline work/natural-performance/frozen-round.json` can select the
equivalent working record explicitly. A deliberately changed scene needs a
new frozen round and new receipts; do not replace a baseline to hide a source
mismatch. The auditor never creates or repairs a baseline.

To check restored sources and the canonical score before the movie exists:

```bash
env PYTHONHASHSEED=0 .venv/bin/python tools/concert_review/dance.py --inputs-only --baseline project-docs/production-system/evidence/natural-dance-frozen-inputs.json
```

This limited mode reports `technical_passed: null` and `movie_audited: false`.
It does not establish a completed movie audit. Both modes return nonzero on
their technical errors and create a new timestamped directory under
`work/production-system/final-qa/concert-dance-study/`. `--out-dir` can choose a
new directory explicitly; existing directories are not overwritten. Keep the
printed `independent-qa.json` and accompanying frame-decode evidence.

The full audit checks the frozen source mapping before and after review,
registered clock, completed shot coverage, assembly/movie identity, finishing
inputs, every presentation timestamp and a complete native FFmpeg decode of
all 1080 frames. It verifies the canonical PCM payload, full-program AAC
correlation and three nonsilent alignment windows spread across the score,
including lag and gain. Normal AAC priming handling and trailing padding are
reported separately. Native source PNGs for frames 360 and 480 are checked
against their receipt hashes and compared with decoded RGB when available.
Missing reference PNGs are reported, never silently treated as comparisons.

The tool imports no renderer and starts no render. It does not certify natural
acting, physical contact, fingers, cloth, artistic synchronization or owner
approval. Its 1080p result does not establish a full 4K movie. Read the JSON's
limitations and inspect the encoded performance even when technical checks pass.

## Narrow auditor tests

```bash
uv run --frozen --extra legacy python -m unittest discover -s tools/concert_review -p 'test_*.py' -v
```

These cover explicit project clocks, rejected source/offset/finishing changes,
separate baseline paths, repeatable sample selection and measured lag sign.
They neither render scenes nor substitute for the completed movie audit.

## Font bytes and historical receipts

Exact historical receipt reuse requires the matching source checkout, recorded
runtime and original font bytes. In a fresh checkout of current source, use
`python3 scripts/bootstrap.py --p3d-only --reference-fonts` to reconstruct the
exact 74 study TTFs from the pinned WOFF2 files and checked metadata. See
[REFERENCE-FONTS.md](../../docs/REFERENCE-FONTS.md). Normal deterministic
conversion retains source timestamps and therefore has different file hashes.

The original baseline checkpoint `673f68785c36b57d55d05129ee5549efe6352c60`
predates this bootstrap flag. To reproduce that historical checkout, first
reconstruct and verify the fonts in a separate checkout of setup checkpoint
`3aaa7c5d75a01704c984b60c33cfc2a0bb807b5f` or current source, then copy those
verified TTF files unchanged into the historical checkout's `fonts/` directory.
Keep the recorded runtime and matching source there; do not apply the new
bootstrap flag to the older script or modify its guards.

Create and verify a new render receipt and audit baseline in each new working
round; never substitute historical fingerprints to conceal different inputs.
