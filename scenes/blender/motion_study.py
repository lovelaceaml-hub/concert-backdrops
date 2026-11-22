"""A reusable camera/rig study, independent of the approved concert films.

Every animation is evaluated from absolute frame time or baked into F-curves.
This procedural pavilion is a test environment, not a church reconstruction.
"""
from __future__ import annotations

import bpy
from mathutils import Quaternion, Vector

from pipeline.motion import CameraTrack
from scenes.blender import heavenly
from scenes.blender.animation import (
    CharacterPerformance, bake_callback, bake_camera, bake_character, create_character,
)


SUPPORTS_BAKED_MOTION_BLUR = True


def build_scene(job):
    pavilion_update = heavenly.build_scene(job)
    scene = bpy.context.scene
    camera = scene.camera
    fps = job["video"]["fps"]
    shot = job["shot"]
    start = shot["start_frame"]
    end = shot["end_frame_exclusive"]
    params = shot.get("params", {})
    spec = params.get("camera_path", {"points": [[-4.0, -8.2, 3.4], [2.2, -7.6, 3.05]], "targets": [[0, 0, 1.35]]})
    track = CameraTrack.from_dict(spec, duration_seconds=(end - start) / fps)
    camera.data.lens = 43
    # Keep the original closure's object references alive, while replacing the
    # centre display with a character. No approved models are changed.
    for name in ("Floating pearl of light", "Central light plinth", "Central gold rim"):
        bpy.data.objects[name].hide_render = True
    gold = heavenly.material("Conductor warm light", "#efc875", .25, .4, .65)
    rig = create_character("Conductor", location=(0, -.5, .34), scale=1.0, material=gold, seed=job["seed"])
    local_events = [{**event, "frame": event["frame"] - start}
                    for event in job.get("timing", {}).get("events", [])]
    performance = CharacterPerformance(rig, action=params.get("performance", "conduct"),
                                       strength=.7, fps=fps, events=local_events)
    blur = job.get("motion_blur", {})
    if blur.get("enabled", False):
        options = {"substeps": blur.get("substeps", 2), "shutter": blur.get("shutter", .5)}
        ornaments = [obj for obj in scene.objects if obj.name.startswith(("Stream of colour", "Soft mote"))]
        ranges = []
        for frame in sorted(set(job["frames"])):
            if ranges and frame == ranges[-1][1]:
                ranges[-1][1] += 1
            else:
                ranges.append([frame, frame + 1])
        # A storyboard requests distant frames. Bake only their actual intervals
        # and shutter handles instead of filling all the unused time in between.
        for first, last in ranges:
            bake_callback(ornaments, pavilion_update, first, last, fps, **options)
            bake_camera(camera, track, first, last, fps, time_offset=start / fps, **options)
            bake_character(rig, performance, first, last, fps, time_offset=start / fps, **options)
        scene["pipeline_motion_baked"] = True

        def update(frame):
            # The worker sets scene.frame_set(frame + 1). Cycles also samples
            # these curves at shutter subframes to produce real motion blur.
            pass
    else:
        def update(frame):
            pavilion_update(frame)
            seconds = (frame - start) / fps
            performance.apply(seconds)
            sample = track.sample(seconds)
            camera.location = sample.position
            direction = Vector(sample.target) - camera.location
            if abs(direction.normalized().dot(Vector((0.0, 0.0, 1.0)))) > .9999:
                raise ValueError("Camera look direction is too close to Z-up; choose a target with a stable horizon.")
            camera.rotation_mode = "QUATERNION"
            camera.rotation_quaternion = direction.to_track_quat("-Z", "Y") @ Quaternion((0, 0, 1), sample.roll_radians)
    return update
