"""Subframe animation baking for Cycles and independent render chunks.

Pipeline frame f maps to Blender frame f+1. Values are sampled analytically at
fractional pipeline frames, including handles outside the requested interval.
The resulting action curves are evaluated by Blender during shutter sampling.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from pathlib import Path
import json

import bpy
from mathutils import Quaternion, Vector


@dataclass(frozen=True)
class BakeReceipt:
    start_frame: int
    end_frame_exclusive: int
    first_sample: float
    last_sample: float
    samples: int
    substeps: int
    shutter: float
    interpolation: str
    objects: tuple[str, ...]

    def to_dict(self):
        return asdict(self)


def _sample_frames(start_frame, end_frame_exclusive, fps, substeps, shutter):
    if type(start_frame) is not int or type(end_frame_exclusive) is not int or start_frame < 0 or end_frame_exclusive <= start_frame:
        raise ValueError("bake frames must be a nonempty half-open integer interval")
    if not isinstance(fps, (int, float)) or isinstance(fps, bool) or not math.isfinite(fps) or fps <= 0:
        raise ValueError("bake fps must be positive")
    if type(substeps) is not int or not 1 <= substeps <= 16:
        raise ValueError("substeps must be an integer from 1 to 16")
    if isinstance(shutter, bool) or not isinstance(shutter, (float, int)) or not math.isfinite(shutter) or not 0 <= shutter <= 2:
        raise ValueError("shutter must be 0..2 frames")
    handles = max(1, math.ceil(shutter * 0.5 * substeps))
    first = start_frame * substeps - handles
    last = (end_frame_exclusive - 1) * substeps + handles
    if last - first > 2_000_000:
        raise ValueError("bake has too many samples; split the render into chunks")
    return [value / substeps for value in range(first, last + 1)]


def action_fcurves(animation_data):
    """Support Blender's legacy and layered/slotted Action APIs."""
    if animation_data is None or animation_data.action is None:
        return []
    action = animation_data.action
    try:
        curves = list(action.fcurves)
        if curves:
            return curves
    except AttributeError:
        pass
    curves = []
    slot = animation_data.action_slot
    for layer in action.layers:
        for strip in layer.strips:
            if hasattr(strip, "channelbag"):
                bag = strip.channelbag(slot)
                if bag is not None:
                    curves.extend(bag.fcurves)
    return curves


def _linear_keys(objects):
    for obj in objects:
        for curve in action_fcurves(obj.animation_data):
            for key in curve.keyframe_points:
                key.interpolation = "LINEAR"


def _key_transform(obj, blender_frame, previous_quaternion):
    obj.keyframe_insert(data_path="location", frame=blender_frame)
    if obj.rotation_mode == "QUATERNION":
        quaternion = obj.rotation_quaternion.copy()
        if previous_quaternion is not None and quaternion.dot(previous_quaternion) < 0:
            quaternion.negate()
            obj.rotation_quaternion = quaternion
        obj.keyframe_insert(data_path="rotation_quaternion", frame=blender_frame)
        previous_quaternion = quaternion
    elif obj.rotation_mode == "AXIS_ANGLE":
        obj.keyframe_insert(data_path="rotation_axis_angle", frame=blender_frame)
    else:
        # Existing Euler callbacks, such as the original pavilion ribbons, must
        # keep their rotation mode. They are not silently converted to quats.
        obj.keyframe_insert(data_path="rotation_euler", frame=blender_frame)
    obj.keyframe_insert(data_path="scale", frame=blender_frame)
    return previous_quaternion


def _receipt(objects, samples, start_frame, end_frame_exclusive, substeps, shutter):
    return BakeReceipt(start_frame, end_frame_exclusive, samples[0], samples[-1], len(samples), substeps, shutter, "LINEAR", tuple(obj.name for obj in objects))


def bake_callback(objects, update_frame, start_frame, end_frame_exclusive, fps, *, substeps=2, shutter=0.5):
    """Bake object transforms from update_frame(fractional_absolute_frame).

    This does not bake animated mesh vertices, material inputs, modifiers, or
    simulation state. Geometry Nodes/cloth need their own completed caches.
    Use fresh scene objects or explicitly remove unwanted older actions first.
    """
    objects = tuple(objects)
    if not objects:
        raise ValueError("bake_callback requires explicit objects")
    samples = _sample_frames(start_frame, end_frame_exclusive, fps, substeps, shutter)
    previous = {obj.name: None for obj in objects}
    for frame in samples:
        update_frame(frame)
        for obj in objects:
            previous[obj.name] = _key_transform(obj, frame + 1.0, previous[obj.name])
    _linear_keys(objects)
    return _receipt(objects, samples, start_frame, end_frame_exclusive, substeps, shutter)


def bake_camera(camera, track, start_frame, end_frame_exclusive, fps, *, time_offset=0.0, substeps=2, shutter=0.5):
    """Bake position, look-at rotation, and roll from a CameraTrack.

    time_offset maps absolute pipeline time to a local track. The orientation
    uses Blender's -Z viewing axis, Y screen-up, and world Z-up. Near-vertical
    look directions are rejected to avoid an ambiguous up direction/roll flip.
    """
    camera.rotation_mode = "QUATERNION"

    def update(frame):
        sample = track.sample(frame / fps - time_offset)
        camera.location = sample.position
        direction = Vector(sample.target) - Vector(sample.position)
        if abs(direction.normalized().dot(Vector((0.0, 0.0, 1.0)))) > 0.9999:
            raise ValueError("camera look direction is too close to Z-up; adjust target to define stable roll")
        orientation = direction.to_track_quat("-Z", "Y")
        camera.rotation_quaternion = orientation @ Quaternion((0.0, 0.0, 1.0), sample.roll_radians)

    return bake_callback((camera,), update, start_frame, end_frame_exclusive, fps, substeps=substeps, shutter=shutter)


def bake_character(rig, performance, start_frame, end_frame_exclusive, fps, *, time_offset=0.0, substeps=2, shutter=0.5):
    """Bake an armature's evaluated pose channels, including fractional frames."""
    samples = _sample_frames(start_frame, end_frame_exclusive, fps, substeps, shutter)
    # Curves supply real subframe deformation; explicitly allow Cycles to use it.
    if hasattr(rig.mesh, "cycles"):
        rig.mesh.cycles.use_motion_blur = True
        rig.mesh.cycles.use_deform_motion = True
    previous = {bone.name: None for bone in rig.armature.pose.bones}
    max_reach_error = 0.0
    for frame in samples:
        pose = performance.apply(frame / fps - time_offset)
        max_reach_error = max(max_reach_error, pose.max_reach_error)
        for bone in rig.armature.pose.bones:
            previous[bone.name] = _key_transform(bone, frame + 1.0, previous[bone.name])
    _linear_keys((rig.armature,))
    rig.armature["pipeline_baked_reach_error_m"] = max_reach_error
    rig.armature["pipeline_baked_substeps"] = substeps
    return _receipt((rig.armature,), samples, start_frame, end_frame_exclusive, substeps, shutter)


def bake_physics_cache(output_blend, *, start_frame, end_frame, objects=(), rigid_body=False):
    """Explicit pre-render bake for cloth/soft-body and/or rigid-body caches.

    The result must be distributed with its point-cache files. Invoke this once
    before splitting renders, not independently inside every render worker.
    Geometry Nodes simulations are not included. This helper intentionally
    refuses unsupported modifiers instead of claiming a complete physics bake.
    """
    path = Path(output_blend).expanduser().resolve()
    if path.suffix != ".blend" or type(start_frame) is not int or type(end_frame) is not int or end_frame <= start_frame:
        raise ValueError("physics bake needs a .blend path and increasing integer Blender frames")
    scene = bpy.context.scene
    # Store stable names, not PointCache RNA pointers. A simulation evaluation
    # can replace the rigid-body cache and leave an earlier Python pointer stale.
    targets = []
    for obj in objects:
        found = False
        for modifier in obj.modifiers:
            if modifier.type in ("CLOTH", "SOFT_BODY"):
                targets.append((obj.name, modifier.name))
                found = True
        if not found:
            raise ValueError(f"{obj.name} has no supported cloth or soft-body cache")
    if rigid_body:
        if scene.rigidbody_world is None:
            raise ValueError("scene has no rigid-body world")
        targets.append((None, None))
    if not targets:
        raise ValueError("select explicit physics objects or rigid_body=True")
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.frame_start, scene.frame_end = start_frame, end_frame
    scene.frame_set(start_frame)
    # Enabling disk caches before the scene has a saved filename is ignored.
    bpy.ops.wm.save_as_mainfile(filepath=str(path))

    def resolve(name, modifier_name):
        obj = bpy.data.objects[name] if name else None
        cache = obj.modifiers[modifier_name].point_cache if obj else scene.rigidbody_world.point_cache
        return obj, cache

    for name, modifier_name in targets:
        obj, cache = resolve(name, modifier_name)
        if cache.is_baked:
            raise ValueError(f"{name or 'rigid-body world'} already has a baked cache; free it explicitly before rebaking")
        cache.frame_start, cache.frame_end = start_frame, end_frame
        if obj is not None:
            cache.use_disk_cache = True
            if not cache.use_disk_cache:
                raise RuntimeError(f"disk cache could not be enabled for {name}")
        # Rigid-body caches are embedded in the saved .blend. Blender does not
        # offer the object-simulation Disk Cache switch in its rigid-body UI;
        # setting that RNA property can crash Blender 5.2.4. Do not set it here.
        context = {"scene": scene, "point_cache": cache}
        if obj is not None:
            context.update(object=obj, active_object=obj)
        with bpy.context.temp_override(**context):
            bpy.ops.ptcache.bake(bake=True)
        _, verified_cache = resolve(name, modifier_name)
        if not verified_cache.is_baked:
            raise RuntimeError(f"physics cache did not finish for {obj.name if obj else 'rigid-body world'}")
        if verified_cache.frame_start != start_frame or verified_cache.frame_end != end_frame:
            raise RuntimeError(f"physics cache range changed for {name or 'rigid-body world'}")
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    receipt = {"blend": str(path), "blender_version": bpy.app.version_string, "start_frame": start_frame, "end_frame": end_frame,
               "baked_caches": len(targets), "embedded_rigid_body_cache": bool(rigid_body),
               "cache_files": [str(item.relative_to(path.parent)) for item in sorted(path.parent.glob(f"blendcache_{path.stem}/**/*")) if item.is_file()],
               "note": "Archive the .blend and complete blendcache directory together; this is not a cross-version simulation guarantee."}
    if any(name is not None for name, _ in targets) and not receipt["cache_files"]:
        raise RuntimeError("physics bake completed without discoverable disk-cache files")
    path.with_suffix(".bake.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt
