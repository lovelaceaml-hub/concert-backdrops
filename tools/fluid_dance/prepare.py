"""Bake and validate a costume against the exact evaluated performance."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/fluid-dance"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _bundle_file():
    p = Path(os.environ.get("FLUID_DANCE_BUNDLE", WORK / "performance"))
    return p / "performance.npz" if p.is_dir() else p


def cloth_identity(body):
    paths = [_bundle_file(), _bundle_file().with_suffix(".json"),
             ROOT / "tools/fluid_dance/costume.py",
             ROOT / "tools/advanced_dance/costume.py",
             ROOT / "engine/p3d/cloth.py", ROOT / "engine/p3d/body.py",
             ROOT / "engine/p3d/assets.py", ROOT / "assets/p3d/body_v1.npz"]
    return dict(schema_version=1, duration_seconds=12.0,
                snapshot_rate_hz=30, solver_rate_hz=120,
                shape=[362, body.cloth.n, 3], dtype="float32",
                body_height=float(body.rig.height), origin=body.actor.origin.tolist(),
                seed=float(body.seed), costume=body.advanced_costume,
                inputs={str(p.relative_to(ROOT)): digest(p) for p in paths})


def load_cloth(body, path):
    path = Path(path)
    receipt = json.loads(path.with_suffix(".json").read_text())
    expected = cloth_identity(body)
    if receipt.get("status") != "complete" or receipt.get("identity") != expected:
        raise ValueError("The costume cache does not match this evaluated performance.")
    payload = path.read_bytes()
    if len(payload) != receipt["bytes"] or hashlib.sha256(payload).hexdigest() != receipt["sha256"]:
        raise ValueError("Costume cache bytes differ from the saved receipt.")
    states = np.load(io.BytesIO(payload), allow_pickle=False)
    if states.dtype != np.float32 or list(states.shape) != expected["shape"] or not np.isfinite(states).all():
        raise ValueError("Invalid costume snapshot data.")
    body.cloth.snaps = list(states)
    body.cloth.x = np.asarray(states[-1], np.float64)
    body.cloth.xp = body.cloth.x.copy()
    body.cloth.t0 = body.cloth.t_start
    body.cloth.steps = (len(states) - 1) * 4
    body.fluid_cloth_receipt = receipt
    return True


def bake(path=WORK / "cloth.npy"):
    for p in (ROOT, ROOT / "engine"):
        sys.path.insert(0, str(p))
    from tools.fluid_dance.scene import make_performer
    from tools.fluid_dance.bundle import install_bundle
    from tools.advanced_dance.costume import audit_cloth
    if os.environ.get("FLUID_DANCE_CLOTH"):
        raise RuntimeError("Unset FLUID_DANCE_CLOTH while deliberately preparing a new bake.")
    bundle = _bundle_file()
    body = make_performer(install_performance=lambda b: install_bundle(b, bundle))
    initial = cloth_identity(body)
    path = Path(path)
    if path.exists() and path.with_suffix(".json").exists():
        try:
            load_cloth(body, path)
            return body.fluid_cloth_receipt
        except (ValueError, KeyError):
            pass
    start = time.monotonic()
    for t in range(13):
        body.cloth.positions(float(t))
        print(json.dumps({"event": "cloth_bake", "seconds": t,
                          "elapsed": round(time.monotonic() - start, 2)}), flush=True)
    states = np.asarray(body.cloth.snaps, np.float32)
    if list(states.shape) != initial["shape"] or not np.isfinite(states).all():
        raise ValueError("Incomplete or nonfinite costume bake.")
    if cloth_identity(body) != initial:
        raise RuntimeError("Costume inputs changed during the bake.")
    try:
        audit = audit_cloth(body)
    except (AttributeError, TypeError) as error:
        # The previous audit may depend on score-specific fields. Never mark
        # that absent review as a pass; the full moving cloth still needs review.
        audit = {"status": "not_evaluated", "reason": str(error)}
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent, prefix="cloth-bake-") as tmp:
        stage = Path(tmp) / "cloth.npy"
        np.save(stage, states, allow_pickle=False)
        payload = stage.read_bytes()
        receipt = dict(status="complete", identity=initial,
                       bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(),
                       elapsed_seconds=round(time.monotonic() - start, 3), audit=audit)
        meta = Path(tmp) / "cloth.json"
        meta.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
        stage.replace(path)
        meta.replace(path.with_suffix(".json"))
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=WORK / "cloth.npy")
    a = p.parse_args()
    receipt = bake(a.out)
    # The complete per-snapshot audit stays in the receipt beside the cache.
    # Keep a normal preparation run readable at the command line.
    audit = receipt.get("audit", {})
    print(json.dumps({"status": receipt["status"], "cache": str(a.out),
                      "receipt": str(a.out.with_suffix(".json")),
                      "sha256": receipt["sha256"], "bytes": receipt["bytes"],
                      "audit": {key: value for key, value in audit.items()
                                if key not in ("samples", "failures")}},
                     indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
