"""Explicit rest-space retargeting between already imported Blender armatures.

No motion assets are downloaded or guessed. Callers supply a source action,
bone map, and any bone-axis corrections, then review contact and anatomy.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Quaternion, Vector

from .bake import _key_transform, _linear_keys, _sample_frames


def retarget_action(source, target, bone_map, start_frame, end_frame_exclusive, fps, *,
                    root_bone=None, root_motion_scale=1.0, local_axis_corrections=None, substeps=2, shutter=0.5):
    """Sample and bake source motion onto target using a source->target map.

    Source pose matrices include constraints. They are converted back into each
    source bone's rest-relative local transform before transferring rotations.
    Optional corrections map source bone-local axes into target bone-local axes
    as (w,x,y,z) quaternions. Only the named root bone receives translation;
    target bone lengths and rest offsets stay intact. Bone scale is not copied.

    This adapter does not infer bone names, import FBX/BVH, solve foot sliding,
    or make a differently proportioned actor's contacts correct automatically.
    """
    if source is target or source.type != "ARMATURE" or target.type != "ARMATURE":
        raise ValueError("retargeting needs two different armatures")
    if not isinstance(bone_map, dict) or not bone_map or len(set(bone_map.values())) != len(bone_map):
        raise ValueError("bone_map must be a nonempty one-to-one source->target mapping")
    for source_name, target_name in bone_map.items():
        if source_name not in source.data.bones or target_name not in target.data.bones:
            raise ValueError(f"retarget bone does not exist: {source_name} -> {target_name}")
    if isinstance(root_motion_scale, bool) or not isinstance(root_motion_scale, (float, int)) or not math.isfinite(root_motion_scale) or root_motion_scale <= 0:
        raise ValueError("root_motion_scale must be positive")
    reverse = {destination: origin for origin, destination in bone_map.items()}
    if root_bone is None:
        roots = [name for name in reverse if target.data.bones[name].parent is None]
        root_bone = roots[0] if len(roots) == 1 else None
    if root_bone is not None and root_bone not in reverse:
        raise ValueError("root_bone must be a mapped destination bone")
    corrections = {}
    for name, value in (local_axis_corrections or {}).items():
        if name not in reverse or not isinstance(value, (list, tuple)) or len(value) != 4 or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value):
            raise ValueError("axis corrections need mapped target names and finite (w,x,y,z) quaternions")
        q = Quaternion(value)
        if q.magnitude < 1e-8:
            raise ValueError("axis correction quaternion cannot be zero")
        corrections[name] = q.normalized()
    samples = _sample_frames(start_frame, end_frame_exclusive, fps, substeps, shutter)
    previous = {bone.name: None for bone in target.pose.bones}
    for frame in samples:
        blender_frame = frame + 1.0
        integer = math.floor(blender_frame)
        bpy.context.scene.frame_set(integer, subframe=blender_frame - integer)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated_source = source.evaluated_get(depsgraph)
        for bone in target.pose.bones:
            bone.rotation_mode = "QUATERNION"
            bone.location = (0.0, 0.0, 0.0)
            bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
            bone.scale = (1.0, 1.0, 1.0)
            if bone.name in reverse:
                source_bone = evaluated_source.pose.bones[reverse[bone.name]]
                kwargs = {}
                if source_bone.parent:
                    kwargs.update(parent_matrix=source_bone.parent.matrix, parent_matrix_local=source_bone.parent.bone.matrix_local)
                basis = source_bone.bone.convert_local_to_pose(source_bone.matrix, source_bone.bone.matrix_local, invert=True, **kwargs)
                location, rotation, _ = basis.decompose()
                correction = corrections.get(bone.name, Quaternion())
                bone.rotation_quaternion = correction @ rotation @ correction.inverted()
                if bone.name == root_bone:
                    bone.location = (correction @ Vector(location)) * root_motion_scale
            previous[bone.name] = _key_transform(bone, blender_frame, previous[bone.name])
    _linear_keys((target,))
    return {"source": source.name, "target": target.name, "bone_map": dict(bone_map), "samples": len(samples),
            "first_sample": samples[0], "last_sample": samples[-1], "root_bone": root_bone,
            "unmapped_target_bones": [bone.name for bone in target.data.bones if bone.name not in reverse],
            "needs_contact_review": True,
            "limits": ["Review foot and hand contact when proportions or rest poses differ.",
                       "Finger articulation requires finger bones and a corresponding source action.",
                       "No motion-source files were downloaded or inferred."]}
