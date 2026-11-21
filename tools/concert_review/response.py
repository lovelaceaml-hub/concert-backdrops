"""Independent numeric regression check for the Consideration hand return.

This evaluates the actual pair and the installed response without rendering a
picture or advancing cloth. Full samples stay beside the compact QA report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/concert-motion-review"
ANCHORS = ("palm.L", "elbow.L", "wrist.L", "upperarm01.L")
VARIANTS = ("baseline_live", "baseline_no_life", "revised_live", "revised_no_life")
BASE_IDENTITY = "2fa9e0fce212be765d639fbb85acf8cdb755e5a92d995dae418fa66fbd7eae6e"


def digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def mapping_digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def source_identity():
    from tools.concert_kit.render import source_hashes
    return {
        "base_kit_source_sha256": mapping_digest(source_hashes()),
        "response_sha256": digest(ROOT / "tools/concert_motion_revision/response.py"),
        "checker_sha256": digest(__file__),
        "body_asset_sha256": digest(ROOT / "assets/p3d/body_v1.npz"),
    }


def aggregate(raw):
    import numpy as np

    times = np.array(raw["times"])
    result = {}
    for name in VARIANTS:
        metrics = {}
        for rate, stride in ((120, 1), (60, 2)):
            for label, lower, upper in (("whole", 9.3, 12.5), ("release", 11.5, 12.4)):
                indices = np.where((times >= lower) & (times <= upper))[0][::stride]
                sample_times = times[indices]
                values = {}
                for anchor in ANCHORS:
                    points = np.array(raw[name][anchor]["samples"])[indices]
                    steps = np.linalg.norm(np.diff(points, axis=0), axis=1)
                    peak = int(np.argmax(steps))
                    acceleration = np.linalg.norm(np.diff(points, axis=0, n=2) * rate**2, axis=1)
                    values[anchor] = {
                        "max_step_m": float(steps[peak]),
                        "interval_seconds": [float(sample_times[peak]), float(sample_times[peak+1])],
                        "max_acceleration_m_s2": float(acceleration.max()),
                    }
                metrics[f"{label}_{rate}hz"] = values
        result[name] = metrics
    return result


def critical_samples(raw):
    """Short windows cover the actual pop and the continuous revised return."""
    result = {}
    windows = ((11.5, 11.55), (11.7, 11.725), (11.833333333333, 11.866666666667), (12.3, 12.316666666667))
    for rate, stride in ((120, 1), (60, 2)):
        result[str(rate)] = [
            {"source_seconds": t,
             **{variant: {anchor: [round(x, 9) for x in raw[variant][anchor]["samples"][index]]
                          for anchor in ("palm.L", "elbow.L", "wrist.L")}
                for variant in ("baseline_live", "revised_live")}}
            for index, t in enumerate(raw["times"])
            if index % stride == 0 and any(low - 1e-10 <= t <= high + 1e-10 for low, high in windows)
        ]
    return result


def compact_report(raw, raw_path):
    metrics = aggregate(raw)
    checks = {
        "baseline_pop_reproduced": metrics["baseline_live"]["release_60hz"]["palm.L"]["max_step_m"] > .1,
        "revised_release_palm_under_4cm_per_60fps_frame": all(metrics[name]["release_60hz"]["palm.L"]["max_step_m"] < .04 for name in ("revised_live", "revised_no_life")),
        "revised_release_palm_under_2cm_per_120hz_sample": all(metrics[name]["release_120hz"]["palm.L"]["max_step_m"] < .02 for name in ("revised_live", "revised_no_life")),
        "revised_release_elbow_under_2cm_per_60fps_frame": metrics["revised_live"]["release_60hz"]["elbow.L"]["max_step_m"] < .02,
        "revised_whole_gesture_palm_under_5cm_per_60fps_frame": metrics["revised_live"]["whole_60hz"]["palm.L"]["max_step_m"] < .05,
        "revised_release_acceleration_under_regression_limit": metrics["revised_live"]["release_60hz"]["palm.L"]["max_acceleration_m_s2"] < 50,
        "earlier_right_contact_unchanged": raw["unchanged_prior_contact_max_abs_m"] <= 1e-10,
        "out_of_order_repeat_identical": raw["out_of_order_repeat_max_abs_m"] <= 1e-12,
        "duplicate_install_rejected": raw["duplicate_install_rejected"],
        "source_unchanged": raw.get("source_unchanged", True),
    }
    return {
        "schema_version": 1,
        "check": "consideration-v2 response continuity",
        "passed": all(checks.values()),
        "checks": checks,
        "source_identity": raw.get("source_identity", {"base_kit_source_sha256": BASE_IDENTITY,
                           "response_sha256": raw["response_source_sha256"]}),
        "method": {
            "scope": raw["note"], "source_seconds": [9.3, 12.5], "native_frame_rate": 60,
            "sample_rate": 120, "unused_surface_points": 1000, "cloth_evaluated": False,
            "picture_rendered": False,
            "comparison": "Actual frozen pair before and after install_response, with living hands enabled and disabled.",
            "threshold_note": "These limits detect the measured solver discontinuity. They are not general human-motion standards or aesthetic approval.",
        },
        "revision": raw["revision"],
        "measurements": metrics,
        "critical_transition_samples": critical_samples(raw),
        "unchanged_prior_contact_max_abs_m": raw["unchanged_prior_contact_max_abs_m"],
        "out_of_order_repeat_max_abs_m": raw["out_of_order_repeat_max_abs_m"],
        "full_raw_evidence": {"path": str(raw_path.relative_to(ROOT)) if raw_path.is_relative_to(ROOT) else str(raw_path),
                              "sha256": digest(raw_path), "bytes": raw_path.stat().st_size},
        "elapsed_seconds": raw["elapsed_seconds"],
    }


def measure():
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Start this numeric check with PYTHONHASHSEED=0.")
    if "P3D_BODY_ASSET" in os.environ:
        raise RuntimeError("Unset P3D_BODY_ASSET before checking the registered body.")
    os.environ.update(P3D_CACHE=str(WORK / "cache"), NUMBA_CACHE_DIR=str(WORK / "numba"),
                      OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "engine"))
    import numpy as np
    from tools.concert_kit.people import ConsiderationPair
    from tools.concert_motion_revision.response import install_response

    sources = source_identity()
    if sources["base_kit_source_sha256"] != BASE_IDENTITY:
        raise RuntimeError("Frozen base kit source changed; review this regression fixture.")
    started = time.monotonic()
    pair = ConsiderationPair(points=1000)
    actor = pair.b.actor
    times = np.arange(1116, 1501, dtype=float) / 120.0

    def sample(life):
        actor.life = life
        actor._cache.clear()
        values = {name: {"samples": []} for name in ANCHORS}
        for t in times:
            for name in ANCHORS:
                values[name]["samples"].append(actor.where(float(t), name).tolist())
        return values

    def contact_positions():
        actor.life = True
        actor._cache.clear()
        return {str(t): {who: body.where(t, "palm.R").tolist()
                        for who, body in (("helper", pair.a), ("recipient", pair.b))}
                for t in (3., 4.8, 5.3, 6., 6.9, 7.5, 8.1, 9.3)}

    before_contact = contact_positions()
    result = {}
    for name, life in (("baseline_live", True), ("baseline_no_life", False)):
        result[name] = sample(life)
        print(f"Measured {name}", flush=True)
    revision = install_response(pair)
    for name, life in (("revised_live", True), ("revised_no_life", False)):
        result[name] = sample(life)
        print(f"Measured {name}", flush=True)
    after_contact = contact_positions()
    contact_error = max(float(np.max(np.abs(np.array(before_contact[t][who]) - after_contact[t][who])))
                        for t in before_contact for who in ("helper", "recipient"))
    actor.life = True
    actor._cache.clear()
    order = (12.3, 9.4, 11.5333333333, 10.2, 11.8, 9.3, 12.5)
    first = {t: actor.where(t, "palm.L").copy() for t in order}
    actor._cache.clear()
    repeat_error = max(float(np.max(np.abs(actor.where(t, "palm.L") - first[t]))) for t in reversed(order))
    duplicate_rejected = False
    try:
        install_response(pair)
    except RuntimeError:
        duplicate_rejected = True
    return {"note": "Actual ConsiderationPair and actual installed response; points=1000 only reduces unused body surface generation. No cloth/picture render.",
            "source_identity": sources, "source_unchanged": source_identity() == sources,
            "response_source_sha256": sources["response_sha256"],
            "times": times.tolist(), "revision": revision, **result,
            "unchanged_prior_contact_max_abs_m": contact_error,
            "out_of_order_repeat_max_abs_m": repeat_error,
            "duplicate_install_rejected": duplicate_rejected,
            "elapsed_seconds": time.monotonic()-started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=WORK / "response-qa.json")
    args = parser.parse_args()
    output = args.out.resolve()
    raw_path = output.with_name(output.stem + "-raw.json")
    raw = measure()
    write_json(raw_path, raw)
    report = compact_report(raw, raw_path)
    write_json(output, report)
    print(json.dumps({"passed": report["passed"], "report": str(output), "raw": str(raw_path),
                      "checks": report["checks"], "elapsed_seconds": raw["elapsed_seconds"]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
