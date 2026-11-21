"""Narrow clock, source and namespace checks for the independent auditor."""
import copy
import json
from pathlib import Path
import unittest

import numpy as np

from consideration import (
    CANONICAL_SAMPLES, DEFAULT_PROJECT, PROFILES, RATE, alignment_window,
    audit_directory, program_audio, review_frames, validate_profile,
)


ROOT = Path(__file__).resolve().parents[2]


class ConsiderationAuditTests(unittest.TestCase):
    def manifest(self, name):
        return json.loads((ROOT / "projects" / name / "project.json").read_text())

    def test_both_explicit_profiles_match_the_registered_projects(self):
        for name, profile in PROFILES.items():
            with self.subTest(project=name):
                validate_profile(self.manifest(name), profile)

    def test_changed_audio_source_offset_or_extra_gain_is_rejected(self):
        profile = PROFILES["concert-kit-consideration-v2"]
        for field, value in (("offset_seconds", 0), ("source_sha256", "0" * 64),
                             ("gain_db", -0.5), ("fade_in_seconds", 0.1)):
            with self.subTest(field=field):
                manifest = self.manifest(profile.project)
                manifest["audio"][field] = value
                with self.assertRaisesRegex(RuntimeError, "Audio source/offset"):
                    validate_profile(manifest, profile)

    def test_changed_shot_clock_scene_or_params_is_rejected(self):
        profile = PROFILES["concert-kit-consideration-v2"]
        for field, value in (("end_frame_exclusive", 235),
                             ("scene", "tools/concert_kit/consideration.py"),
                             ("params", {"source_start": 3})):
            with self.subTest(field=field):
                manifest = self.manifest(profile.project)
                manifest["shots"][0][field] = value
                with self.assertRaisesRegex(RuntimeError, "Scene, shot boundaries"):
                    validate_profile(manifest, profile)

    def test_wrong_profile_or_cut_map_is_rejected(self):
        profile = PROFILES["concert-kit-consideration-v2"]
        manifest = self.manifest(profile.project)
        with self.assertRaisesRegex(RuntimeError, "Project identity"):
            validate_profile(manifest, PROFILES[DEFAULT_PROJECT])
        altered = copy.deepcopy(manifest)
        altered["timing"]["events"][0]["frame"] = 233
        with self.assertRaisesRegex(RuntimeError, "Authored cut"):
            validate_profile(altered, profile)

    def test_reference_pcm_is_cropped_once_at_the_declared_source_offset(self):
        canonical = np.broadcast_to(np.arange(CANONICAL_SAMPLES)[:, None], (CANONICAL_SAMPLES, 2))
        original = program_audio(canonical, PROFILES[DEFAULT_PROJECT])
        revised = program_audio(canonical, PROFILES["concert-kit-consideration-v2"])
        self.assertEqual(len(original), 18 * RATE)
        self.assertEqual(len(revised), 15 * RATE)
        self.assertEqual(revised[0, 0], 3 * RATE)
        self.assertEqual(revised[-1, 0], CANONICAL_SAMPLES - 1)
        self.assertTrue(np.shares_memory(canonical, revised))
        with self.assertRaisesRegex(RuntimeError, "does not cover"):
            program_audio(canonical[:-1], PROFILES["concert-kit-consideration-v2"])

    def test_original_and_revised_baselines_have_separate_locations(self):
        original = audit_directory(ROOT, PROFILES[DEFAULT_PROJECT])
        revised = audit_directory(ROOT, PROFILES["concert-kit-consideration-v2"])
        self.assertEqual(original, ROOT / "work/production-system/final-qa")
        self.assertEqual(revised, original / "concert-kit-consideration-v2")
        self.assertNotEqual(original, revised)

    def test_random_native_samples_are_repeatable_and_cover_cut_neighbors(self):
        for profile in PROFILES.values():
            selected, random = review_frames(profile, list(profile.cuts))
            self.assertEqual((selected, random), review_frames(profile, list(profile.cuts)))
            self.assertEqual(len(random), 8)
            self.assertTrue(all(0 <= f < profile.frames for f in selected))
            self.assertTrue(set(random).issubset(selected))
            for cut in profile.cuts:
                self.assertTrue({cut - 1, cut, cut + 1}.issubset(selected))

    def test_alignment_lag_sign_and_zero_are_measured_from_samples(self):
        samples = np.random.default_rng(701).normal(0, 0.05, (24000, 2))
        for lag in (0, 7, -11):
            with self.subTest(lag=lag):
                measured = alignment_window(samples, np.roll(samples, lag, axis=0), 6000, 18000, 64)
                self.assertEqual(measured["best_lag_samples"], lag)
                self.assertGreater(measured["best_correlation"], 0.999999)


if __name__ == "__main__":
    unittest.main()
