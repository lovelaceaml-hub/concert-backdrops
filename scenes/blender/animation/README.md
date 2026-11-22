# Reusable motion and character animation

These tools add deterministic camera paths, actual armatures, IK, pose layers,
subframe baking, and an explicit motion-retarget adapter. They do not replace an
approved film or provide finished professional performances automatically.

## Coordinates and clocks

Blender examples use metres, **Z-up**, with a standing figure facing **-Y**.
Three.js examples use Y-up. Convert coordinates explicitly when sharing a scene.

The pipeline uses global zero-based frames. Blender frame `f + 1` represents
pipeline frame `f`, including fractional values. Shot intervals are half-open.
Every analytic sampler accepts absolute or shot-local seconds, as chosen by the
caller. Set `time_offset=shot_start_frame / fps` when a track uses local seconds.
Musical events use the same clock as the sampler; offset their frame values when
passing global events to a shot-local character performance.

## Camera paths

```python
from pipeline.motion import CameraTrack

track = CameraTrack.from_dict({
    "seconds": [0, 2, 5, 10],
    "points": [[-3, -14, 4], [-2, -10, 3], [1, -5, 2.8], [4, 1, 6]],
    "targets": [[0, 0, 1.6]],
    "easing": "smootherstep",
    "roll_degrees": [0, 0],
})
sample = track.sample(3.25)
report = track.diagnostics(sample_hz=60)
```

Natural cubic splines interpolate the supplied points and targets, with continuous
velocity and acceleration at internal knots. One quintic time warp spans the
whole shot, so the camera starts and stops with zero velocity and acceleration.
It does not stop at every waypoint. Targets may contain one fixed target or one
target per point. Times must be finite and strictly increasing; an arbitrary time
domain is allowed. If times are absent, pass `duration_seconds` to obtain uniform
times over that duration. Values hold outside the domain.

`easing="linear"` preserves the waypoint arrival times but can start and stop
abruptly at a clamped endpoint. With `smootherstep`, interior times are parameters
of the spatial curve and the global time warp changes their wall-clock arrival
times. The browser implementation uses the same interpolation and easing, with a
shared numerical fixture in the tests.

The path is not collision-aware and does not promise constant speed or continuous
jerk. Cubic interpolation can overshoot the waypoints. Review framing, clearance,
speed, and target distance. The bake rejects look directions almost parallel to
world Z, because a look-at camera cannot infer a stable up direction there. For a
vertical shot, author a small target offset or implement an explicit orientation
track instead of accepting an uncontrolled roll flip.

## Actual rig and layered performance

```python
from scenes.blender.animation import create_character, CharacterPerformance

rig = create_character("Conductor", location=(0, -0.5, 0.34),
                       scale=1, material=gold_material, seed=2026)
performance = CharacterPerformance(rig, action="conduct", strength=0.7, fps=60)
pose = performance.apply(1.5)
assert pose.max_reach_error < 0.001
```

The procedural example has a real 16-bone armature and a mesh weighted to those
bones. It layers authored conduct/reach/bow/idle gestures, breathing, small weight
shifts, head orientation, and damped wrist lag. Two-bone analytical IK keeps the
feet planted and makes elbow/knee bend directions explicit. The IK solver returns
its reach error instead of calling an unreachable target a successful contact.
It preserves limb lengths and all pose sampling is independent of render order.

The visible figure is an original soft gold form. It has no photorealistic skin,
generated imagery, external model, face, or glowing eyes. Fingers are grouped
relaxed forms attached to the hand bone. Close-up hands, complex acting, playing
instruments, walking, embracing, cloth, and collision avoidance require additional
authored rigs, assets, constraints, and review. A higher frame rate alone does not
create those performances.

`HumanoidPerformance` in `pipeline.motion` exposes the same pose sampler without
Blender, so contacts, segment lengths, and determinism can be checked cheaply.

## Bake before motion-blurred or distributed rendering

```python
from scenes.blender.animation import bake_camera, bake_character, bake_callback

# A worker can bake only its chunk, plus automatically generated shutter handles.
begin = min(job["frames"])
end = max(job["frames"]) + 1
fps = job["video"]["fps"]
offset = job["shot"]["start_frame"] / fps

bake_callback(ribbon_objects, existing_update, begin, end, fps,
              substeps=2, shutter=0.5)
bake_camera(camera, track, begin, end, fps, time_offset=offset,
            substeps=2, shutter=0.5)
bake_character(rig, performance, begin, end, fps, time_offset=offset,
               substeps=2, shutter=0.5)

# Set only after every moving element that needs blur has actually been baked.
bpy.context.scene["pipeline_motion_baked"] = True

def update(frame):
    # The worker calls scene.frame_set(frame + 1). Blender evaluates the actions
    # at fractional shutter times during render. Do not overwrite these poses.
    pass
```

The scene module must declare `SUPPORTS_BAKED_MOTION_BLUR = True` when it supports
this contract. The worker enforces the scene marker when blur is requested.
`shutter=0.5` means half a frame, or 1/120 second at 60 fps. The worker uses a
centered shutter. Bake the same or a wider shutter than the render setting.

`bake_callback` receives fractional global frame values and keys object location,
active rotation mode, and scale. Euler callbacks retain their Euler rotation
mode. Camera and pose quaternions are sign-unwrapped before keying. Extra samples
cover both sides of the render interval, including the first and last shutter.
Returned `BakeReceipt` objects have `to_dict()` for provenance.

Keys are densely sampled with linear interpolation. Blender evaluates real
fractional-frame transforms and deforming geometry from these actions; this is
not a blur flag on otherwise static geometry. The mathematical source is C2, but
linear baked samples approximate it. Increase `substeps` for fast motion and
compare subframe pose error. The no-render Blender check measures this error,
contact drift, camera direction, and equality between full-range and chunk bakes.
Final motion-blur appearance still needs a rendered comparison.

The generic callback helper bakes object transforms only. Animated vertices,
material/shader values, Geometry Nodes simulation, and caches need their own
baking. Use fresh objects or explicitly remove unwanted preexisting action
curves before baking; the helpers do not delete an existing animation.

## Events and secondary motion

`event_envelope(frame, events, fps=60, kind=None, cap=None)` evaluates C2 attack
and release around an exact authored hit frame. Each event may set `amplitude`,
`attack_frames`, and `release_frames`. Defaults are a 0.25-second attack and a
1.2-second release, rounded to frames. Optional saturation has a smooth knee
between cap/2 and cap; it changes amplitudes in that interval. Leave `cap=None`
for exact additive values. Keep important hits manually checked against audio.

`DampedSpring([(time, target), ...], frequency_hz=1.5, damping_ratio=0.75)` solves
a damped second-order response from a fixed cue list. It supports underdamped,
critical, and overdamped responses. It has no mutable time-stepping state, so
frames can be requested in any order. Position and velocity remain continuous at
target changes; acceleration can change there. Use an eased envelope when the
acceleration change would be visible.

## Retarget existing actions explicitly

```python
from scenes.blender.animation import retarget_action

receipt = retarget_action(
    source_armature, destination_rig.armature,
    {"Hips": "pelvis", "Spine": "spine", "Head": "head"},
    0, 600, 60, root_bone="pelvis", root_motion_scale=1.0,
    local_axis_corrections={}, substeps=2,
)
```

Import or create the source action first. The map is **source name to target
name**. The adapter evaluates source constraints, converts poses to rest-relative
bone-local transforms, copies rotations, and copies translation only to the named
root. It retains target bone lengths and rest offsets. Optional `(w,x,y,z)` axis
corrections describe different bone-local orientations. Source bone scaling is
not transferred. Unmapped bones hold their rest-relative pose.

This is a usable transfer and bake mechanism, verified on matching synthetic
skeletons. It does not infer mappings or fix contacts when proportions differ.
Inspect the resulting feet, hands, shoulder range, and contact constraints before
using retargeted motion in a film. Existing project motion assets remain untouched;
this example neither assumes their mapping nor downloads new assets.

## Bake stateful physics once

`bake_physics_cache(path_to_blend, start_frame=1, end_frame=600,
objects=[cloth_object], rigid_body=True)` handles explicit cloth/soft-body and
rigid-body point caches. These arguments use native Blender frame numbers. It
saves the scene, enables cloth/soft-body disk caches, invokes the bake operator,
verifies each cache's completed state, saves again, and writes a JSON receipt.
The rigid-body cache is stored inside the saved `.blend`. Archive the
`.blend`, receipt, and complete `blendcache_<name>` directory together.

Run that operation once before distributing jobs. Do not simulate independently
in each worker. Pin Blender and keep the cache with the source scene; the helper
does not guarantee identical simulations across versions or machines. Geometry
Nodes simulation and external caches are outside this helper's supported scope.

## Verification

```sh
python -m unittest discover -s tests/pipeline -p test_motion.py -v
.tools/blender-5.2.4-linux-x64/blender -b --factory-startup --python-exit-code 1 \
  --python tests/blender/check_animation.py -- --physics
```

The second command renders no frames. It checks actual armature deformation,
fractional F-curve evaluation, contacts, chunk equivalence, camera direction,
legacy Euler callbacks, explicit retargeting, and a four-frame physics cache.
