# Independent review of the Consideration study

`consideration.py` independently checks the registered
`concert-kit-consideration` review master. Its scope is this exact **18-second,
1920 x 1080, 60 fps, 1080-frame study**, with the established RGB8 SDR color
contract and canonical Song 07 excerpt. It is not a generic auditor for all
concert songs or alternate quality presets.

The tool reads sources, receipts, audio and media. It imports no scene renderer,
creates no graphics context, and does not rerender, re-encode, repair or replace
production output. Its new files stay under ignored
`work/production-system/final-qa/`.

## Prerequisites

Use the repository's locked Python environment, including NumPy, SciPy and
Pillow, and working host FFmpeg and FFprobe executables. The script uses
FFmpeg's `-fps_mode passthrough` and the software `scale` filter. No GPU,
Blender, browser or connected account is required to run the audit once the
private inputs exist locally.

The full original recording and the prepared WAV are private inputs, not Git
files. Restore Song 07 and run `./scripts/concert prepare-study-audio` as described
in `project-docs/production-system/START-HERE.md`. The audit requires:

- `work/concert-kit/consideration-score.wav`, canonical PCM24, 48 kHz stereo,
  864000 samples per channel. Expected file SHA256:
  `0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b`.
- `work/concert-kit/audio-provenance.json`, identifying original Song 07 from
  137.5 to 155.5 seconds at unchanged speed. The prepared excerpt already includes
  its documented gain and fades.
- Registered shot receipts and their source PNGs under
  `work/pipeline/concert-kit-consideration/review/shots/`.

The final check additionally requires completed `master.mp4`, `master.json` and
`qa.json` in `work/pipeline/concert-kit-consideration/review/`. It does not poll
for a running production to finish.

## Before the full render

First inspect the normal native preview. The baseline command uses the existing
`approach` receipt to record the actual sources used by a render, so a completely
fresh checkout needs at least one registered preview frame before freezing:

```bash
./scripts/video produce concert-kit-consideration --quality review --frames 0
uv run --frozen --extra legacy python tools/concert_review/consideration.py --freeze-only
```

`--freeze-only` checks that the receipt fingerprint is internally consistent,
that its recorded source files still have the same bytes, and that the canonical
WAV matches. It writes `work/production-system/final-qa/frozen-inputs.json` once
and refuses to overwrite an existing baseline. It captures the picture contract,
common provenance and source mapping separately from the finished movie.

For the first production-system study, this baseline was captured while the
already-frozen production was running and matched its earlier `approach` receipt.
That historical baseline is preserved. Future rounds should capture theirs
before the full render as shown above.

Do not regenerate a baseline to hide a source mismatch. When starting an
intentional new round, first finish or stop the current round, preserve its audit
directory under a distinct ignored name, and create the new baseline from a
current preview receipt. Do not run font setup or change any frozen dependency
during rendering.

## After the full render and pipeline QA

```bash
./scripts/video produce concert-kit-consideration --quality review
uv run --frozen --extra legacy python tools/concert_review/consideration.py
```

The first command is the existing resumable production route. If the movie and
its pipeline QA are already complete, run only the second command. In an already
prepared checkout, `.venv/bin/python` can replace `uv run --frozen --extra legacy
python` without synchronizing the environment.

Each independent audit creates a unique `run-<UTC timestamp>/` directory
containing `independent-qa.json`, selected native decoded PNGs, a cut and batch
boundary contact sheet, and the decoder error log. The process exits with a
nonzero status for a failed check. Review warnings and the actual pictures even
when technical checks pass.

## What the evidence means

The audit checks complete video decoding, 1080 presentation timestamps at exact
1/60-second spacing, native dimensions, stream duration, H.264 pixel format and
BT.709 primaries, transfer, matrix and limited-range tags. It verifies the master
hash, assembly identity, shot receipts, frozen sources and finishing inputs.

Audio checks include 48 kHz stereo, exact 18-second stream program duration,
decoded full-scale exceedances, the canonical PCM payload, and correlation in
three nonsilent windows spread across the excerpt. AAC priming is handled by the
normal FFmpeg demuxer and decoder. Any trailing partial AAC frame is recorded
separately from the logical program sample count. Sample alignment is technical
evidence; it does not establish artistic or musical synchronization.

Selected decoded frames are compared with their checksummed source PNGs using
the inverse limited-range BT.709 matrix and range conversion only. No second
gamma or transfer conversion is applied. The generous mismatch bounds detect
gross identity or encoding errors; they are not a beauty score. Worker boundaries
come from actual render logs and are distinguished from authored camera cuts.

The audit does not claim real-time playback, natural acting, distinct native
motion-capture samples at every output frame, exact finger interlock, complete
visual review or owner approval. It does not independently rehash every rendered
PNG; it checks selected source PNGs and the full shot receipt coverage, and also
reads the existing pipeline QA, which verifies the complete source sequence.
