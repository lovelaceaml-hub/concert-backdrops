"""Exact reusable cloth snapshots, keyed by actual authored inputs.

The cached positions are the original solver's float32 snapshots. Loading a
cache adds no retiming, resampling, pose interpolation or image approximation.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
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


def load_cloth(body):
    """Reuse a previously completed simulation; return False if absent."""
    policy=os.environ.get("ADVANCED_DANCE_CLOTH_CACHE","auto")
    if policy not in ("auto","off","required"):
        raise ValueError("ADVANCED_DANCE_CLOTH_CACHE must be auto, off or required")
    if policy=="off":
        return False
    path=ROOT/"work/advanced-dance/cloth-cache"/(motion_key(body)+".npy")
    if not path.is_file():
        if policy=="required":
            raise FileNotFoundError("Complete the declared costume bake first: "+str(path))
        return False
    data=np.load(path,mmap_mode="r",allow_pickle=False)
    expected=int(np.ceil(body.actor.advanced_score.duration*30))+2
    if data.dtype!=np.float32 or data.shape!=(expected,body.cloth.n,3):
        raise ValueError("Invalid completed dance cloth cache: "+str(path))
    body.cloth.snaps=list(data)
    # _ensure recognises an initialized system. This complete cache serves
    # only the declared performance range; it cannot resume simulation.
    body.cloth.x=np.asarray(data[-1],np.float64)
    body.cloth.xp=body.cloth.x.copy()
    body.cloth.t0=body.cloth.t_start
    body.cloth.steps=(len(data)-1)*4
    body.advanced_cloth_cache=str(path)
    return True


def bake_cloth(body):
    """Complete and atomically save one exact deterministic costume bake."""
    if load_cloth(body):
        return body.advanced_cloth_cache
    body.cloth.positions(body.actor.advanced_score.duration)
    data=np.asarray(body.cloth.snaps,dtype=np.float32)
    if not np.isfinite(data).all():
        raise ValueError("Nonfinite cloth cannot enter the completed cache")
    path=ROOT/"work/advanced-dance/cloth-cache"/(motion_key(body)+".npy")
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.stem+f".{os.getpid()}.partial.npy")
    np.save(temp,data,allow_pickle=False)
    temp.replace(path)
    return str(path)
