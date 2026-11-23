"""Negative acceptance tests for the one-run reviewed-host assembly boundary."""
import copy
import unittest

from tools.s11_delivery import assemble_reviewed as a


class ReviewedHostValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = a.load_contract()
        packages = {}
        for line in a.git_blob("tools/s11_renewed/requirements-render.txt").decode().splitlines():
            if line and not line.startswith("#"):
                name, value = line.split("==")
                packages[name] = value
        host = next(iter(a.HOSTS.values()))
        runtime = dict(
            python="3.12.14", packages=packages, architecture="x86_64",
            github_image="ubuntu24", **host,
            environment=dict(PYTHONHASHSEED="0", LP_NUM_THREADS="2",
                             OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                             NUMBA_NUM_THREADS="1", LIBGL_ALWAYS_SOFTWARE="1"),
            ffmpeg="ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023 the FFmpeg developers",
            openssl="OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)",
            mesa_packages="libegl-mesa0=25.2.8-0ubuntu0.24.04.5\nlibgl1-mesa-dri=25.2.8-0ubuntu0.24.04.5",
            mesa_query_status=0)
        cls.original = dict(
            schema="s11-cloud-picture-v1", request=cls.contract["request"],
            request_sha256=a.REQUEST_SHA, sources=cls.contract["manifest"]["picture_sources"],
            adapter=cls.contract["adapter"], runtime=runtime, waveform_included=False,
            width=1920, height=1080, fps=60, samples=2, crf=14, picture_delay=0.1,
            temporal_interpolation=False, spatial_upscale=False)
        cls.original["fingerprint"] = a.c.mapping_digest(cls.original)
        if cls.original["fingerprint"] != next(iter(a.HOSTS)):
            raise AssertionError("Fixture does not reconstruct the observed producing identity.")

    def setUp(self):
        self.value = copy.deepcopy(self.original)

    def rehash(self):
        self.value.pop("fingerprint", None)
        self.value["fingerprint"] = a.c.mapping_digest(self.value)

    def test_observed_first_host(self):
        self.assertEqual(a.validate_identity(self.value, self.contract), self.value["fingerprint"])

    def test_observed_second_host(self):
        fingerprint, host = list(a.HOSTS.items())[1]
        self.value["runtime"].update(host)
        self.rehash()
        self.assertEqual(self.value["fingerprint"], fingerprint)
        self.assertEqual(a.validate_identity(self.value, self.contract), fingerprint)

    def test_unrecomputed_full_fingerprint_rejected(self):
        self.value["runtime"]["packages"]["numpy"] = "0.0.0"
        with self.assertRaisesRegex(ValueError, "full fingerprint"):
            a.validate_identity(self.value, self.contract)

    def test_changed_source_with_valid_hash_rejected(self):
        key = next(iter(self.value["sources"]))
        self.value["sources"][key] = "0" * 64
        self.rehash()
        with self.assertRaisesRegex(ValueError, "source map"):
            a.validate_identity(self.value, self.contract)

    def test_changed_dependency_with_valid_hash_rejected(self):
        self.value["runtime"]["packages"]["numpy"] = "2.5.4"
        self.rehash()
        with self.assertRaisesRegex(ValueError, "rendering dependencies"):
            a.validate_identity(self.value, self.contract)

    def test_changed_request_with_valid_hash_rejected(self):
        self.value["request"]["samples"] = 3
        self.rehash()
        with self.assertRaisesRegex(ValueError, "producing request"):
            a.validate_identity(self.value, self.contract)

    def test_changed_request_digest_rejected(self):
        self.value["request_sha256"] = "0" * 64
        self.rehash()
        with self.assertRaisesRegex(ValueError, "producing request"):
            a.validate_identity(self.value, self.contract)

    def test_changed_adapter_rejected(self):
        key = next(iter(self.value["adapter"]))
        self.value["adapter"][key] = "0" * 64
        self.rehash()
        with self.assertRaisesRegex(ValueError, "adapter"):
            a.validate_identity(self.value, self.contract)

    def test_unknown_host_even_with_same_normalized_contract_rejected(self):
        self.value["runtime"]["github_image_version"] = "20261116.999.1"
        self.rehash()
        with self.assertRaisesRegex(ValueError, "host fingerprint"):
            a.validate_identity(self.value, self.contract)

    def test_changed_thread_control_rejected(self):
        self.value["runtime"]["environment"]["LP_NUM_THREADS"] = "1"
        self.rehash()
        with self.assertRaisesRegex(ValueError, "rendering dependencies"):
            a.validate_identity(self.value, self.contract)

    def receipt(self, part=0):
        return dict(schema="s11-cloud-picture-chunk-v1", fingerprint=self.original["fingerprint"],
                    request_id=a.REQUEST_ID, part=part, parts=40,
                    start=16500 * part // 40, end=16500 * (part + 1) // 40,
                    width=1920, height=1080, fps=60, samples=2, waveform_included=False)

    def test_altered_assigned_range_rejected(self):
        receipt = self.receipt(7)
        receipt["start"] += 1
        with self.assertRaisesRegex(ValueError, "assigned range"):
            a.validate_receipt_meta(receipt, self.original["fingerprint"], self.contract["request"])

    def test_receipt_cannot_use_other_allowed_fingerprint(self):
        receipt = self.receipt()
        receipt["fingerprint"] = list(a.HOSTS)[1]
        with self.assertRaisesRegex(ValueError, "identity"):
            a.validate_receipt_meta(receipt, self.original["fingerprint"], self.contract["request"])

    def test_complete_coverage(self):
        a.validate_coverage([self.receipt(i) for i in range(40)], self.contract["request"])

    def test_missing_part_rejected(self):
        with self.assertRaisesRegex(ValueError, "every requested"):
            a.validate_coverage([self.receipt(i) for i in range(39)], self.contract["request"])

    def test_duplicate_part_rejected(self):
        parts = [self.receipt(i) for i in range(39)] + [self.receipt(38)]
        with self.assertRaisesRegex(ValueError, "every requested"):
            a.validate_coverage(parts, self.contract["request"])

    def test_gap_and_overlap_rejected(self):
        for shift in (-1, 1):
            parts = [self.receipt(i) for i in range(40)]
            parts[20]["start"] += shift
            with self.subTest(shift=shift), self.assertRaisesRegex(ValueError, "ranges"):
                a.validate_coverage(parts, self.contract["request"])


if __name__ == "__main__":
    unittest.main()
