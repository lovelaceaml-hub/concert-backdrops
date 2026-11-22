"""Fast, phrase-led fan choreography with explicit support and corrected hands.

The supplied moving performances inform pace, diagonal sweeps and ensemble
canon. This score is authored, not recovered motion capture. Covered reference
feet are never treated as measured contacts. All distances are metres.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from p3d import bodymath as bm
from .anatomy import AnatomyController

DURATION = 32.0
FPS = 60
DEG = np.pi / 180.0
CLOCKS = json.loads(Path(__file__).with_name("clock.json").read_text())
PHRASES = (
    "launch and opening fans", "diagonal traveling sweeps",
    "three traveling step turns", "low circles and rebound",
    "quick side chasses", "answering fan canon",
    "turning crescendo", "expanding flower and offering",
)


def curve(t, values):
    return PchipInterpolator(np.asarray(t, float), np.asarray(values, float), axis=0)


@dataclass(frozen=True)
class DanceStep:
    start: float
    end: float
    side: str
    source: tuple
    target: tuple
    source_yaw: float
    target_yaw: float
    lift: float
    pitch: float
    phrase: int


# One pair per musical count. Arcs pass through lateral and forward depth;
# paired hands deliberately avoid intersecting at the face or torso centre.
_RIGHT = (
    ((-.42,1.03,.28),(-.61,1.32,.16),(-.41,1.72,.12),(-.18,1.82,.15),
     (-.56,1.51,.17),(-.65,1.17,.12),(-.45,.91,.32),(-.24,1.35,.42)),
    ((-.62,1.54,.16),(-.38,1.80,.12),(-.20,1.51,.43),(-.54,1.10,.31),
     (-.64,.91,.12),(-.52,1.28,.22),(-.35,1.72,.12),(-.58,1.54,.14)),
    ((-.60,1.32,.12),(-.52,1.59,.10),(-.32,1.79,.12),(-.59,1.45,.14),
     (-.49,1.08,.24),(-.36,1.76,.14),(-.60,1.38,.12),(-.43,1.12,.30)),
    ((-.59,1.23,.20),(-.61,.90,.21),(-.43,.78,.34),(-.27,1.15,.43),
     (-.40,1.72,.15),(-.58,1.51,.12),(-.65,1.12,.17),(-.43,1.49,.31)),
    ((-.58,1.56,.14),(-.64,1.13,.21),(-.27,1.26,.44),(-.44,1.75,.13),
     (-.60,1.41,.15),(-.58,.95,.26),(-.31,1.27,.42),(-.54,1.64,.11)),
    ((-.55,1.29,.19),(-.29,1.76,.17),(-.50,1.62,.13),(-.61,1.10,.21),
     (-.43,.93,.34),(-.24,1.39,.44),(-.39,1.78,.15),(-.62,1.46,.15)),
    ((-.59,1.48,.14),(-.36,1.80,.13),(-.54,1.49,.10),(-.59,1.08,.22),
     (-.32,1.80,.15),(-.61,1.46,.12),(-.41,1.06,.31),(-.55,1.65,.13)),
    ((-.42,1.77,.15),(-.60,1.45,.17),(-.61,1.04,.24),(-.33,1.18,.43),
     (-.24,1.48,.40),(-.50,1.66,.14),(-.61,1.43,.18),(-.49,1.61,.18)),
)
_LEFT = (
    ((.47,1.47,.17),(.29,1.77,.13),(.59,1.33,.14),(.56,1.04,.23),
     (.38,1.19,.40),(.23,1.74,.15),(.56,1.60,.12),(.61,1.20,.16)),
    ((.43,1.05,.29),(.62,1.22,.15),(.46,1.72,.13),(.18,1.79,.16),
     (.53,1.54,.15),(.62,1.14,.13),(.45,.98,.26),(.24,1.40,.41)),
    ((.57,1.55,.14),(.42,1.14,.26),(.60,1.27,.11),(.32,1.79,.14),
     (.59,1.49,.12),(.56,1.12,.22),(.33,1.79,.13),(.61,1.41,.14)),
    ((.32,1.68,.17),(.56,1.30,.24),(.59,.87,.22),(.37,.91,.38),
     (.22,1.39,.42),(.40,1.78,.14),(.60,1.54,.12),(.58,1.12,.23)),
    ((.47,1.00,.30),(.29,1.41,.42),(.45,1.75,.13),(.63,1.35,.14),
     (.55,1.02,.23),(.31,1.32,.42),(.46,1.77,.14),(.61,1.39,.15)),
    ((.42,1.12,.33),(.57,1.25,.16),(.31,1.74,.16),(.52,1.58,.12),
     (.62,1.13,.20),(.45,.94,.32),(.25,1.40,.43),(.40,1.78,.14)),
    ((.42,1.06,.30),(.61,1.41,.15),(.32,1.81,.13),(.57,1.50,.12),
     (.54,1.12,.23),(.31,1.79,.14),(.61,1.47,.12),(.45,1.18,.29)),
    ((.42,1.77,.15),(.58,1.48,.16),(.61,1.06,.23),(.35,1.18,.43),
     (.24,1.48,.40),(.50,1.66,.14),(.61,1.43,.18),(.49,1.61,.18)),
)


class AdvancedScore:
    """Time-addressable support, body phrasing, turns, hands and fan action."""

    def __init__(self, actor, ensemble=False, role=0):
        self.actor, self.rig, self.mo = actor, actor.rig, actor.mo
        self.ensemble, self.role = bool(ensemble), int(role)
        self.mode = "ensemble" if ensemble else "solo"
        self.name = self.mode + str(role)
        self.duration = DURATION
        self.scale = self.rig.height / 1.65
        self._breathe = self.mo.breathe
        self.anatomy = AnatomyController(actor)
        beat_seconds = np.asarray(CLOCKS[self.mode]["beat_seconds"], float)
        self.beat_seconds = beat_seconds
        self.to_seconds = curve(np.arange(65), beat_seconds)
        self.to_beats = curve(beat_seconds, np.arange(65))
        self._init_motion()
        self._init_steps()

    def _init_motion(self):
        path_b = (0,4,8,10,12,14,16,18,20,22,24,26,28,30,32,
                  34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64)
        path = [(0,0),(-.20,.06),(0,.12),(-.40,.15),(-.73,-.08),(-.37,-.32),
                (-.15,-.30),(-.07,-.38),(.02,-.43),(.14,-.38),(.25,-.23),
                (.55,-.07),(.65,.16),(.34,.32),(.03,.24),(-.40,.21),
                (-.68,.07),(-.25,-.14),(.16,-.20),(.40,-.05),(.50,.18),
                (.25,.34),(0,.26),(-.10,.14),(-.03,.06),(.10,.16),(.08,.34),
                (0,.41),(-.08,.36),(0,.28),(0,.28)]
        if self.ensemble:
            side = np.sign(self.role - 2)
            factor = (.42 + .12*abs(self.role-2))
            path = [(x*.48-side*factor*math.sin(np.pi*b/64)**2,
                     z*.68+.30*math.sin(np.pi*b/64)) for b,(x,z) in zip(path_b,path)]
        self._path = curve(path_b, path)
        yaw_b = (0,4,8,12,16,17,18,19,20,21,22,23,24,26,28,30,32,
                 36,40,42,44,46,48,49,50,51,52,53,54,55,56,60,64)
        yaw = (-12,22,-12,35,0,45,180,360,540,720,900,1040,1080,
               1108,1053,1105,1080,1035,1080,1107,1120,1060,1080,
               1125,1260,1440,1620,1800,1980,2120,2160,2160,2160)
        self.turn_sign = -1 if self.ensemble and self.role in (0,1) else 1
        self._yaw = curve(yaw_b, np.asarray(yaw)*self.turn_sign)
        right, left = np.concatenate(_RIGHT), np.concatenate(_LEFT)
        # Low sweeps come from the plie and torso, not an arm stretched past
        # its length. Keep those palms inside a reachable lower side arc.
        for hand in (right,left):
            low=hand[:,1]<1.10
            hand[low,0]=np.clip(hand[low,0],-.50,.50)
            hand[low,1]=np.maximum(hand[low,1],1.04)
            hand[low,2]=np.minimum(hand[low,2],.28)
        if self.ensemble and self.role in (0,4):
            # Outer petals answer with one low fan while the centre is high.
            for k in range(40,48):
                right[k,1] = max(1.04,right[k,1]-.15)
                if right[k,1]<1.14:
                    right[k,0]=max(-.50,right[k,0])
                left[k,1] += .04
        if self.ensemble and self.role in (1,3):
            for k in range(40,48):
                right[k,1], left[k,1] = left[k,1], right[k,1]
        final = ((-.44,1.63,.18),(.44,1.63,.18))
        self._palms = {"R":curve(np.arange(65),np.vstack([right,final[0]])),
                       "L":curve(np.arange(65),np.vstack([left,final[1]]))}
        self._drop = curve(np.arange(0,65,2),
            (.08,.055,.12,.065,.08,.10,.13,.07,.075,.065,.07,.07,.10,
             .21,.26,.10,.08,.09,.07,.10,.08,.12,.075,.11,.07,.07,.065,
             .07,.06,.15,.11,.065,.055))
        self._lean = curve(np.arange(0,65,2),
            (6,-5,8,-5,3,-7,10,-6,3,-3,3,-2,8,17,22,-5,4,10,-6,
             6,-7,8,-5,4,2,-3,3,-3,-5,8,3,-4,-4))
        self._side = curve(np.arange(0,65,2),
            (2,-9,8,-7,5,-12,11,-5,0,-3,3,0,7,14,-15,8,-5,-12,
             12,-8,6,10,-8,6,0,3,-3,0,0,-7,7,0,0))
        self._twist = curve(np.arange(0,65,2),
            (-6,12,-14,9,-8,16,-15,8,0,-5,5,0,-12,17,-16,10,-8,
             15,-14,12,-9,13,-14,9,0,-4,4,0,0,-10,8,0,0))

    def beat(self, t):
        return float(self.to_beats(np.clip(t,0,self.beat_seconds[-1])))

    def _hand_beat(self, b):
        # A local canon only during its answering phrase; every role meets the
        # phrase boundaries and the final flower at the same clock time.
        if not self.ensemble or not 40 < b < 48:
            return b
        delay = (0.72,.36,0,.54,.90)[self.role]
        return b-delay*math.sin(np.pi*(b-40)/8)**2

    def _init_steps(self):
        N,i = self.rig.neutral_pos,self.rig.idx
        D,P,_ = self.mo.local_fk(self.mo.identity())
        M = self.rig.matrices(D,P)
        self.flat_lift = float(-self.rig.lowest(M))
        self.neutral_feet = {s:N[i["foot."+s]].copy() for s in ("L","R")}
        self._neutral_mid = (self.neutral_feet["L"]+self.neutral_feet["R"])*.5
        self._foot_local = {}
        for side in ("L","R"):
            j=i["foot."+side]
            v=self.rig.verts0[self.rig.vert_bone==j]
            self._foot_local[side]=v@M[j,:3,:3].T+M[j,:3,3]-P[j]
        yaw0=float(self._yaw(0))
        self.initial_feet,self.initial_yaw={},{}
        for side,sign in (("L",1),("R",-1)):
            off=self.neutral_feet[side]-self._neutral_mid
            off[0]+=sign*.033*self.scale
            p=bm.qrot(bm.qy(yaw0*DEG),off)+self._neutral_mid
            p[1]+=self.flat_lift
            self.initial_feet[side]=p
            self.initial_yaw[side]=yaw0+sign*6
        latest={s:p.copy() for s,p in self.initial_feet.items()}
        angles=self.initial_yaw.copy()
        steps=[]
        # Syncopated quick steps, sustained sweeping weight transfers and two
        # sixteen-step turning runs. There is always an explicit support foot.
        schedules = ((0,8,1.0),(8,16,.5),(16,24,.5),(24,32,1.0),
                     (32,40,.5),(40,48,1.0),(48,56,.5),(56,63.5,1.0))
        k=0
        for lo,hi,spacing in schedules:
            for b in np.arange(lo,hi-1e-7,spacing):
                end_b=min(b+spacing*.86,63.70)
                start=float(self.to_seconds(b+spacing*.08))
                end=float(self.to_seconds(end_b))
                side,sign=("R",-1) if k%2==0 else ("L",1)
                center=np.asarray(self._path(end_b))*self.scale
                yaw=float(self._yaw(end_b))
                off=self.neutral_feet[side]-self._neutral_mid
                off[0]+=sign*(.025 if lo in (16,48) else .045)*self.scale
                if lo==32:
                    off[0]+=sign*.035*self.scale
                    off[2]+=(.045 if k%4<2 else -.045)*self.scale
                p=bm.qrot(bm.qy(yaw*DEG),off)+self._neutral_mid
                p[[0,2]]+=center
                p[1]+=self.flat_lift
                lift=(.065 if lo in (16,48) else .085 if spacing<1 else .115)*self.scale
                # Place the foot for the middle of its following support
                # interval. Without this anticipation a fast turn can rotate
                # the pelvis more than 110 degrees over a trailing flat foot.
                contact_mid=min(64,end_b+.61*spacing)
                landing_yaw=float(self._yaw(contact_mid))+sign*6
                steps.append(DanceStep(start,end,side,tuple(latest[side]),tuple(p),
                    angles[side],landing_yaw,lift,12 if spacing<1 else 18,int(lo//8)))
                latest[side],angles[side]=p,landing_yaw
                k+=1
        self.steps=tuple(steps)

    def score_time(self,t):
        return float(np.clip(t,0,self.duration))

    def feet(self,t):
        t=self.score_time(t)
        p={s:x.copy() for s,x in self.initial_feet.items()}
        yaw=self.initial_yaw.copy()
        swing=None
        pitch=0.
        for step in self.steps:
            if t<=step.start:
                break
            if t>=step.end:
                p[step.side]=np.asarray(step.target)
                yaw[step.side]=step.target_yaw
                continue
            raw=(t-step.start)/(step.end-step.start)
            u=float(bm.smoother(raw))
            arc=math.sin(np.pi*u)
            p[step.side]=(1-u)*np.asarray(step.source)+u*np.asarray(step.target)
            p[step.side][1]+=step.lift*arc
            yaw[step.side]=(1-u)*step.source_yaw+u*step.target_yaw
            pitch=step.pitch*arc
            swing=(step.side,u)
            break
        rot={s:bm.qy(a*DEG) for s,a in yaw.items()}
        if swing:
            side,u=swing
            rot[side]=bm.qmul(rot[side],bm.qx(pitch*DEG))
            # Sole clearance is calculated on the authored foot orientation,
            # including the pointed swing toe, before the leg IK is solved.
            old_min=self._foot_local[side][:,1].min()
            new_min=bm.qrot(rot[side],self._foot_local[side])[:,1].min()
            p[side][1]+=max(0.,float(old_min-new_min))
        return p,rot,swing

    @lru_cache(maxsize=256)
    def _solved(self,t):
        b=self.beat(t)
        p=self.mo.identity()
        feet,rot,swing=self.feet(t)
        midpoint=(feet["L"]+feet["R"])*.5
        p.pos[[0,2]]=(midpoint-self._neutral_mid)[[0,2]]
        phase=0. if swing is None else math.sin(np.pi*swing[1])
        if swing:
            support="L" if swing[0]=="R" else "R"
            p.pos[[0,2]]+=.42*phase*(feet[support]-feet[swing[0]])[[0,2]]
        p.pos[1]=self.flat_lift-(float(self._drop(b))+.016*phase**2)*self.scale
        yaw=float(self._yaw(b))
        roll=(0 if swing is None else (1 if swing[0]=="R" else -1)*2.6*phase)
        yq=bm.qy(yaw*DEG)
        p.rot=bm.qmul(yq,bm.qz(roll*DEG))
        # Secondary breathing belongs before final hand and foot placement.
        # Applying it afterwards would move the already-solved palms again.
        self._breathe(p,t,self.actor.seed)
        lead_b=min(64,b+.12)
        self.mo._lean(p,1,fwd=float(self._lean(lead_b)),twist=float(self._twist(lead_b)),
                      side=float(self._side(lead_b))-.55*roll)
        spin=(16<b<24) or (48<b<56)
        spot=-52*math.tanh(1.4*math.sin(yaw*DEG)) if spin else -float(self._twist(b))*.55
        self.mo._head(p,1,up=5+7*math.sin(np.pi*b/8)**2,turn=spot,
                      tilt=-float(self._side(b))*.28)
        root=self.rig.neutral_pos[0]+p.pos
        hb=self._hand_beat(b)
        corrections,gesture_fits={},{}
        for side,sign in (("L",1),("R",-1)):
            target=self._palms[side](hb)*self.scale
            # A quiet final opening keeps breathing and a finished arm line
            # through the coda, rather than freezing the final numeric pose.
            coda=float(bm.smoother(np.clip((t-self.beat_seconds[-1])/
                                         (self.duration-self.beat_seconds[-1]),0,1)))
            target+=np.array([sign*.055*coda,-.05*coda,.035*coda])*self.scale
            palm=root+bm.qrot(yq,target-self.rig.neutral_pos[0])
            elevation=float(np.clip((target[1]/self.scale-1.35)/.45,0,1))
            self.mo._add(p,"clavicle."+side,bm.qz(sign*(4+9*elevation)*DEG))
            # Fit the phrase's directional cue to this performer's actual
            # posed shoulder and arm length. This smooth authoring envelope
            # preserves the direction and timing, with a bent-elbow margin.
            # Its correction is recorded separately from final IK accuracy.
            _,joints,_=self.mo.local_fk(p)
            shoulder=joints[self.rig.idx["upperarm01."+side]]
            raw_palm=palm.copy()
            direction=palm-shoulder
            radius=float(np.linalg.norm(direction))
            reach=sum(self.mo.arm_len[side])*.94+np.linalg.norm(self.anatomy._palm_offset[side])*.88
            softness=.023*self.scale
            fitted=radius-softness*np.logaddexp(0,(radius-reach)/softness)
            palm=shoulder+direction*(fitted/max(radius,1e-9))
            gesture_fits[side]=dict(raw_cue=raw_palm.tolist(),fitted_palm=palm.tolist(),
                correction_m=float(np.linalg.norm(raw_palm-palm)),reachable_radius_m=float(reach))
            # A changing palm plane is led through the forearm, with the wrist
            # limited by the anatomy controller instead of freely spun in space.
            bank=18*math.sin(np.pi*(hb+(.7 if side=="L" else 0))/2)
            normal=bm.qrot(yq,bm.qrot(bm.qy(sign*bank*DEG),[0,0,1]))
            pole=bm.qrot(yq,[sign*.62,-.76,-.38])
            corrections[side]=self.anatomy.hand(p,side,palm,fingers=None,
                normal=normal,pole=pole,grip=1.,flourish=.25*math.sin(np.pi*hb/2))
        for side,sign in (("L",1),("R",-1)):
            # The knee follows the actual toes, including a foot that lands
            # ahead of the turning pelvis. Rotation is distributed through
            # the hip instead of twisting a planted ankle under a forward knee.
            knee=bm.qrot(rot[side],[sign*.10,0,1]);knee[1]=0
            self.mo.leg_to(p,side,feet[side],knee=knee,foot=rot[side])
        p.ground,p.contact=0.,None
        return p,corrections,gesture_fits

    def pose(self,t):
        return self._solved(round(self.score_time(t),6))[0].copy()

    def anatomy_report(self,t):
        return self._solved(round(self.score_time(t),6))[1]

    def gesture_fit_report(self,t):
        return self._solved(round(self.score_time(t),6))[2]

    def diagnostics(self,t):
        feet,_,swing=self.feet(t)
        b=self.beat(t)
        return dict(role=self.name,score_time=self.score_time(t),beat=b,
            phrase=PHRASES[min(7,int(b//8))],
            contact={s:swing is None or swing[0]!=s for s in ("L","R")},
            swing=None if swing is None else swing[0],
            ankle_targets={s:p.tolist() for s,p in feet.items()},
            authored=True,reconstructed_reference_motion=False)

    def fan_open(self,t,side):
        b=self._hand_beat(self.beat(t))
        # A held, partially closing fan remains finite, with no prop teleport.
        local=b%8
        fold=math.sin(np.pi*np.clip((local-2)/3,0,1))**2 if int(b//8) in (1,3,4,5) else 0
        opposite=.7 if side=="L" else 1.
        return 1-.42*fold*opposite


def install(body,ensemble=False,role=0):
    actor=body.actor
    if actor._cache:
        raise ValueError("Install the score before sampling the body or cloth")
    score=AdvancedScore(actor,ensemble,role)
    actor.base_pose,actor.life=score.pose,False
    actor.mo.breathe=lambda pose,t,seed,depth=1.0:None
    original=actor.frame
    actor.frame=lambda t,**kw:original(round(float(t),6),**kw)
    actor.advanced_score=score
    actor._cache.clear()
    for name in ("_sk","_pts","_anchors"):
        cache=getattr(body,name,None)
        if cache is not None:
            cache.clear()
    return score
