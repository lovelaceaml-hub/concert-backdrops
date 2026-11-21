# Natural dance performance study

This isolated eighteen-second duet develops the approved promo's luminous
people and sweeping motion. Its complete captured dance supplies the torso,
arms, legs, turn and travel. The new performance layer conditions preparation,
support and settlement without changing the approved engine or old films.

The example is a technical and creative study. Consult the production-system
delivery catalog for the actual rendered version, verification and owner review
status. Successful tests do not confer creative approval.

## Reproduce the study

Work from a clean current checkout on a cloud Linux CPU host. The Mac is not
used and the cloud GPU provider remains unconfigured.

```bash
python3 scripts/bootstrap.py --p3d-only --reference-fonts
./scripts/concert verify-audio s07
./scripts/concert prepare-study-audio
./scripts/video doctor --project concert-dance-study
./scripts/video produce concert-dance-study --quality review --plan
./scripts/video produce concert-dance-study --quality review --frames 0,156,252,330,480,648,858,948,1056
./scripts/video produce concert-dance-study --quality review
```

The private Song 07 input must first be restored to the path and exact identity
in `project-docs/production-system/catalogs/songs.json`. The preparation command
validates the canonical eighteen-second score. It retains the source's speed.
Choreography uses an authored visual clock; the recording does not establish
ear-verified musical transients or instrument-specific movement.

The pipeline writes checked frames, a receipt, the encoded movie, technical QA
and a review gallery under `work/pipeline/concert-dance-study/review/`. Repeating
the production command resumes verified frames with the same source identity.
Changing a hashed scene or renderer starts a new round. Finish or intentionally
stop a render before editing its source. A `STOP` file in the quality directory
requests interruption; remove it only when intentionally resuming.

For a genuine native 4K composition check:

```bash
./scripts/video produce concert-dance-study --quality 4k-check --frames 480
```

This renders a 3840 x 2160 frame. The separate full-film preset uses three CPU
workers to leave memory headroom at 4K:

```bash
./scripts/video produce concert-dance-study-4k --quality final --plan
./scripts/video produce concert-dance-study-4k --quality final
```

It requires all 1080 native frames followed by assembly and review. A single
4K still does not certify a full 4K delivery. The measured one-frame 4K worker
peaked at about 1.65 GiB; check the target host and retain headroom. The 1080p
project uses six workers. Neither preset dispatches a GPU or paid service.

## Reuse the motion layer

Create a normal `p3d.body.Body`, then install its performance before sampling
the body or cloth:

```python
from tools.concert_dance.performance import install_dance

performance = install_dance(
    body,
    start=2.0,
    rate=1.0,
    prepare_seconds=2.0,
    settle_seconds=2.5,
)
hand_position = body.where(8.0, "palm.R")
support_evidence = performance.contact_report(sample_times)
```

The default whole phrase lasts 9.333 source seconds plus a 0.24-second clock
envelope. The wrapper retains the final travel and facing during settlement.
Support intervals are calculated once from contact confidence, height, speed
and spread. A selected heel or toe can stay anchored while the foot rotates.
The correction is bounded; this is kinematic cleanup, not a physical balance
or ground-reaction-force solver. Unsupported airborne poses remain airborne.

`clip_start` and `clip_end` select a reviewed subsection. They do not turn a
non-looping performance into a seamless loop. Rates outside 0.75 to 1.25 are
rejected to discourage extreme retiming. New choreography needs its own source
review, contact checks, garment checks and moving example.

The supplied study has two differently placed and scaled bodies, with a
0.6-second phrase offset. It uses the same capture for both. It does not claim
a newly captured duet or an expanded dance library.

## Rendering and art direction

- A continuous camera keeps both bodies and their feet visible through the
  dance. The final widen follows the physical phrase.
- A clear reflective terrace and perimeter planting keep vegetation out of the
  translucent figures.
- Local hand and foot exposure preserves small detail without lowering the
  whole scene.
- Ribbon endpoints use final solved palm positions. Older ribbon material is
  displaced analytically by a gentle air path. These are light trails, not a
  physical silk simulation.
- The world opens after the dance. Authored concluding gestures provide a
  human finish before the wider setting takes over.
- Absolute-time poses and paired hand-track precomputation support independent
  render chunks. No previous worker's frame state defines the choreography.

Native review output is RGB8 SDR at 1920 x 1080 and 60 fps, with two temporal
samples and the established filmic color treatment. The stored capture is
30 Hz, so 60 fps output interpolates its motion. It does not create new captured
detail or imply HDR, 10-bit precision or photorealistic skin.

## Verification and continued improvement

Run the focused regressions after changing the performance or registration:

```bash
.venv/bin/python -m unittest discover -s tests -p test_concert_dance_performance.py -v
.venv/bin/python -m unittest discover -s tests -p test_dance_registration.py -v
```

After full assembly, run the independent native movie auditor:

```bash
env PYTHONHASHSEED=0 .venv/bin/python tools/concert_review/dance.py
```

It checks the exact registered eighteen-second profile, all decoded frames and
presentation timestamps, unchanged frozen sources, canonical audio alignment
and available native reference frames. Read `tools/concert_review/README.md`
for baseline handling and scoped results. This command does not validate the
separate full 4K preset; that requires a matching completed 4K audit profile.

Inspect the actual encoded movie around preparation, toe pivots, airborne
moments, landing, the dance-to-settle transition and ending. Inspect hands and
cloth at native size. Keep measurements separate from artistic judgments.

The next meaningful extensions are independently reviewed motion phrases,
authored hand articulation, costume silhouette improvements during turns and
a duet with complementary actions. Follow the current improvement queue rather
than treating this one capture as sufficient for every concert song.

## Provenance

The unchanged `assets/p3d/body_v1.npz` includes the prepared CMU 05_02 dance,
281 poses at 30 Hz. Its SHA256 is
`0a72159f84b7008dcb135c79f82ae3b05df5f7361197e99ab9ca4af148c91189`.
Retain the asset's existing CMU/NSF and MakeHuman acknowledgement and terms.
The original CMU catalog's 120 Hz capture rate differs from this prepared asset.
Finger and thumb performance was not captured. Read the sourced
`project-docs/production-system/NATURAL-PERFORMANCE-RESEARCH.md` before acquiring
or adapting additional motion.
