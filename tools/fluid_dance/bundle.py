"""Frozen evaluated performances for the existing luminous renderer.

The authoring score is native Python/IK. Blender creates editable armature
keys and evaluates the final bake; this is not recovered motion capture.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from p3d import bodymath as bm
from p3d.actor import Actor
from p3d.assets import Rig


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "concert.performance.bundle.v1"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rig_identity(rig):
    return dict(shape=rig.shape, height_m=float(rig.height), build=float(rig.build),
                bone_names=rig.names, parents=rig.parent.tolist(),
                asset_sha256=sha256(ROOT / "assets/p3d/body_v1.npz"))


def _source_commit():
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          text=True, capture_output=True, check=True).stdout.strip()


def prepare_source(path, sample_hz=120, height=1.66, build=.96):
    """Sample the complete authored pose, with explicit neutral rig identity."""
    from .score import FluidScore
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    actor = Actor(rig=Rig("woman", height=height, build=build), at=(0, 0, 0), life=False)
    score = FluidScore(actor)
    n = int(round(score.duration * sample_hz)) + 1
    times = np.arange(n, dtype=np.float64) / sample_hz
    positions, rotations, contact, labels, fan_openings = [], [], [], [], []
    for t in times:
        pose = score.pose(float(t))
        _D, P, A = actor.mo.local_fk(pose)
        positions.append(P)
        rotations.append(A)
        if hasattr(score, "diagnostics"):
            diagnostics = score.diagnostics(float(t))
            c = diagnostics.get("contact", {})
            contact.append([bool(c.get(s, False)) for s in ("L", "R")])
            labels.append([diagnostics.get("support_labels",{}).get(s,"unknown") for s in ("L","R")])
        else:
            contact.append([False, False])
            labels.append(["unknown", "unknown"])
        fan_openings.append([score.fan_open(float(t),s) for s in ("L","R")])
    rig = actor.rig
    positions, rotations = np.asarray(positions), np.asarray(rotations)
    np.savez_compressed(path, times=times, positions=positions, world_rotations=rotations,
        bone_names=np.asarray(rig.names), parents=rig.parent,
        neutral_positions=rig.neutral_pos, neutral_directions=rig.neutral_dir,
        model_heads=rig.head, model_tails=rig.tail, neutral_correction=rig.C,
        contact=np.asarray(contact, dtype=np.uint8),support_labels=np.asarray(labels,dtype="U24"),
        fan_openings=np.asarray(fan_openings,dtype=np.float32),
        model_vertices=rig.verts0, model_triangles=rig.tris,
        weight_indices=rig.w_idx, weight_values=rig.w_val)
    manifest = dict(schema="concert.performance.authoring-input.v1",
        description="Original fan phrase authored with native controls and IK; input for an editable Blender armature and evaluated bake.",
        duration_seconds=float(score.duration), sample_rate=[sample_hz, 1], output_rate=[60, 1],
        samples=n, rig=rig_identity(rig), source_commit=_source_commit(),
        authored_score_sha256=sha256(Path(__file__).with_name("score.py")),
        source_npz_sha256=sha256(path),
        source_files={str(p.relative_to(ROOT)):sha256(p) for p in [
            Path(__file__),Path(__file__).with_name("score.py"),
            ROOT/"tools/advanced_dance/anatomy.py",ROOT/"engine/p3d/assets.py",
            ROOT/"engine/p3d/motion.py",ROOT/"engine/p3d/bodymath.py"]},
        support_annotation_origin="authored, not measured capture or force",
        support_labels=sorted(set(np.asarray(labels).ravel().tolist())),
        authoring_times=list(getattr(score,"authoring_times",())),
        capture=False, authoring="Python whole-body controls and IK", basis="right-handed +Y up, +Z forward, metres",
        review_status="awaiting artistic review")
    path.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


class PerformanceBundle:
    """Validated bake with shortest-path quaternion interpolation.

    Local rotations are in the native neutral frames. Their world composition
    is A; the native Rig.fk then applies its separately recorded modelled-rest
    correction C exactly once. Root translation is already absolute stage
    position. No neutral root height or root travel is added a second time.
    """

    def __init__(self, path, rig):
        path = Path(path)
        if path.is_dir():
            path = path / "performance.npz"
        if path.suffix == ".json":
            path = path.with_suffix(".npz")
        self.path = path
        self.manifest = json.loads(path.with_suffix(".json").read_text())
        if self.manifest.get("schema") != SCHEMA:
            raise ValueError("Unsupported evaluated performance schema")
        if self.manifest["npz_sha256"] != sha256(path):
            raise ValueError("Performance bundle bytes do not match manifest")
        expected = self.manifest["rig"]
        if expected["bone_names"] != rig.names or expected["parents"] != rig.parent.tolist():
            raise ValueError("Bundle skeleton differs from character")
        if expected["asset_sha256"] != sha256(ROOT / "assets/p3d/body_v1.npz"):
            raise ValueError("Bundle model asset changed")
        if expected["shape"] != rig.shape or abs(expected["height_m"] - rig.height) > 1e-7 or abs(expected["build"] - rig.build) > 1e-7:
            raise ValueError("Bundle body proportions differ from character")
        with np.load(path, allow_pickle=False) as data:
            self.times = data["times"].astype(np.float64)
            self.local = data["local_rotations"].astype(np.float64)
            self.root_rot = data["root_rotations"].astype(np.float64)
            self.root_pos = data["root_positions"].astype(np.float64)
            self.contact = data["contact"].astype(bool)
            self.support_labels=data["support_labels"] if "support_labels" in data else np.full((len(self.times),2),"unknown")
            self.fan_openings=data["fan_openings"].astype(np.float64) if "fan_openings" in data else np.ones((len(self.times),2))
            neutral = data["neutral_positions"].astype(np.float64)
            correction = data["neutral_correction"].astype(np.float64)
        if not np.allclose(neutral, rig.neutral_pos, atol=1e-8, rtol=0) or not np.allclose(correction, rig.C, atol=1e-8, rtol=0):
            raise ValueError("Bundle bind/neutral mapping differs from native rig")
        n, b = len(self.times), rig.nb
        if n < 2 or self.local.shape != (n,b,4) or self.root_rot.shape != (n,4) or self.root_pos.shape != (n,3):
            raise ValueError("Malformed performance array shapes")
        if not np.all(np.diff(self.times)>0) or not all(np.isfinite(a).all() for a in (self.times,self.local,self.root_rot,self.root_pos)):
            raise ValueError("Invalid performance time or numeric data")
        if np.max(np.abs(np.linalg.norm(self.local,axis=-1)-1)) > 1e-5 or np.max(np.abs(np.linalg.norm(self.root_rot,axis=-1)-1)) > 1e-5:
            raise ValueError("Performance contains non-unit rotations")
        self.rig = rig
        self.duration = float(self.times[-1])
        self.sample_rate = self.manifest["sample_rate"][0] / self.manifest["sample_rate"][1]

    @lru_cache(maxsize=256)
    def _frame(self, t):
        t = float(np.clip(t, self.times[0], self.times[-1]))
        idx = int(np.clip(np.searchsorted(self.times,t,side="right")-1,0,len(self.times)-2))
        u = (t-self.times[idx])/(self.times[idx+1]-self.times[idx])
        q = bm.qslerp(self.local[idx],self.local[idx+1],u)
        root_q = bm.qslerp(self.root_rot[idx],self.root_rot[idx+1],u)
        root = (1-u)*self.root_pos[idx]+u*self.root_pos[idx+1]
        D,P,A = self.rig.fk(q,root,root_q)
        return dict(D=D,P=P,A=A,M=self.rig.matrices(D,P),
                    origin=np.zeros(3),heading=0.,speed=0.)

    def frame(self,t,**_kwargs):
        return self._frame(round(float(t),9))

    def fan_open(self,t,side):
        if side not in ("L","R"):raise ValueError("Invalid fan side")
        return float(np.interp(float(t),self.times,self.fan_openings[:,0 if side=="L" else 1]))


def install_bundle(body, path):
    """Install before skin/cloth sampling. All native attachments use this bake."""
    if body.actor._cache or body._sk or body._pts:
        raise ValueError("Install the final performance before sampling the body")
    bundle = PerformanceBundle(path,body.rig)
    body.actor.frame = bundle.frame
    body.actor.life = False
    body.actor.performance_bundle = bundle
    if hasattr(body.actor,"advanced_score"):
        body.actor.advanced_score.fan_open=bundle.fan_open
    body.actor._cache.clear()
    return bundle


def validate_bundle(path, source_path, out=None):
    """Measured joint/skin agreement plus order independence on decoded bake."""
    metadata=json.loads(Path(path).with_suffix(".json").read_text())
    reference=metadata.get("evaluated_reference")
    if reference and sha256(source_path)!=reference["sha256"]:
        raise ValueError("Use this saved-Blender export's matching evaluated reference, not old authored poses")
    identity=metadata["rig"]
    rig=Rig(identity["shape"],height=identity["height_m"],build=identity["build"])
    bundle=PerformanceBundle(path,rig)
    with np.load(source_path,allow_pickle=False) as source:
        times=source["times"]
        positions=source["positions"]
        rotations=source["world_rotations"]
    # Full-grid joint/rotation comparison; selected full-skin comparisons.
    joint_max=rotation_max=skin_max=0.
    select=set(np.linspace(0,len(times)-1,17,dtype=int).tolist())
    for j,t in enumerate(times):
        f=bundle.frame(float(t))
        joint_max=max(joint_max,float(np.linalg.norm(f["P"]-positions[j],axis=1).max()))
        dot=np.abs(np.sum(f["A"]*rotations[j],axis=1))
        rotation_max=max(rotation_max,float(np.max(2*np.arccos(np.clip(dot,0,1)))))
        if j in select:
            D=bm.qmul(rotations[j],rig.C)
            before=rig.skin(rig.matrices(D,positions[j]))
            after=rig.skin(f["M"])
            skin_max=max(skin_max,float(np.linalg.norm(before-after,axis=1).max()))
    probe=np.unique(np.concatenate([np.linspace(0,bundle.duration,31),[.137,2.011,5.777,8.123,11.999]]))
    baseline={float(t):bundle.frame(float(t))["P"].copy() for t in probe}
    order=np.random.default_rng(20261122).permutation(probe)
    seek_error=max(float(np.max(np.abs(bundle.frame(float(t))["P"]-baseline[float(t)]))) for t in order)
    report=dict(schema="concert.performance.validation.v1",samples_compared=len(times),
        comparison_target=reference["comparison_target"] if reference else "original authored poses",
        maximum_joint_error_m=joint_max,maximum_rotation_error_radians=rotation_max,
        maximum_selected_skin_error_m=skin_max,random_seek_maximum_error_m=seek_error,
        blender_receipt=metadata["blender_validation"],
        pass_numeric=bool(joint_max<2e-5 and skin_max<3e-5 and rotation_max<.001 and seek_error<1e-12),
        artistic_review="not established by these measurements")
    if out: Path(out).write_text(json.dumps(report,indent=2)+"\n")
    return report


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True)
    prep=sub.add_parser("prepare");prep.add_argument("--out",required=True);prep.add_argument("--sample-hz",type=int,default=120)
    prep.add_argument("--height",type=float,default=1.66);prep.add_argument("--build",type=float,default=.96)
    val=sub.add_parser("validate");val.add_argument("--bundle",required=True);val.add_argument("--source",required=True);val.add_argument("--out")
    a=p.parse_args()
    if a.command=="prepare": result=prepare_source(a.out,a.sample_hz,a.height,a.build)
    else: result=validate_bundle(a.bundle,a.source,a.out)
    print(json.dumps(result,indent=2))
    if a.command=="validate" and not result["pass_numeric"]: raise SystemExit(2)


if __name__=="__main__": main()
