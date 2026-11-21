"""Exercise the actual scene contract, without rendering expensive pixels."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pipeline.motion import HumanoidPerformance
from scenes.blender import motion_study


def job(blur=False):
    return {"seed": 2026, "samples": 1, "frames": [300, 301, 302],
            "video": {"fps": 60, "width": 32, "height": 18},
            "motion_blur": {"enabled": blur, "substeps": 2, "shutter": .5},
            "shot": {"start_frame": 300, "end_frame_exclusive": 600,
                     "params": {"camera_path": {"points": [[-4, -8, 3], [2, -7, 3]], "roll_degrees": [10, 10]}}},
            "timing": {"events": [{"frame": 290, "kind": "cue", "attack_frames": 15, "release_frames": 72}]}}


def state(blur):
    data = job(blur)
    update = motion_study.build_scene(data)
    bpy.context.scene.frame_set(301)
    update(300)
    bpy.context.view_layer.update()
    camera = bpy.context.scene.camera
    rig = bpy.data.objects["Conductor rig"].evaluated_get(bpy.context.evaluated_depsgraph_get())
    expected = HumanoidPerformance(action="conduct", strength=.7, seed=2026, fps=60,
                                  events=[{**data["timing"]["events"][0], "frame": -10}]).sample(0)
    hand = rig.pose.bones["hand.R"].head.copy()
    error = (hand - Vector(expected.bones["hand.R"][0])).length
    assert error < 1e-5, error
    return camera.location.copy(), camera.rotation_quaternion.copy(), error


plain, baked = state(False), state(True)
assert (plain[0] - baked[0]).length < 1e-6
angle = plain[1].rotation_difference(baked[1]).angle
assert angle < 1e-5, angle
empty = job(False)
empty["shot"]["params"] = {}
motion_study.build_scene(empty)(300)
print(json.dumps({"event": "study_contract_passed", "optional_camera_fields": True,
                  "empty_scene_params": True, "roll_toggle_error_radians": angle,
                  "cross_shot_cue_hand_error_m": max(plain[2], baked[2])}), flush=True)
