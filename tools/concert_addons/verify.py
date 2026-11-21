"""Small geometry/contact checks for the independent native model prototypes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

from .models import Dove, Rose, Wheat

ROOT = Path(__file__).resolve().parents[2]


def _identity(batches):
    result = hashlib.sha256()
    for batch in batches:
        for key in sorted(batch):
            value = batch[key]
            result.update(key.encode())
            if isinstance(value, np.ndarray):
                result.update(str(value.shape).encode())
                result.update(value.tobytes())
            else:
                result.update(repr(value).encode())
    return result.hexdigest()


def verify():
    sys.path.insert(0, str(ROOT / "engine"))
    from p3d.api import normalize
    cases = [Dove(), Rose(variant="blush"), Rose(variant="crimson"),
             Rose(variant="golden"), Wheat(variant="ripe"), Wheat(variant="green")]
    report = {"status": "passed", "owner_approval": "pending", "models": []}
    for model in cases:
        before = _identity(model.sample(1.65))
        for t in (0, .65, .8, 1.1, 2.2, 4.7, 4.9, 5.6):
            for batch in model.sample(t):
                normalize(batch)
                assert np.isfinite(batch["pos"]).all()
                if "normal" in batch:
                    lengths = np.linalg.norm(batch["normal"], axis=1)
                    assert np.max(np.abs(lengths-1)) < 1e-5
        after = _identity(model.sample(1.65))
        assert before == after, "An out-of-order sample changed the result"
        assert after != _identity(model.sample(1.65+1/120)), "No subframe motion was evaluated"
        report["models"].append({"constructor": type(model).__name__,
                                  "variant": getattr(model, "variant", "ivory"),
                                  "points_and_segments": sum(len(b["pos"]) for b in model.sample(1.65)),
                                  "out_of_order_deterministic": True,
                                  "subframe_positions_change": True})
    dove = cases[0]
    contacts = {}
    for name, times in (("launch", (0, .45, .65, dove.launch)),
                        ("landing", (dove.land, 5.1, 5.6, 6))):
        points = np.asarray([dove.anchors(t)["feet"] for t in times])
        error = float(np.max(np.linalg.norm(points-points[0], axis=-1)))
        assert error < 1e-12, "A planted foot moved"
        contacts[name+"_foot_drift_metres"] = error
    jumps = []
    bone_error = []
    for event in (dove.launch, dove.land):
        a = np.asarray(dove.anchors(event-1e-6)["feet"])
        b = np.asarray(dove.anchors(event+1e-6)["feet"])
        jumps.append(float(np.max(np.linalg.norm(b-a, axis=1))))
    assert max(jumps) < 1e-6, "Foot release or contact has a discontinuity"
    for t in np.linspace(0, 6, 31):
        for wing in dove.anchors(t)["wings"].values():
            s, e, w = [np.asarray(wing[k]) for k in ("shoulder", "elbow", "wrist")]
            bone_error.extend([abs(np.linalg.norm(e-s)-.145*dove.scale),
                               abs(np.linalg.norm(w-e)-.150*dove.scale)])
    assert max(bone_error) < 1e-10, "A wing bone stretched during folding"
    contacts["maximum_boundary_jump_metres"] = max(jumps)
    contacts["maximum_wing_bone_length_error_metres"] = max(bone_error)
    report["contacts"] = contacts
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = verify()
    encoded = json.dumps(report, indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()
