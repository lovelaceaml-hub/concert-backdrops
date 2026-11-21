"""Usable starting projects. Presets never modify an existing film."""
from __future__ import annotations


def cinematic_project(project_id: str, title: str, fps: int = 60, seconds: int = 10) -> dict:
    duration = float(seconds)
    return {
        "schema_version": 1, "project_id": project_id, "title": title,
        "description": "Procedural camera and character study. Replace the study with authored scenes after visual review.",
        "video": {"width": 3840, "height": 2160, "fps": fps},
        "audio": {"source": None, "offset_seconds": 0},
        "production": {"cloud_gpu_provider": None, "allow_local_gpu": False,
            "allow_paid_services": False, "allow_ai_generated_visuals": False,
            "allow_stock_footage": False, "random_seed": 2026,
            "threads": 4, "render_chunk_frames": 1, "render_timeout_seconds": 7200},
        "delivery": {"profile": "hevc10", "source_transfer": "srgb", "color_space": "rec709",
            "profiles_by_quality": {"draft": "h264", "review": "h264", "4k-check": "hevc10", "final": "hevc10"}},
        "quality": {
            "motion-check": {"width": 320, "height": 180, "samples": 2, "image_bit_depth": 8,
                "motion_blur": {"enabled": True, "shutter": .5, "substeps": 2}},
            "draft": {"width": 960, "height": 540, "samples": 8, "image_bit_depth": 8,
                "motion_blur": {"enabled": True, "shutter": .5, "substeps": 2}},
            "review": {"width": 1920, "height": 1080, "samples": 24, "image_bit_depth": 16,
                "motion_blur": {"enabled": True, "shutter": .5, "substeps": 2}},
            "4k-check": {"width": 3840, "height": 2160, "samples": 8, "image_bit_depth": 16,
                "motion_blur": {"enabled": True, "shutter": .5, "substeps": 2}},
            "final": {"width": 3840, "height": 2160, "samples": 64, "image_bit_depth": 16,
                "motion_blur": {"enabled": True, "shutter": .5, "substeps": 4}},
        },
        "style": "styles/zion-cinematic.json",
        "timing": {"fps": fps, "visual_only": True, "manually_verified": False,
            "note": "Example visual cues, not verified song hits. Replace after listening to the actual recording.",
            "events": [
                {"frame": min(seconds * fps - 1, round(fps * duration * .3)), "kind": "lift", "amplitude": .45,
                    "attack_frames": max(1, round(fps * .7)), "release_frames": max(1, round(fps * 1.3))},
                {"frame": min(seconds * fps - 1, round(fps * duration * .68)), "kind": "resolve", "amplitude": .3,
                    "attack_frames": max(1, round(fps * .8)), "release_frames": max(1, round(fps * 1.7))},
            ]},
        "shots": [{"id": "motion-study", "name": "Golden conductor and flowing camera",
            "renderer": "blender", "start_frame": 0, "end_frame_exclusive": seconds * fps,
            "scene": "scenes/blender/motion_study.py",
            "params": {"performance": "conduct", "camera_path": {
                "seconds": [0, duration * .32, duration * .68, duration],
                "points": [[-4.0, -8.2, 3.4], [-2.4, -7.4, 2.9], [.1, -7.2, 2.7], [2.2, -7.6, 3.05]],
                "targets": [[0, 0, 1.3], [0, 0, 1.35], [0, 0, 1.35], [0, 0, 1.4]],
                "easing": "smootherstep"}}}],
    }
