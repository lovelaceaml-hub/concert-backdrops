"""One continuous, deliberately authored fan phrase on the concert body rig.

This is original keyframe/control animation, not extracted motion capture.
Seven deliberate steps replace the earlier recurring alternating step schedule.
The pelvis has one continuous authored trajectory, including preparation before
foot release. During the turn, each supporting foot pivots about its rigid toe
tip; the existing asset has no independently articulated toe bones.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator

from p3d import bodymath as bm
from tools.advanced_dance.anatomy import AnatomyController

DURATION = 12.0
FPS = 60
DEG = math.pi / 180.0


def _ease(x):
    return float(bm.smoother(np.clip(x, 0., 1.)))


def _smooth_curve(times, values):
    return CubicSpline(np.asarray(times, float), np.asarray(values, float),
                       bc_type=((1, np.zeros(np.shape(values)[1:])),
                                (1, np.zeros(np.shape(values)[1:]))))


@dataclass(frozen=True)
class Step:
    start: float
    end: float
    side: str
    target_x: float
    target_z: float
    lift: float
    purpose: str


class FluidScore:
    """Deterministic controls, support annotations and final native rig poses."""

    duration = DURATION
    name = "fluid-solo"
    mode = "solo"
    role = 0
    ensemble = False
    authored = True
    reconstructed_reference_motion = False
    authoring_times = (0., .7, 1.4, 1.65, 2.1, 2.55, 2.9, 3.55, 4.25,
                       4.8, 5.0, 5.48, 5.6, 6.08, 6.2, 6.68, 6.8,
                       7.28, 7.8, 8.1, 8.8, 9.4, 10.2, 11.1, 12.)

    def __init__(self, actor):
        self.actor, self.rig, self.mo = actor, actor.rig, actor.mo
        self.scale = self.rig.height / 1.68
        self.anatomy = AnatomyController(actor)
        i, n = self.rig.idx, self.rig.neutral_pos
        d, p, _ = self.mo.local_fk(self.mo.identity())
        m = self.rig.matrices(d, p)
        self.flat_lift = float(-self.rig.lowest(m))
        self.neutral_feet = {s: n[i["foot." + s]].copy() for s in ("L", "R")}
        self._foot_local = {}
        self._toe = {}
        self.initial_feet = {}
        for side, sign in (("L", 1), ("R", -1)):
            j = i["foot." + side]
            verts = self.rig.verts0[self.rig.vert_bone == j]
            local = verts @ m[j, :3, :3].T + m[j, :3, 3] - p[j]
            self._foot_local[side] = local
            # A rigid toe-tip support proxy at the foot's front/lower extent.
            # The full foot geometry is checked separately after the solve.
            self._toe[side] = np.array([np.median(local[:, 0]),
                                        local[:, 1].min(), local[:, 2].max()])
            f = self.neutral_feet[side].copy()
            f[0] += sign * .022 * self.scale
            f[1] += self.flat_lift
            self.initial_feet[side] = f

        # Continuous whole-body travel. Hip motion is not calculated from a
        # per-step sine or reset to the foot midpoint at each landing.
        rt = [0, .8, 1.4, 1.65, 2.1, 2.55, 2.9, 3.3, 3.65, 4.3,
              4.8, 5.1, 5.55, 5.95, 6.4, 6.85, 7.35, 7.85, 8.1,
              8.7, 9.3, 10.2, 11.1, 12]
        rv = [(0,.0),(-.035,.0),(-.085,.0),(-.09,.0),(-.04,.02),
              (.13,.05),(.31,.06),(.345,.06),(.29,.06),(.27,.06),
              (.33,.10),(.34,.15),(.30,.18),(.255,.18),(.275,.15),
              (.33,.15),(.305,.16),(.27,.13),(.25,.11),(.19,.09),
              (.105,.09),(.12,.09),(.12,.09),(.12,.09)]
        self._root = PchipInterpolator(rt, rv, axis=0)
        self._yaw = PchipInterpolator(
            [0,1.4,2.6,3.8,4.4,4.8,5.3,5.9,6.5,7.1,7.65,8.2,9.2,10.5,12],
            [-9,-14,16,8,-12,0,65,150,235,315,357,360,370,360,360])
        self._drop = _smooth_curve(
            [0,.8,1.5,2.2,2.7,3.2,3.9,4.55,4.9,5.4,6.5,7.5,8.1,8.7,9.4,10.4,12],
            [.065,.07,.11,.125,.105,.085,.055,.105,.09,.075,.07,.075,.10,.12,.075,.055,.055])
        # Torso/attention keys describe the same reach and turn, with no
        # independent repeating sway added on top of the performed action.
        tt = [0,1.0,1.65,2.55,3.5,4.25,4.85,5.6,6.5,7.3,8.05,8.8,9.6,10.7,12]
        self._torso = _smooth_curve(tt, [
            (2,-3,-6),(4,-7,-10),(7,-9,-12),(1,9,10),(-4,7,14),
            (-6,2,6),(4,-3,-9),(-3,1,-4),(-2,0,0),(-2,1,3),
            (5,5,10),(12,-7,-12),(2,-3,-6),(-3,0,0),(-2,0,0)])
        self._head = _smooth_curve(tt, [
            (2,-8,2),(4,-15,3),(5,-20,5),(9,18,-5),(12,14,-3),
            (12,6,-2),(6,-12,2),(7,12,-2),(8,15,-2),(9,5,0),
            (4,-10,3),(3,-16,4),(8,-5,1),(11,0,0),(9,0,0)])
        ht = [0,.85,1.7,2.7,3.7,4.45,4.95,5.55,6.3,7.1,7.8,8.55,9.3,10.25,11.2,12]
        self._palms = {
            "L": _smooth_curve(ht, [
                (.30,1.06,.23),(.32,1.12,.26),(.40,1.16,.29),(.53,1.39,.16),
                (.33,1.72,.12),(.22,1.80,.13),(.36,1.61,.17),(.37,1.65,.16),
                (.32,1.72,.12),(.38,1.63,.14),(.50,1.38,.16),(.40,1.09,.28),
                (.31,1.23,.36),(.40,1.48,.26),(.44,1.55,.19),(.44,1.55,.19)]),
            "R": _smooth_curve(ht, [
                (-.30,1.06,.23),(-.39,1.02,.24),(-.50,1.10,.19),(-.33,1.59,.15),
                (-.48,1.41,.18),(-.53,1.22,.20),(-.38,1.24,.24),(-.36,1.51,.18),
                (-.33,1.68,.14),(-.38,1.56,.17),(-.40,1.13,.28),(-.48,1.02,.19),
                (-.32,1.23,.36),(-.40,1.48,.26),(-.44,1.55,.19),(-.44,1.55,.19)])}
        # Each event is named and placed for the phrase; there is no automatic
        # alternation generator. Turn landings follow the body's new direction.
        turn_centre = np.array([.30,.15])
        turn_steps = []
        for a,b,side in ((5.0,5.48,"R"),(5.6,6.08,"L"),
                          (6.2,6.68,"R"),(6.8,7.28,"L")):
            sg = 1 if side == "L" else -1
            y = float(self._yaw(b)) * DEG
            v = bm.qrot(bm.qy(y), [sg*.108,0,-.12])
            target = turn_centre + v[[0,2]]
            turn_steps.append(Step(a,b,side,*target,.035,"quarter-turn travel"))
        self.steps = (
            Step(1.65,2.55,"L",.38,.055,.045,"open lateral travel"),
            Step(2.95,3.55,"R",.17,.055,.035,"gather under supporting hip"),
            *turn_steps,
            Step(8.15,8.85,"R",-.035,.09,.038,"recover into offering"),
        )
        self._prepare_steps()

    def score_time(self,t):
        return float(np.clip(t,0,self.duration))

    def _pivot_amount(self,t):
        return _ease((t-4.65)/.35) * (1-_ease((t-7.85)/.4))

    def _stance(self,side,t,position,landing_time,landing_yaw):
        """Rigid toe pivot with fixed world contact point, flat outside turn."""
        sign = 1 if side == "L" else -1
        amt=self._pivot_amount(t)
        at_land=self._pivot_amount(landing_time)
        base_rot=bm.qmul(bm.qy(landing_yaw*DEG),bm.qx(8*at_land*DEG))
        pivot=np.asarray(position)+bm.qrot(base_rot,self._toe[side])
        turn_start=max(4.65,landing_time)
        turn_time=min(max(t,turn_start),7.85)
        entered=_ease((t-turn_start)/.22) if landing_time<7.85 else 0.
        yaw=landing_yaw + (float(self._yaw(turn_time))-float(self._yaw(turn_start))) * entered
        rot=bm.qmul(bm.qy(yaw*DEG),bm.qx(8*amt*DEG))
        return pivot-bm.qrot(rot,self._toe[side]),rot

    def _prepare_steps(self):
        latest={s:(p.copy(),0.,(8 if s=="L" else -8)-9) for s,p in self.initial_feet.items()}
        self._resolved=[]
        for step in self.steps:
            side=step.side
            p0,r0=self._stance(side,step.start,*latest[side])
            yaw=float(self._yaw(step.end))+(8 if side=="L" else -8)
            rot=bm.qmul(bm.qy(yaw*DEG),bm.qx(8*self._pivot_amount(step.end)*DEG))
            target=np.array([step.target_x*self.scale,
                             self.neutral_feet[side][1]+self.flat_lift,
                             self.neutral_feet[side][2]+step.target_z*self.scale])
            # Sole rests on the plane at landing, including a raised heel.
            target[1]=-float(bm.qrot(rot,self._toe[side])[1])
            self._resolved.append((step,p0,r0,target,rot,yaw))
            latest[side]=(target,step.end,yaw)

    def feet(self,t):
        t=self.score_time(t)
        latest={s:(p.copy(),0.,(8 if s=="L" else -8)-9) for s,p in self.initial_feet.items()}
        active=None
        for item in self._resolved:
            st,p0,r0,p1,r1,yaw=item
            if t>=st.end:
                latest[st.side]=(p1,st.end,yaw)
            elif t>st.start:
                active=item
        positions={}; rotations={}; labels={}
        for side in ("L","R"):
            positions[side],rotations[side]=self._stance(side,t,*latest[side])
            labels[side]="toe_pivot" if self._pivot_amount(t)>1e-6 else "flat_support"
        if active:
            st,p0,r0,p1,r1,yaw=active
            u=(t-st.start)/(st.end-st.start)
            e=_ease(u)
            positions[st.side]=(1-e)*p0+e*p1
            # Zero endpoint speed and acceleration for the swing clearance.
            positions[st.side][1]+=st.lift*self.scale*64*u**3*(1-u)**3
            rotations[st.side]=bm.qslerp(r0,r1,e)
            labels[st.side]="free"
        return positions,rotations,labels

    @lru_cache(maxsize=1024)
    def _solved(self,t):
        p=self.mo.identity()
        yaw=float(self._yaw(t))
        p.rot=bm.qy(yaw*DEG)
        p.pos[[0,2]]=np.asarray(self._root(t))*self.scale
        # The root joint sits behind the hip midpoint in this asset. Keep the
        # authored hip trajectory stable when the character turns around it.
        hip_mid=(self.rig.neutral_pos[self.rig.idx['upperleg01.L']]+
                 self.rig.neutral_pos[self.rig.idx['upperleg01.R']])*.5
        hip_offset=hip_mid-self.rig.neutral_pos[0]
        compensation=hip_offset-bm.qrot(p.rot,hip_offset)
        p.pos[[0,2]]+=compensation[[0,2]]
        p.pos[1]=self.flat_lift-float(self._drop(t))*self.scale
        # Slight torso lead is part of the authored phrase, not cyclic noise.
        fwd,side,twist=self._torso(min(12,t+.08))
        self.mo._lean(p,1,fwd=float(fwd),side=float(side),twist=float(twist))
        up,turn,tilt=self._head(t)
        self.mo._head(p,1,up=float(up),turn=float(turn),tilt=float(tilt))
        root=self.rig.neutral_pos[0]+p.pos
        corrections={}
        for side,sign in (("L",1),("R",-1)):
            target=np.asarray(self._palms[side](t))*self.scale
            # Elevation lifts the clavicle before the hand solve.
            elevation=np.clip((target[1]/self.scale-1.28)/.46,0,1)
            self.mo._add(p,"clavicle."+side,bm.qz(sign*(3+9*elevation)*DEG))
            palm=root+bm.qrot(p.rot,target-self.rig.neutral_pos[0])
            _,joints,_=self.mo.local_fk(p)
            shoulder=joints[self.rig.idx["upperarm01."+side]]
            v=palm-shoulder; radius=float(np.linalg.norm(v))
            reach=sum(self.mo.arm_len[side])*.94+np.linalg.norm(self.anatomy._palm_offset[side])*.88
            soft=.025*self.scale
            fitted=radius-soft*np.logaddexp(0,(radius-reach)/soft)
            palm=shoulder+v*fitted/max(radius,1e-9)
            pole=bm.qrot(p.rot,[sign*.55,-.75,-.42])
            normal=bm.qrot(p.rot,[0,0,1])
            corrections[side]=self.anatomy.hand(p,side,palm,normal=normal,pole=pole,grip=1)
        feet,rot,labels=self.feet(t)
        for side,sign in (("L",1),("R",-1)):
            knee=bm.qrot(rot[side],[sign*.08,0,1]); knee[1]=0
            self.mo.leg_to(p,side,feet[side],knee=knee,foot=rot[side])
        p.ground=0.;p.contact=None
        return p,corrections

    def pose(self,t):
        return self._solved(round(self.score_time(t),7))[0].copy()

    def anatomy_report(self,t):
        return self._solved(round(self.score_time(t),7))[1]

    def diagnostics(self,t):
        t=self.score_time(t)
        feet,rot,labels=self.feet(t)
        p=self.pose(t); _,joints,_=self.mo.local_fk(p)
        return dict(score_time=t,authored=True,reconstructed_reference_motion=False,
            support_labels=labels,contact={s:labels[s]!="free" for s in labels},
            ankle_targets={s:feet[s].tolist() for s in feet},
            ankle_error_m={s:float(np.linalg.norm(joints[self.rig.idx['foot.'+s]]-feet[s])) for s in feet},
            root_position=p.pos.tolist(),yaw_degrees=float(self._yaw(t)))

    def fan_open(self,t,side):
        t=self.score_time(t)
        # The held fans narrow during preparation and unfurl with the sweep.
        keys=[0,.9,1.5,2.8,4.5,5.2,7.7,8.6,9.7,12]
        values=[.78,.74,.70,1.,1.,.86,.92,.72,1.,1.]
        return float(PchipInterpolator(keys,values)(t))


def install(body):
    """Install before cloth/skin samples; compatible with current fan props."""
    actor=body.actor
    if actor._cache:
        raise ValueError("Install FluidScore before sampling the character")
    score=FluidScore(actor)
    actor.base_pose=score.pose
    actor.life=False
    actor.mo.breathe=lambda pose,t,seed,depth=1.:None
    actor.fluid_score=score
    actor.advanced_score=score
    actor._cache.clear()
    return score
