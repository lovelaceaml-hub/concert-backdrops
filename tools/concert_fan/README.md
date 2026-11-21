# Fan and silk trio

A continuous twenty-second original performance in the approved luminous concert style. Three distinct authored roles, twelve explicit steps per role, two held open fans, and broad simulated silk replace the previous duet's repeated capture and decorative hand trails. The existing approved renderer, rig and garment engine remain unchanged.

This is an original best-effort adaptation. The first two supplied reference posters were inspected, but their moving footage was unavailable. No source choreography or shot timing is reconstructed. See [the current handoff](../../project-docs/production-system/FAN-SILK-PERFORMANCE.md) for the precise delivered media, review coverage and limitations.

## Reproduce

Use a Linux CPU checkout and the locked dependencies. The cloud GPU provider remains unconfigured; the Mac is not used.

```bash
python3 scripts/bootstrap.py --p3d-only --reference-fonts
```

Obtain the selected Song 07 recording from its private catalog entry and place it at `work/song-sources/s07.mp3`. The expected SHA256 is `2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a`. Then:

```bash
.venv/bin/python -m tools.concert_fan.prepare_audio
./scripts/video validate concert-fan-trio
PYTHONPATH=engine:. .venv/bin/python -m unittest tools.concert_fan.test_performance tools.concert_fan.test_props
PYTHONHASHSEED=0 .venv/bin/python -m tools.concert_fan.render \
  --stills 1.4,5.8,7,8.4,14.4,18.6 --width 1920 --height 1080 --samples 2 \
  --out work/fan-silk-performance/native-review
```

The first renderer constructs both deterministic cloth bakes. Later render workers reuse the numeric caches in `work/fan-silk-performance/cloth-cache`. Motion or solver changes invalidate the cache; a camera or garment palette change does not.

Inspect full-size silhouettes and a moving proof before freezing a new round. The renderer is a registered `p3d-kit` scene, so the shared checkpoint/resume and source fingerprint rules apply:

```bash
./scripts/video produce concert-fan-trio --quality review --plan
./scripts/video render concert-fan-trio --quality draft --frames 360:480
./scripts/video produce concert-fan-trio --quality review
.venv/bin/python tools/concert_review/fan.py \
  --baseline project-docs/production-system/evidence/fan-trio-frozen-inputs.json
```

The committed baseline belongs to the exact source round that produced its delivery. A changed picture needs a new separately recorded baseline before rendering; do not overwrite an old baseline to make an audit pass. The auditor never freezes or repairs inputs.

Native 4K is supported by the same geometry and renderer:

```bash
./scripts/video render concert-fan-trio --quality 4k-check --frames 864
```

That command renders the delivered 14.4-second frame at 3840 x 2160. Run it after the 1080p pool has finished. A full 4K film is a distinct production and delivery operation, not a label to place on the 1080p movie. Benchmark memory and elapsed time before the full run.

The original manifest has six single-thread CPU workers and 200-frame chunks. On the roughly 10 GB host used for this study, one 1080p worker terminated during the first full run, and a concurrent 4K attempt also terminated. Their logs do not establish the kill cause. The existing checkpoint system preserved 1,129 1080p frames; the missing 71 were successfully recovered with two workers and 40-frame chunks, without changing the frozen picture fingerprint. The final movie and independent audit both passed.

For a memory-constrained host, this safer sequence preserves the exact manifest and source identity while scheduling at most two 200-frame workers at once:

```bash
for frames in 0:400 400:800 800:1200; do
  ./scripts/video render concert-fan-trio --quality review --frames "$frames" || exit 1
done
./scripts/video produce concert-fan-trio --quality review
```

Use 200-frame ranges for one worker at a time if necessary. Rendered frames are validated and reused on resumption. Do not start a native 4K check concurrently with the 1080p pool.

## The modules

| File | Responsibility |
| --- | --- |
| `performance.py` | Distinct lead, answer and welcome scores; fixed support targets, IK, root travel, torso/head response, hands and fan banking |
| `props.py` | Rigid held fan, constrained finite silk, body capsules, floor contact, numeric bake/cache and diagnostics |
| `fan_trio.py` | Bodies, role placement, garment palettes, camera, mirror lake, distant garden and closing light |
| `render.py` | Software EGL, exact fonts, deterministic frame time, source hashes and native image output |
| `prepare_audio.py` | Verified Song 07 interval, unchanged playback speed, exact fades/gain and canonical WAV hash |

Install a performance before sampling its body or constructing the prop. `install_performance(body, role, duration=20.0)` rejects already sampled actors and conflicting external hand/gesture controls. `FanSilk(...).prebake()` solves the same final hand and body motion that is drawn. Its pinned edge is replaced with the exact grip at every rendered subframe.

The public sample interface remains absolute time. The pose score is pure, the actor time is canonicalized before its cache lookup, and the prop reads immutable baked samples. A worker can render a late frame independently without changing the choreography.

## Review honestly

Tests measure final rig support, continuity, arbitrary seeking, attachment and cache reuse. They do not certify a professional dance performance. The people use authored kinematics and IK, not force-based whole-body balance. Cloth uses an art-directed position based solver with local stretch. It has no self collision, partner collision or collision against the actual garment surface. Full-resolution and encoded motion review remain necessary.

The visual clock was authored for the study; the attached Song 07 excerpt does not make its events musically measured. Source interval: 137.5 to 157.5 seconds. Output: 48 kHz stereo PCM16 WAV, with an 80 ms opening fade, a 600 ms closing fade and -1 dB gain. No new instrument separation or ear-verified transient alignment is claimed.

Keep audio, frames, finished movies and caches in private ignored work paths. Save final media and QA through the shared delivery workflow; store code, fingerprints, instructions and honest review status in Git. Owner approval is a separate recorded event.
