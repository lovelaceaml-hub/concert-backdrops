# Native 4K and smoother animation

This extends the repeatable pipeline with actual 16-bit Blender PNGs, native
3840 x 2160 delivery, reusable camera and character animation, baked motion blur,
resumable frame rendering, and technical motion review. It does not revise the
approved concert films or their audio. The cloud GPU provider remains null.

## Start a new project

From the repository root after the locked bootstrap:

```bash
./scripts/video new "My next film" --template cinematic --fps 60 --seconds 10
./scripts/video validate my-next-film
./scripts/video motion-qa my-next-film
./scripts/video preview my-next-film --quality motion-check
./scripts/video storyboard my-next-film --quality review --render
./scripts/video preview my-next-film --quality draft
```

`new` now defaults to the cinematic template. Use `--template browser` for the
original Three.js project. This creates a new project directory and refuses to
overwrite one that already exists. The example scene is a procedural pavilion
and a simplified conductor rig, not a finished concert sequence or church model.

The complete `motion-study` example is included, so its commands work without
creating a project. It has a 10-second timeline, 600 unique frame times, an eased
camera move and a procedural conductor performance. Its visual cues are examples,
not verified beats from one of the concert recordings. No audio is generated.

### Quality levels

| Preset | Native render size | FPS | Cycles samples | PNG precision | Default export |
|---|---|---|---|---|---|
| motion-check | 320 x 180 | Project clock, normally 60 | 2 | 8 bit | H.264 MP4 |
| draft | 960 x 540 | Project clock, normally 60 | 8 | 8 bit | H.264 MP4 |
| review | 1920 x 1080 | Same project clock | 24 | 16 bit | H.264 MP4 |
| 4k-check | 3840 x 2160 | Same project clock | 8 | 16 bit | HEVC Main 10 MP4 |
| final | 3840 x 2160 | Same project clock | 64 | 16 bit | HEVC Main 10 MP4 |

All levels enable a half-frame shutter and baked animation in the supplied
Blender scene. Draft/review bake two time samples per frame; final bakes four.
At 60 fps, the half-frame shutter is 1/120 second. Samples are starting settings,
not a promise that every scene will be clean. Dense glow, reflections and fine
particles need full-size inspection in motion. Increase sampling only where it
fixes a visible problem.

`motion-check` is a deliberately small engineering preview for CPU workers. Use
it to inspect timing and continuity; it cannot approve detail, fine hands, text,
sampling noise or the final lighting. Full-size frames remain essential.
`4k-check` checks native resolution and precision with fewer samples than final.
Use it for early still inspection. It is not proof of production sampling quality.

Resolution is rendered natively. The workflow does not resize a 1080p movie and
call it native 4K, interpolate frames to claim native 60 fps, or call SDR output
HDR. Moving from 1080p to 4K increases pixel count by four; actual rendering cost
also depends on geometry, samples, blur, shading, denoising and compositing.

## Render and deliver

```bash
./scripts/video benchmark motion-study --qualities review 4k-check
./scripts/video render my-next-film --quality final
./scripts/video finalize my-next-film --quality final --profile hevc10
./scripts/video finalize my-next-film --quality final --profile prores422hq
./scripts/video finalize my-next-film --quality final --profile h264
```

Benchmark renders only three selected frames by default: beginning, middle and
end. `--frames 0,120,360,599` changes that selection. It writes actual timing
evidence to `work/pipeline/PROJECT/benchmark.json`. Any full-film time is labeled
as a rough estimate. It reuses a verified existing frame cache instead of
discarding a completed render for a benchmark.
The default uses `4k-check` when available to keep CPU checks bounded. Select
`--qualities review final` explicitly to measure the full final sampling budget.
Comparisons report each preset's sample count and blur settings; different
presets are not a resolution-only performance comparison.

`render` generates frames. `finalize` assembles existing complete, verified
frames and runs technical QA. Multiple profiles reuse those frames. The files
are `master-10bit.mp4`, `master-prores422hq.mov`, and `master.mp4`. `master.json`
tracks the most recently assembled profile, and review/QA/archive use that exact
filename. Assemble the profile you intend to archive last.

HEVC Main 10 is a compact 10-bit viewing/delivery file. ProRes 422 HQ is a larger
10-bit 4:2:2 editing intermediate. H.264 is an 8-bit compatibility copy. They use
Rec.709 SDR, with explicit conversion from the display-referred sRGB PNGs.
HEVC and ProRes require actual 16-bit source PNGs. Merely changing an 8-bit file's
format does not recover missing color precision, and the source checks reject
that shortcut. See [delivery details](VIDEO-DELIVERY.md).

The current Three.js capture and Remotion compositor are 8-bit paths. The
pipeline rejects their use for this 16-bit source / 10-bit master workflow.
Keep high-bit titles inside Blender or use a finishing application that retains
the source precision. Remotion remains useful for compatible H.264 reviews,
editing experiments and browser motion graphics.

## How motion is made smoother

### Camera tracks

`pipeline.motion.CameraTrack` and `apps/shared/motion.mjs` evaluate natural cubic
splines from authored waypoints and times. Position, velocity and acceleration
are continuous inside the path. One quintic `smootherstep` ease spans the whole
shot, bringing speed and acceleration to zero at the outer endpoints. It does
not stop at every waypoint. Sample time comes from the requested frame, not the
wall clock or the order of rendering.

```json
{
  "camera_path": {
    "seconds": [0, 3, 7, 10],
    "points": [[-4, -8, 3], [-2, -7.5, 2.8], [0, -7.2, 2.7], [2, -7.6, 3]],
    "targets": [[0, 0, 1.3]],
    "easing": "smootherstep"
  }
}
```

Blender is Z-up; the browser/legacy world is Y-up. Convert axes deliberately when
transferring a path. A shared interpolation contract is not an automatic scene
coordinate conversion. Whole-shot easing changes waypoint arrival times; use
`linear` when the supplied knot times must be exact and the shot begins/ends at
cuts. The path is not constant-speed and does not guarantee continuous jerk or
collision avoidance. Inspect its clearance, lens, framing and look target.

`video motion-qa PROJECT` reports speed, acceleration, sampled jerk and endpoint
speed in `motion-review.json`. Default thresholds are review warnings. Per-shot
`params.motion_limits` can set positive speed, acceleration and jerk limits.
Anatomy and composition still require visual review.

### Character performance

`scenes/blender/animation` contains a real procedural armature, two-bone IK,
layered actions, anchored feet, breathing/gaze and secondary follow-through.
The study uses it as a simple conductor. Actions and motion envelopes are
reusable; they are not a substitute for posing a production choir, refining
hands, avoiding body intersections and checking contacts from the actual lens.

The existing MakeHuman/CMU asset remains in `assets/p3d/body_v1.npz`. Its walk,
run, jump, dance, twirl, get-up and paired helping clips are present, along with
the recorded attribution in `assets/p3d/README.md`. They remain available to the
legacy engine. The new Blender rig is separate. Importing another capture into
Blender requires the supplied explicit bone mapping/rest-pose retarget utility
and a contact review; this setup does not claim that every old clip has already
been converted and polished for the new rig.

### Secondary motion and blur

Closed-form damped springs can be sampled in any frame order. They add lag and
settling to a chosen action without accumulating state across render calls.
They preserve position and velocity at cue changes; acceleration can change at
those cues, so the C2 event envelope is preferable when that change is visible.

For Blender physics, bake the simulation cache before distributing frames. The
animation utilities also bake camera, pose and object transforms at subframes,
including shutter handles beyond each requested chunk. The worker refuses
motion blur unless the scene declares support and confirms the bake. Enabling
a renderer flag on a scene that only changes at integer frames is insufficient.

The supplied study bakes its moving ribbons, particles, character and camera.
The shot's absolute time remains the source of truth, so chunks can render
independently. GPU/hardware and denoiser differences can still change pixels;
deterministic animation state does not promise bit-identical Cycles images.

## Timing the music

Keep one fixed frame clock for the project. Store manually checked hits in the
timing file using `frame`, `kind`, `amplitude`, `attack_frames`, and
`release_frames`. The event envelope peaks at the authored hit frame and eases
into/out of it. Automatic audio onsets remain suggestions until checked against
the exact recording. Do not drive every effect from every beat.

Use camera moves over phrases, body anticipation before the gesture, the
principal action at the meaningful musical moment, then a gentle settle.
`apps/shared/shot-templates.mjs` supplies reusable browser camera/phrase templates.
The browser preview applies event energy to bounded local motion, not full-scene
exposure. Keep typography stable and readable.

## Recovering long CPU renders

New cinematic projects use one-frame chunks, four CPU threads, and a 7200-second
timeout per chunk. This conservative starting point avoids requiring a batch of
30 slow 4K frames to finish within a short worker limit. Set
`render_chunk_frames`, `threads`, and `render_timeout_seconds` under `production`
for the worker's measured capacity. Larger chunks can reduce startup overhead
for lightweight previews after benchmarking. No GPU provider is selected.

The included `motion-study` verification project retains its recorded preview
settings of 30-frame chunks and 1800 seconds. Its native-size checks requested
only one frame. Before using that existing project for a full 1080p or 4K CPU
sequence, use one-frame chunks and the longer timeout from the new-project
template. The measured 4K check took about 217 seconds for one frame, so 30 such
frames would exceed 1800 seconds. A timeout cannot guarantee success for every
scene; size it from the actual final-preset benchmark.

Every finished PNG is written atomically and verified for dimensions, expected
bit depth and checksum. Even when a worker fails, valid completed frames in that
chunk get a receipt. Running the same render command resumes missing frames.
Changing scene code, timing, quality or a dependency invalidates the affected
cache. Use ordinary rendering to resume; `--force` deliberately invalidates the
selected shot's owned cached products.
Workers also check their source hashes before and after a chunk, so a source
edit during rendering stops the round. Finishing-only edits have their own
provenance map and do not invalidate unchanged 3D frames.

## Review cycle

1. Review camera diagnostics and native 1080p/4K stills for geometry, lettering,
   exposure and composition before committing to a full render.
2. Watch the draft at the actual 60 fps. Look for sliding feet, stiff elbows,
   hand contact, awkward acceleration, distracting particles and text timing.
3. Freeze shared scene/lighting code during a render round. Make changes after
   reviewing the complete round to avoid constantly invalidating its cache.
4. Render the final frames, assemble the chosen profile and inspect QA. Temporal
   QA decodes the delivered movie and flags frozen intervals, brightness
   reversals, pixel shimmer and abrupt changes away from declared cuts/flashes.
   These are candidate warnings, not proof that movement is natural.
5. Record an actual human review with `video approve` only after viewing it, then
   use `video archive` for a delivery package with checksums and provenance.

No automatic approval is recorded. The reference setup remains cloud CPU by
default. Browser capture and the live Blender MCP bridge need a cloud host that
allows local IPC and, for the bridge, a Blender GUI. Build/installation success
must not be reported as successful playback. See the current verification record
in [4K-MOTION-VALIDATION.md](4K-MOTION-VALIDATION.md).
