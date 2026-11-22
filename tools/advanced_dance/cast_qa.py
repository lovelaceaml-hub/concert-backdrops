"""Reuse final FK captures to check bodies and real fans across the ensemble.

No motion is solved again. The real fan model reads the exact final skeleton
captured by qa.py. Existing actor caches are restored afterwards. These are
conservative capsule-proxy checks, not full fabric or mesh intersection tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from p3d import bodymath as bm
from p3d.cloth import Colliders
from .qa import audit_cast_captures, capsule_clearance


def verify_capture_bytes(path, receipt):
    """Reject altered snapshots before using their geometry in a cast audit."""
    path = Path(path)
    identity = receipt.get("final_fk_capture", {})
    if (identity.get("bytes") != path.stat().st_size
            or identity.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest()):
        raise ValueError("The final FK capture does not match the hash-bound audit receipt")


def audit_cast_fans(bodies, fans, captures, *, review_penetration_m=.015):
    if len(bodies) != len(captures) or len(bodies) < 2:
        raise ValueError("Provide a final FK capture for each of at least two bodies")
    if any(body.frame is not None or body.scale != 1.0 for body in bodies):
        raise ValueError("This registered-cast audit expects unscaled bodies with no moving parent frame")
    data = [np.load(Path(path), allow_pickle=False) for path in captures]
    saved_caches = [dict(body.actor._cache) for body in bodies]
    try:
        times = data[0]["times"]
        for body, record in zip(bodies, data):
            if not np.array_equal(record["times"], times):
                raise ValueError("All final FK captures must share the exact frame clock")
            if list(record["bone_names"]) != body.rig.names:
                raise ValueError("Captured bones do not match the actual fan owner's rig")
        # NPZ members are decompressed once, not on every frame.
        frames = [{key: record[key] for key in ("P", "A", "M", "origin", "heading")} for record in data]
        colliders = [Colliders(body.rig) for body in bodies]
        owner = {id(body): k for k, body in enumerate(bodies)}
        records = {}
        for index, fan in enumerate(fans):
            if id(fan.body) not in owner:
                raise ValueError("A fan belongs to a body outside the supplied cast")
            source = owner[id(fan.body)]
            for target in range(len(bodies)):
                if target != source:
                    records[index, target] = {
                        "source_performer": bodies[source].actor.advanced_score.name,
                        "side": fan.side, "target_performer": bodies[target].actor.advanced_score.name,
                        "minimum_clearance_m": float("inf"), "time_seconds": None,
                        "body_group": None,
                    }
        for k, t in enumerate(times):
            t = float(t)
            caps = []
            for body, frame, collider in zip(bodies, frames, colliders):
                actor, rig = body.actor, body.rig
                sample = {key: frame[key][k] for key in ("P", "A", "M", "origin")}
                sample.update(D=bm.qmul(sample["A"], rig.C), heading=float(frame["heading"][k]), speed=0.)
                # Fan geometry only reads palm position/normal/finger direction.
                # Its scene-time clock still drives the real folding mechanism.
                actor._cache.clear()
                actor._cache[(round(t, 6), True, True, False)] = sample
                caps.append(collider.at(sample["M"]))
            for index, fan in enumerate(fans):
                points = fan.geometry(t, diagnostic=True)
                if not np.isfinite(points).all():
                    raise ValueError("The real fan model returned nonfinite surface geometry")
                for target, collider in enumerate(colliders):
                    key = (index, target)
                    if key not in records:
                        continue
                    distance = capsule_clearance(points, *caps[target], collider.ra, collider.rb)
                    point, capsule = np.unravel_index(int(distance.argmin()), distance.shape)
                    value = float(distance[point, capsule])
                    if value < records[key]["minimum_clearance_m"]:
                        records[key].update(minimum_clearance_m=value, time_seconds=t,
                                            body_group=collider.groups[capsule])
        pairs = list(records.values())
        issues = [dict(record, severity="review", check="fan_other_body_capsules") for record in pairs
                  if record["minimum_clearance_m"] < -review_penetration_m]
        return {"schema_version": 1, "status": "review_required" if issues else "proxy_clearance_pass",
                "sample_count": len(times), "fps": int(data[0]["fps"]), "fan_count": len(fans),
                "surface_points_per_fan": 75, "review_penetration_threshold_m": review_penetration_m,
                "pairs": pairs, "issues": issues,
                "scope": "Actual diagnostic fan surface against other bodies' existing capsule proxies on every captured frame.",
                "fan_to_fan_overlap_checked": False, "cloth_collision_checked": False,
                "physical_collision_validation": False}
    finally:
        for body, cache in zip(bodies, saved_caches):
            body.actor._cache.clear()
            body.actor._cache.update(cache)
        for record in data:
            record.close()


def main():
    from .scene import make_cast

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    bodies, fans = make_cast(True)
    captures = [args.captures/f"ensemble{role}.npz" for role in range(5)]
    receipts = [json.loads((args.captures/f"ensemble{role}.json").read_text()) for role in range(5)]
    root = Path(__file__).resolve().parents[2]
    # Cloth-only refinements cannot change these skeleton snapshots. Guard all
    # actual kinematic code and the precise actor configuration independently.
    kinematic = ("tools/advanced_dance/score.py", "tools/advanced_dance/anatomy.py",
                 "tools/advanced_dance/clock.json", "assets/p3d/body_v1.npz")
    kinematic += tuple(str(p.relative_to(root)) for p in sorted((root/"engine/p3d").glob("*.py")))
    hashes = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in kinematic}
    for body, capture, receipt in zip(bodies, captures, receipts):
        verify_capture_bytes(capture, receipt)
        if any(receipt["source_hashes"].get(name) != digest for name, digest in hashes.items()):
            raise ValueError("The actual kinematic source changed after a supplied FK capture")
        actual = receipt["actor"]
        if (actual["height_m"] != body.rig.height or actual["build"] != body.rig.build
                or actual["origin"] != body.actor.origin.tolist() or actual["seed"] != body.seed):
            raise ValueError("The actual cast rig or placement changed after its FK capture")
    body_report = audit_cast_captures([body.actor.advanced_score for body in bodies], captures)
    fan_report = audit_cast_fans(bodies, fans, captures)
    report = {"schema_version": 1,
              "status": "review_required" if body_report["issues"] or fan_report["issues"] else "proxy_clearance_pass",
              "kinematic_source_hashes": hashes,
              "cast_qa_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fan_source_sha256": hashlib.sha256((root/"tools/advanced_dance/props.py").read_bytes()).hexdigest(),
              "body": body_report, "fans": fan_report, "owner_approval": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": report["status"], "body_issues": body_report["issues"],
                      "fan_issues": fan_report["issues"], "out": str(args.out)}), flush=True)


if __name__ == "__main__":
    main()
