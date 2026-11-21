# Original fan and silk performance

November 21, 2026, America/Los_Angeles.

## Owner direction

The owner asked to try the three supplied dance/theatre references as well as possible, continuing in the approved Mother's Words of Love style. This supersedes the earlier instruction to wait for source files before doing useful original work. Accurate source choreography still requires inspected moving footage, but that missing input does not block an explicitly original study.

## What is built

`concert-fan-trio` is a twenty-second continuous scene with three distinct authored roles, two open fans with finite silk sheets, a changing formation and an ending over the mirror lake. It uses the existing approved rig, garment engine and native p3d renderer without modifying their files.

The lead opens a fan phrase, the answer follows with a different hand/turn score, and the welcome performer advances through the formation. The outside dancers carry their own fans throughout. No prop handover, partner lift or aerial act is present. Head, torso, free fingers, fan grip and stepping are authored together. The final light response begins from actual silk-edge positions.

The [module README](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/tools/concert_fan/README.md) gives exact commands. `projects/concert-fan-trio/project.json` registers 1,200 output frames at 60 fps. The selected music is the verified original Song 07 interval from 137.5 to 157.5 seconds, with unchanged playback speed and recorded gain/fades.

## Saved outputs and review

| Saved file | Verified Drive copy | Contents |
| --- | --- | --- |
| [Fan-Silk-Trio-20s-1080p60.mp4](https://chatgpt.com/library?file_id=libfile_5d95a136726c8191a7eacbf8509a9bec&account_id=personal) | [Open in Drive](https://drive.google.com/file/d/1e4p1pwcjfhZN35lD-ducwa_mU2_M5dsh/view?usp=drivesdk) | Original continuous trio with distinct authored roles, grounded steps, held fans, finite silk, mirror lake and a gentle closing pose. Not reconstructed source choreography. |
| [Fan-Silk-Trio-Native-4K.png](https://chatgpt.com/library?file_id=libfile_401345b49ea88191a3d6ba7e0c794939&account_id=personal) | [Open in Drive](https://drive.google.com/file/d/1r3NL97rDqXL1waC_gKflb7cODqh7n0dV/view?usp=drivesdk) | One separately rendered native 3840 x 2160 frame. No upscaling; a full 4K movie is not included. |
| [Fan-Silk-Trio-Motion-Review.jpg](https://chatgpt.com/library?file_id=libfile_0a92fd2387848191a628133b595d7be6&account_id=personal) | [Open in Drive](https://drive.google.com/file/d/1x418ePl741G1Ooo0cZHzwwYirYxFQXG3/view?usp=drivesdk) | Nine labeled frames decoded from the final movie, with uniform scaling and no brightness or content edits. |

The independent final-film review covers 37 ordered decoded samples, including all seven requested render-boundary pairs and the final 1.2 seconds. A separate nine-frame overview and the native 4K still were inspected by the coordinator. No blocker was found in the covered samples. Silk still crosses the head or upper body in some bank poses and mostly hangs as a long folded panel. The choreography is gentle and ceremonial. Exact foot contact is supported by rig diagnostics; long costumes conceal it visually. No real-time playback or creative approval is claimed.

## What the references actually supplied

The cloud browser retry again stalled at time zero with no decoded video frame. The first two posters could be inspected. The third reference supplied title/channel metadata only. No sign-in wall or explicit bot denial was encountered; the player simply did not deliver usable motion.

| Reference | Usable observation | Use in this study |
| --- | --- | --- |
| Fei Tian Dancers, Upwards to the Moon | Three performers in asymmetrical triangular staging; open fans carrying broad attached fabric; lavender outer layers and flowing white lower garments; black backdrop | Three distinct roles and broad held fan fabric, redesigned as code-drawn light. The modest long skirts are this production's design choice, not a claim about every source garment. |
| Cirque du Soleil, The Beatles LOVE trailer | Bright yellow car, ensemble at multiple elevations, saturated stage light and separated silhouettes | A reminder to use deliberate ensemble depth and a clear visual hierarchy. No trailer action, car, lift or aerial apparatus is recreated. |
| Pilinh Dance, Song Dien Yen Tuan | Metadata only | No costume, prop or choreography detail is attributed to this video. |

The approved promo was reacquired and verified against its cataloged SHA256, then sampled at nine times for the luminous body, colored light, dark-sky and mirror-water language. These comparison samples are still-frame review, not new real-time playback evidence.

## Improvements that matter visually

1. Each performer has a separate score instead of sharing the same short capture with a time offset.
2. Twelve explicit steps per person carry the root motion. Planted feet retain world position and orientation; the body does not slide over them.
3. Fingers, free wrists and torso/head direction support the phrase. The free hands extend diagonally while the fans rise, avoiding a repeated both-elbows-up silhouette.
4. Fans follow the final solved hand. Their bank is staggered between lead and answer, so the fabric changes plane with the gesture.
5. Each finite silk sheet has a 319-node physical approximation, saved at 60 Hz from a 120 Hz solve. Its surface is drawn as translucent light, with restrained ribs and hems.
6. The camera was brought closer after the first review. Reduced body-mask strength removed the heavy dark halo, while selective body light restored the promo's focus without lifting the whole sky.
7. Actual cloth caches are reused across camera iterations. Longer CPU chunks reduce repeated garment-history setup. The final run recovered 71 missing frames from a terminated worker without redrawing the other 1,129; the README records a lower-concurrency reproduction sequence.

## Evidence and limits

The native 1080p60 movie is complete: 20 seconds, 1,200 frames and two temporal samples. Both pipeline and independent technical audits passed without errors or warnings. The independent auditor verified the unchanged 201-file picture mapping, full decode, exact frame presentation times and three zero-lag audio windows. Technical checks, sampled visual review and owner creative approval remain separate. The delivery catalog records the exact saved outputs.

The seven focused motion/prop checks cover deterministic final skinning matrices, stable support, foot clearance, wrist continuity, immediate entry, ending pose, arbitrary prop seeking, finite cloth, floor contact and cache reuse. Full-motion cache measurements record submicrometre pin residuals and no free-node floor penetration. They also record approximately 11 to 12 percent 99th-percentile structural strain and larger local maxima. These are solver diagnostics, not a claim that this represents a measured silk fabric.

This is authored kinematic dance with IK. It does not use a new motion-capture library, physical whole-body balance, automatic professional choreography or reconstructed YouTube motion. The cloth has body capsule and floor contact, but no self collision, partner collision or exact costume-surface collision. The hands and hems still require visual judgment in the rendered film.

## Next quality work

[The next performance upgrades](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/NEXT-PERFORMANCE-UPGRADES.md) records the primary-source research, a concrete six-second whole-body proof, optional action baking and the separate motion-annotation candidate. Those items remain future work.

Use the delivered study as the next concrete comparison. The highest-value continuation is a richer complete dance phrase: an expressive turn, deliberate arrival, changed level and clear recovery, with the camera keeping feet and fan shapes readable. Refine the real skirt silhouette and silk during reversal before adding crowd scale. For faithful adaptations, ingest source videos through the existing reference tool and annotate support, grip, rhythm and recovery from actual footage.

To take this across all concert songs, preserve the division between an authored performance score, the final solved body/contact state, its cached garment/prop response, the campaign's light style and the song-specific camera/music edit. A reusable rig or constructor is only a starting point; every new phrase still needs an actual moving review.


# Exact reproduction commands and implementation contract

# Fan and silk trio

A continuous twenty-second original performance in the approved luminous concert style. Three distinct authored roles, twelve explicit steps per role, two held open fans, and broad simulated silk replace the previous duet's repeated capture and decorative hand trails. The existing approved renderer, rig and garment engine remain unchanged.

This is an original best-effort adaptation. The first two supplied reference posters were inspected, but their moving footage was unavailable. No source choreography or shot timing is reconstructed. See [the current handoff](https://github.com/lovelaceaml-hub/concert-backdrops/blob/main/project-docs/production-system/FAN-SILK-PERFORMANCE.md) for the precise delivered media, review coverage and limitations.

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
