"""Exact reusable cloth snapshots, keyed by actual authored inputs.

The cached positions are the original solver's float32 snapshots. Loading a
cache adds no retiming, resampling, pose interpolation or image approximation.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import numpy as np

ROOT=Path(__file__).resolve().parents[2]


def motion_key(body):
    paths=[ROOT/"tools/advanced_dance"/n for n in
           ("score.py","anatomy.py","costume.py","clock.json","cache.py")]
    paths.extend((ROOT/"engine/p3d").glob("*.py"))
    paths.append(ROOT/"assets/p3d/body_v1.npz")
    source={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    score=body.actor.advanced_score
    source["instance"]=dict(mode=score.mode,role=score.role,height=body.rig.height,
        origin=body.actor.origin.tolist(),seed=body.seed,costume=body.advanced_costume,
        duration=score.duration)
    return hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()


def _cache_path(key):
    return ROOT / "work/advanced-dance/cloth-cache" / (key + ".npy")


def _identity(body, key, path):
    score = body.actor.advanced_score
    return dict(schema_version=1, status="complete", mode=score.mode,
                role=score.role, motion_key=key, duration_seconds=score.duration,
                snapshot_rate_hz=30, solver_rate_hz=120,
                cache=str(path.relative_to(ROOT)),
                shape=[int(np.ceil(score.duration * 30)) + 2, body.cloth.n, 3],
                dtype="float32")


def _validate_states(data, body):
    expected = (int(np.ceil(body.actor.advanced_score.duration * 30)) + 2,
                body.cloth.n, 3)
    if not isinstance(data, np.ndarray) or data.dtype != np.float32 or data.shape != expected:
        raise ValueError("Invalid completed dance cloth cache shape or dtype")
    if not np.isfinite(data).all():
        raise ValueError("Nonfinite cloth cannot enter the completed cache")


def _read_completed(body, key, path):
    """Read one receipt-bound immutable byte snapshot, or an incomplete pair."""
    receipt_path = path.with_suffix(".json")
    if not path.is_file() or not receipt_path.is_file():
        return None
    receipt_bytes = receipt_path.read_bytes()
    try:
        receipt = json.loads(receipt_bytes)
    except (ValueError, UnicodeError) as error:
        raise ValueError("Invalid dance cloth completion receipt: " + str(receipt_path)) from error
    if not isinstance(receipt, dict):
        raise ValueError("Invalid dance cloth completion receipt: " + str(receipt_path))
    if receipt.get("status") == "incomplete":
        return None
    if any(receipt.get(name) != value for name, value in _identity(body, key, path).items()):
        raise ValueError("Dance cloth completion receipt identity does not match this performer")
    # Hash the exact bytes that are decoded, rather than hashing the path and
    # later reopening it for an unrelated mmap. Atomic replacement cannot make
    # the installed states refer to different bytes after this validation.
    payload = path.read_bytes()
    if len(payload) != receipt.get("bytes") or hashlib.sha256(payload).hexdigest() != receipt.get("sha256"):
        raise ValueError("Dance cloth cache bytes do not match their completion receipt")
    data = np.load(io.BytesIO(payload), allow_pickle=False)
    _validate_states(data, body)
    if receipt_path.read_bytes() != receipt_bytes or motion_key(body) != key:
        raise RuntimeError("Cloth source or completion receipt changed while loading")
    return data, receipt


def load_cloth(body):
    """Install only a complete verified cache; absent/incomplete pairs are misses."""
    policy = os.environ.get("ADVANCED_DANCE_CLOTH_CACHE", "auto")
    if policy not in ("auto", "off", "required"):
        raise ValueError("ADVANCED_DANCE_CLOTH_CACHE must be auto, off or required")
    if policy == "off":
        return False
    key = motion_key(body)
    path = _cache_path(key)
    completed = _read_completed(body, key, path)
    if completed is None:
        if policy == "required":
            raise FileNotFoundError("Complete the declared costume bake and receipt first: " + str(path))
        return False
    data, receipt = completed
    body.cloth.snaps = list(data)
    # _ensure recognises an initialized system. This complete cache serves
    # only the declared performance range; it cannot resume simulation.
    body.cloth.x = np.asarray(data[-1], np.float64)
    body.cloth.xp = body.cloth.x.copy()
    body.cloth.t0 = body.cloth.t_start
    body.cloth.steps = (len(data) - 1) * 4
    body.advanced_cloth_cache = str(path)
    body.advanced_cloth_receipt = receipt
    return True


def _receipt_metadata(receipt, metadata):
    extras = dict(metadata() if callable(metadata) else (metadata or {}))
    protected = {"schema_version", "status", "mode", "role", "motion_key",
                 "duration_seconds", "snapshot_rate_hz", "solver_rate_hz",
                 "cache", "shape", "dtype", "bytes", "sha256"}
    if protected.intersection(extras):
        raise ValueError("Audit metadata cannot replace cloth completion identity fields")
    return dict(receipt, **extras)


def _write_receipt(path, receipt):
    path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")


def bake_cloth(body, *, source_guard=None, receipt_metadata=None):
    """Publish exact snapshots and their receipt only while pinned inputs hold.

    ``source_guard`` may check additional inputs; it must raise on a change.
    ``receipt_metadata`` is an optional mapping or factory for audit fields.
    An incomplete receipt marks interrupted publication as a recoverable miss.
    """
    key = motion_key(body)
    path = _cache_path(key)

    def unchanged_sources():
        if motion_key(body) != key:
            raise RuntimeError("Authored sources changed during cloth baking; repeat after freezing the inputs")
        if source_guard is not None:
            source_guard()

    unchanged_sources()
    if load_cloth(body):
        unchanged_sources()
        if receipt_metadata is not None:
            receipt = _receipt_metadata(body.advanced_cloth_receipt, receipt_metadata)
            with tempfile.TemporaryDirectory(prefix=key + ".", suffix=".partial", dir=path.parent) as temporary:
                staged_receipt = Path(temporary) / "complete.json"
                _write_receipt(staged_receipt, receipt)
                # Metadata enrichment must still bind the exact loaded bytes.
                payload = path.read_bytes()
                if len(payload) != receipt["bytes"] or hashlib.sha256(payload).hexdigest() != receipt["sha256"]:
                    raise RuntimeError("Cloth cache changed before audit receipt publication")
                unchanged_sources()
                staged_receipt.replace(path.with_suffix(".json"))
            body.advanced_cloth_receipt = receipt
        return str(path)
    body.cloth.positions(body.actor.advanced_score.duration)
    data = np.asarray(body.cloth.snaps, dtype=np.float32)
    _validate_states(data, body)
    unchanged_sources()
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=key + ".", suffix=".partial", dir=path.parent) as temporary:
        temporary = Path(temporary)
        staged_array = temporary / "snapshots.npy"
        np.save(staged_array, data, allow_pickle=False)
        payload = staged_array.read_bytes()
        receipt = _receipt_metadata(dict(_identity(body, key, path),
                                        bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest()),
                                    receipt_metadata)
        staged_receipt = temporary / "complete.json"
        _write_receipt(staged_receipt, receipt)
        pending_receipt = temporary / "incomplete.json"
        _write_receipt(pending_receipt, dict(schema_version=1, status="incomplete", motion_key=key))
        unchanged_sources()
        pending_receipt.replace(path.with_suffix(".json"))
        unchanged_sources()
        staged_array.replace(path)
        unchanged_sources()
        if path.read_bytes() != payload:
            raise RuntimeError("Cloth cache changed before completion receipt publication")
        unchanged_sources()
        staged_receipt.replace(path.with_suffix(".json"))
    return str(path)
