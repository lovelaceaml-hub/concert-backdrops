"""Protect the frame clock, path boundaries, and explicit render policy."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline.cli import frame_list
from pipeline.project import PipelineError, Project, load_project, safe_path, validate
from pipeline.render import guard_render


def project_fixture(root: Path) -> Project:
    (root / "scenes").mkdir()
    (root / "scenes/a.tsx").write_text("export const a = 1;\n")
    (root / "scenes/b.tsx").write_text("export const b = 1;\n")
    data = {
        "schema_version": 1,
        "project_id": "contract-test",
        "video": {"width": 32, "height": 18, "fps": 30},
        "production": {"cloud_gpu_provider": None, "allow_local_gpu": False, "allow_paid_services": False, "random_seed": 2026},
        "quality": {name: {"width": 32, "height": 18, "samples": 1} for name in ("draft", "review", "final")},
        "audio": {"source": None},
        "style": {"palette": {"gold": "#dda352"}},
        "timing": {"fps": 30, "events": [{"frame": 0, "kind": "cue"}]},
        "shots": [
            {"id": "a", "renderer": "threejs", "start_frame": 0, "end_frame_exclusive": 2, "scene": "scenes/a.tsx"},
            {"id": "b", "renderer": "threejs", "start_frame": 2, "end_frame_exclusive": 4, "scene": "scenes/b.tsx"},
        ],
    }
    manifest = root / "project.json"
    manifest.write_text(json.dumps(data))
    return Project(root, manifest, data)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.project = project_fixture(self.root)

    def test_valid_timeline_has_one_shared_clock(self):
        validate(self.project)
        self.assertEqual(self.project.frames, 4)
        for quality in ("draft", "review", "final"):
            self.assertEqual(self.project.settings(quality)["fps"], 30)

    def test_gap_overlap_and_empty_shot_are_rejected(self):
        for field, value in (("start_frame", 1), ("start_frame", 3), ("end_frame_exclusive", 2)):
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(self.project.data)
                data["shots"][1][field] = value
                with self.assertRaisesRegex(PipelineError, "no gaps or overlaps"):
                    validate(Project(self.root, self.project.manifest, data))

    def test_boolean_or_fractional_frames_are_rejected(self):
        for value in (True, 0.5, "0"):
            with self.subTest(value=value):
                self.project.data["shots"][0]["start_frame"] = value
                with self.assertRaisesRegex(PipelineError, "integer"):
                    validate(self.project)

    def test_quality_cannot_change_fps(self):
        self.project.data["quality"]["draft"]["fps"] = 15
        with self.assertRaisesRegex(PipelineError, "cannot change fps"):
            validate(self.project)

    def test_timing_cannot_use_another_clock_or_outside_frame(self):
        self.project.data["timing"]["fps"] = 60
        with self.assertRaisesRegex(PipelineError, "fixed project"):
            validate(self.project)
        self.project.data["timing"]["fps"] = 30
        self.project.data["timing"]["events"][0]["frame"] = 4
        with self.assertRaisesRegex(PipelineError, "outside the timeline"):
            validate(self.project)

    def test_no_gpu_provider_or_paid_dispatch(self):
        self.project.data["production"]["cloud_gpu_provider"] = "some-provider"
        with self.assertRaisesRegex(PipelineError, "No cloud GPU"):
            validate(self.project)
        self.project.data["production"]["cloud_gpu_provider"] = None
        self.project.data["production"]["allow_paid_services"] = True
        with self.assertRaisesRegex(PipelineError, "paid services"):
            validate(self.project)

    def test_mac_render_requires_invocation_flag(self):
        self.project.data["production"]["allow_local_gpu"] = True
        with patch("pipeline.render.platform.system", return_value="Darwin"):
            with self.assertRaisesRegex(PipelineError, "--allow-local-render"):
                guard_render(self.project)
            guard_render(self.project, allow_local=True)

    def test_repository_paths_cannot_escape(self):
        for path in ("../outside", str(self.root / "scenes/a.tsx")):
            with self.subTest(path=path), self.assertRaises(PipelineError):
                safe_path(self.root, path, exists=False)
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaisesRegex(PipelineError, "escapes"):
            safe_path(self.root, "escape/file", exists=False)

    def test_project_id_symlink_cannot_escape(self):
        with tempfile.TemporaryDirectory() as external:
            Path(external, "project.json").write_text(json.dumps(self.project.data))
            (self.root / "projects").mkdir()
            (self.root / "projects/contract-test").symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(PipelineError, "inside the repository"):
                load_project(self.root, "contract-test")

    def test_dependency_list_is_typed(self):
        self.project.data["shots"][0]["dependencies"] = "scenes/a.tsx"
        with self.assertRaisesRegex(PipelineError, "list of repository-relative"):
            validate(self.project)

    def test_ranges_are_half_open_and_deduplicated(self):
        self.assertEqual(frame_list("0:3,2,7"), [0, 1, 2, 7])


if __name__ == "__main__":
    unittest.main()
