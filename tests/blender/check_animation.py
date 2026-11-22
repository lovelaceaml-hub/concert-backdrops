"""No-render Blender checks for actual armatures, subframes, and retargeting.

Run with the pinned Blender binary:
  blender -b --factory-startup --python-exit-code 1 --python tests/blender/check_animation.py
Add -- --physics to exercise four-frame cloth and rigid-body cache baking.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import bpy
from mathutils import Vector

from pipeline.motion import CameraTrack
from pipeline.motion.character import REST_BONES
from scenes.blender.animation import (CharacterPerformance, bake_callback, bake_camera, bake_character,
                                     bake_physics_cache, create_character, retarget_action)
from scenes.blender.animation.bake import action_fcurves


def set_pipeline_frame(frame):
    value = frame + 1.0
    integer = math.floor(value)
    bpy.context.scene.frame_set(integer, subframe=value - integer)
    bpy.context.view_layer.update()


def difference(a, b):
    return (Vector(a) - Vector(b)).length


def camera_object(name):
    obj = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    bpy.context.collection.objects.link(obj)
    return obj


def check():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    rig = create_character("Source", seed=2026)
    performance = CharacterPerformance(rig, action="conduct")
    max_pose_error = 0.0
    vertex_snapshots = []
    for t in (0.0, 0.5, 1.0, 0.0):
        desired = performance.apply(t)
        bpy.context.view_layer.update()
        for name, (head, tail) in desired.bones.items():
            bone = rig.armature.pose.bones[name]
            max_pose_error = max(max_pose_error, difference(bone.head, head), difference(bone.tail, tail))
        evaluated = rig.mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        vertex_snapshots.append([v.co.copy() for v in evaluated.data.vertices])
    assert max_pose_error < 3e-6, max_pose_error
    assert max(difference(a, b) for a, b in zip(vertex_snapshots[0], vertex_snapshots[1])) > 0.02
    assert max(difference(a, b) for a, b in zip(vertex_snapshots[0], vertex_snapshots[-1])) < 3e-6

    receipt = bake_character(rig, performance, 0, 121, 60, substeps=2, shutter=0.5)
    assert receipt.first_sample < 0 and receipt.last_sample > 120
    assert any(abs(point.co.x - round(point.co.x)) > 0.1 for curve in action_fcurves(rig.armature.animation_data) for point in curve.keyframe_points)
    chunk = create_character("Chunk", seed=2026)
    chunk_performance = CharacterPerformance(chunk, action="conduct")
    bake_character(chunk, chunk_performance, 32, 91, 60, substeps=2, shutter=0.5)
    max_subframe_error, max_contact_error, max_chunk_error = 0.0, 0.0, 0.0
    for frame in (0.25, 17.75, 31.75, 32, 45.25, 60.75, 89.25, 90.25, 119.75):
        set_pipeline_frame(frame)
        expected = performance.motion.sample(frame / 60)
        for name, (head, tail) in expected.bones.items():
            bone = rig.armature.pose.bones[name]
            max_subframe_error = max(max_subframe_error, difference(bone.head, head), difference(bone.tail, tail))
            if 31.5 <= frame <= 90.5:
                max_chunk_error = max(max_chunk_error, difference(chunk.armature.pose.bones[name].head, bone.head), difference(chunk.armature.pose.bones[name].tail, bone.tail))
        for side in ("L", "R"):
            max_contact_error = max(max_contact_error, difference(rig.armature.pose.bones[f"foot.{side}"].head, REST_BONES[f"foot.{side}"][0]))
    assert max_subframe_error < 0.0005, max_subframe_error
    assert max_contact_error < 0.0001, max_contact_error
    assert max_chunk_error < 3e-6, max_chunk_error

    track = CameraTrack.from_dict({"seconds": [0, 0.6, 1.3, 2], "points": [[-2, -8, 3], [-1, -6, 2.8], [1, -4, 2.5], [3, -2, 3]],
                                   "targets": [[0, 0, 1.2]], "easing": "smootherstep"})
    camera, chunk_camera = camera_object("Full camera"), camera_object("Chunk camera")
    bake_camera(camera, track, 0, 121, 60)
    bake_camera(chunk_camera, track, 32, 91, 60)
    max_camera_error, max_camera_chunk_error, max_look_error = 0.0, 0.0, 0.0
    for frame in (0.25, 17.75, 31.75, 45.25, 60.75, 89.25, 119.75):
        set_pipeline_frame(frame)
        expected = track.sample(frame / 60)
        max_camera_error = max(max_camera_error, difference(camera.location, expected.position))
        direction = (Vector(expected.target) - Vector(expected.position)).normalized()
        actual_direction = camera.rotation_quaternion @ Vector((0, 0, -1))
        max_look_error = max(max_look_error, actual_direction.angle(direction))
        if 31.5 <= frame <= 90.5:
            max_camera_chunk_error = max(max_camera_chunk_error, difference(camera.location, chunk_camera.location))
    assert max_camera_error < 0.001, max_camera_error
    assert max_look_error < 0.001, max_look_error
    assert max_camera_chunk_error < 3e-6, max_camera_chunk_error

    euler_object = bpy.data.objects.new("Euler ribbon proxy", None)
    bpy.context.collection.objects.link(euler_object)
    euler_object.rotation_mode = "XYZ"

    def old_callback(frame):
        euler_object.rotation_euler.z = 0.2 * math.sin(frame / 60)

    bake_callback([euler_object], old_callback, 0, 121, 60)
    set_pipeline_frame(45.25)
    assert euler_object.rotation_mode == "XYZ"
    assert abs(euler_object.rotation_euler.z - 0.2 * math.sin(45.25 / 60)) < 1e-5

    destination = create_character("Retargeted", seed=2026)
    bone_map = {name: name for name in REST_BONES}
    retarget_receipt = retarget_action(rig.armature, destination.armature, bone_map, 0, 121, 60)
    max_retarget_error = 0.0
    for frame in (0, 18.25, 60.75, 100.5, 120):
        set_pipeline_frame(frame)
        for name in REST_BONES:
            source_bone = rig.armature.pose.bones[name]
            target_bone = destination.armature.pose.bones[name]
            max_retarget_error = max(max_retarget_error, difference(source_bone.head, target_bone.head), difference(source_bone.tail, target_bone.tail))
    assert max_retarget_error < 1e-5, max_retarget_error
    assert retarget_receipt["needs_contact_review"] is True
    return {"blender_version": bpy.app.version_string, "rendered_frames": 0,
            "max_pose_error_m": max_pose_error, "max_subframe_pose_error_m": max_subframe_error,
            "max_subframe_contact_error_m": max_contact_error, "max_chunk_pose_difference_m": max_chunk_error,
            "max_camera_subframe_error_m": max_camera_error, "max_camera_chunk_difference_m": max_camera_chunk_error,
            "max_camera_look_error_radians": max_look_error, "max_same_skeleton_retarget_error_m": max_retarget_error,
            "character_bake": receipt.to_dict(), "euler_callback_preserved": True}


def check_physics():
    # Four frames and four cloth vertices are enough to verify actual point-cache
    # invocation without starting a production simulation or rendering anything.
    mesh = bpy.data.meshes.new("Tiny cloth geometry")
    mesh.from_pydata([(-0.1, -0.1, 2), (0.1, -0.1, 2), (0.1, 0.1, 2), (-0.1, 0.1, 2)], [], [(0, 1, 2, 3)])
    cloth = bpy.data.objects.new("Tiny cloth", mesh)
    bpy.context.collection.objects.link(cloth)
    cloth.modifiers.new("Cloth cache check", "CLOTH")
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 2))
    cube = bpy.context.object
    cube_name = cube.name
    bpy.ops.rigidbody.object_add()
    with tempfile.TemporaryDirectory(prefix="motion-cache-check-") as directory:
        receipt = bake_physics_cache(Path(directory) / "test.blend", start_frame=1, end_frame=4, objects=[cloth], rigid_body=True)
        assert receipt["baked_caches"] == 2
        assert receipt["cache_files"], "bake did not write distributable disk-cache files"
        bpy.ops.wm.open_mainfile(filepath=str(Path(directory) / "test.blend"))
        assert bpy.context.scene.rigidbody_world.point_cache.is_baked, "rigid-body cache did not survive saving and reopening"
        assert bpy.data.objects["Tiny cloth"].modifiers["Cloth cache check"].point_cache.is_baked
        # Read late, then early, then late: an archive must provide random access.
        bpy.context.scene.frame_set(4)
        late = bpy.data.objects[cube_name].matrix_world.translation.z
        bpy.context.scene.frame_set(1)
        early = bpy.data.objects[cube_name].matrix_world.translation.z
        bpy.context.scene.frame_set(4)
        again = bpy.data.objects[cube_name].matrix_world.translation.z
        assert late < early and abs(late - again) < 1e-7
        return {"frames": 4, "baked_caches": receipt["baked_caches"], "cache_file_count": len(receipt["cache_files"]), "reopened_random_access": True}


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--physics", action="store_true")
    options = parser.parse_args(args)
    report = check()
    if options.physics:
        report["physics"] = check_physics()
    print(json.dumps({"event": "motion_checks_passed", **report}, sort_keys=True), flush=True)
