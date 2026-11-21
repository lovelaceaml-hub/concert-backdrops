# Natural performance handoff

## What is reusable now

`concert-dance-study` is a registered eighteen-second, continuous dance example built around the existing CMU 05_02 phrase. Its isolated performance layer preserves root travel through the ending, calculates stable support intervals, allows a supported heel or toe to pivot, and evaluates poses at absolute time. The source engine and approved films remain unchanged. The reusable model catalog entry is `people.natural-dance` in the existing acting family.

The picture round is pinned to source commit `0c42f4422a6b67464cb9cd84aac32008d45d4f4c`, PR #104. Read [STATE.json](STATE.json), [DELIVERIES.md](DELIVERIES.md) and [catalogs/deliveries.json](catalogs/deliveries.json) for completed media, exact identities, evidence and owner review. The complete native 1080p60 movie has passed both technical audits, is saved and has a raw-byte-verified Drive copy. The single native 4K frame is also delivered. The independent visual review covers 89 targeted final-film samples, with the earlier 62-sample silent proof preserved separately. Owner approval remains unrecorded.

The historical ZIP delivered to Production System is an immutable snapshot. Use current `main` for the latest merged source and documentation; consult the open PR for any increment still awaiting merge. Future handoff exports now include both dance project manifests and the tool README. Preserve the delivered archive's exact bytes instead of rebuilding it under the same identity.

## Reproduce on a cloud CPU host

First restore the private Song 07 input to the exact path and hash recorded in [catalogs/songs.json](catalogs/songs.json). Then use these commands from the [study README](../../tools/concert_dance/README.md):

```bash
python3 scripts/bootstrap.py --p3d-only --reference-fonts
./scripts/concert verify-audio s07
./scripts/concert prepare-study-audio
./scripts/video doctor --project concert-dance-study
./scripts/video produce concert-dance-study --quality review --plan
./scripts/video produce concert-dance-study --quality review --frames 0,156,252,330,480,648,858,948,1056
./scripts/video produce concert-dance-study --quality review
```

The review preset renders all 1,080 frames at native 1920 x 1080, 60 fps and two temporal samples. It writes frame receipts, the movie, technical QA and a gallery under `work/pipeline/concert-dance-study/review/`. Rerunning resumes verified frames when their source identity matches. A `STOP` file in that quality directory interrupts dispatch; remove it only for an intentional resume. Finish or stop a round before editing its picture inputs.

Run the independent audit after the complete movie is assembled:

```bash
env PYTHONHASHSEED=0 .venv/bin/python tools/concert_review/dance.py
```

The [auditor guide](../../tools/concert_review/README.md) explains its explicit frozen baseline and separate timestamped reports. The [delivered audit](evidence/natural-dance-independent-qa.json) checks all 1,080 decoded frames and exact presentation times, the canonical score and three audio windows at zero-sample lag, 197 unchanged picture inputs and two native reference comparisons. It does not replace normal-speed artistic review. The completed delivery's [visual evidence](evidence/natural-dance-visual-review.json) records the long preparation, raised-foot settle and final held gestures for the next creative pass.

For a native 4K detail check:

```bash
./scripts/video produce concert-dance-study --quality 4k-check --frames 480
```

This requests one 3840 x 2160 frame. The separate `concert-dance-study-4k` project is configured for the same eighteen-second clock, native 3840 x 2160 output and three CPU workers:

```bash
./scripts/video produce concert-dance-study-4k --quality final --plan
./scripts/video produce concert-dance-study-4k --quality final
```

Its full 4K movie remains unrendered at this handoff. A complete delivery needs all 1,080 native frames, assembly and encoded review. Neither a valid plan nor the completed single-frame check establishes a full 4K movie. The Mac and an external GPU provider are not used.

## Reuse and honest limits

Create a normal `p3d.body.Body`, then call `install_dance(body, ...)` from `tools.concert_dance.performance` before sampling its actor or cloth. Use final solved palm anchors for trails or attachments. `contact_report(times)` exposes support intervals, weights, residuals and floor measurements for review. Copy the working API example from the study README.

- Both performers use the same existing capture, delayed by 0.6 seconds. This is not a newly captured or independently choreographed duet.
- The prepared asset has 281 poses at 30 Hz. Native 60 fps rendering interpolates those poses; it does not create new captured detail. The original CMU recording's 120 Hz rate is a separate provenance fact.
- Finger and thumb motion was not captured. Current hand detail and procedural movement do not establish realistic authored finger performance.
- Support cleanup uses bounded kinematic correction, not force or balance simulation. Light trails follow wrist history with analytic drift; they are not simulated silk.
- The existing score retains its established speed and preparation. The visual timing is authored, with no claim of ear-verified transients or instrument-specific choreography.
- Output uses RGB8 SDR and the established display curve. Greater spatial resolution does not imply HDR or 10-bit precision.

Retain the CMU/NSF and MakeHuman provenance in `assets/p3d/README.md`. Read [NATURAL-PERFORMANCE-RESEARCH.md](NATURAL-PERFORMANCE-RESEARCH.md) for primary-source terms and capture limitations before acquiring further motion. [MOTION-LIBRARY.md](MOTION-LIBRARY.md) inventories the compiled clips and separates proposed acquisitions from available assets.

## Verification and resource evidence

The focused implementation checks passed as recorded for this increment:

| Check | Passed | Command |
| --- | ---: | --- |
| Actual captured pose, support and transition behavior | 4 | `.venv/bin/python -m unittest discover -s tests -p test_concert_dance_performance.py -v` |
| Registered clock, parameters and source identity | 7 | `.venv/bin/python -m unittest discover -s tests -p test_dance_registration.py -v` |
| Parallel ownership, interruption, failure and caching | 7 | `.venv/bin/python -m unittest discover -s tests/pipeline -p test_parallel_render.py -v` |
| Existing cache and recovery regressions | 11 | `.venv/bin/python -m unittest discover -s tests/pipeline -p test_cache.py -v` |

These checks support correctness and recovery. Inspect the actual encoded motion, feet, hands, garment turns, transition boundaries and final settlement to judge visual quality.

The completed frozen 1080p round used six single-thread workers and twelve 90-frame chunks. The largest measured worker peak was 1,193,408 KiB, about 1,165.4 MiB. Summed worker initialization time was 1,211.545 seconds and summed frame time was 5,754.656 seconds; those times overlap across concurrent workers and are not total elapsed time. The [implementation evidence](evidence/natural-dance-implementation.json) retains every worker measurement and the earlier, separately scoped profile. Remeasure memory before increasing resolution or scene complexity.

The actual native 4K frame worker peaked at 1,734,260 KiB, about 1.65 GiB. The configured `concert-dance-study-4k` project uses **3 workers for a future full 4K run on this host**, compared with **6 for the current 1080p project**. Keep the 4K scope explicit: one frame has rendered, with completion evidence retained by the delivery catalog; this does not certify a full 4K movie or its maximum memory. Recheck live memory when the full sequence runs, and select lower concurrency if other jobs share the host.

## Next concrete improvement

Review the complete dance, then develop a complementary duet with a distinct answering phrase. Expand only through independently reviewed motion sources, authored hands and costume tests during turns. Preserve the eleven song-specific proposals and unresolved issues in [IMPROVEMENT-QUEUE.md](IMPROVEMENT-QUEUE.md). These acting additions leave the existing nine new geometry families and eighteen variants unchanged.
