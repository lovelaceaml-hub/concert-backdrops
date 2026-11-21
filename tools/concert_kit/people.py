"""The existing paired CMU capture, with a shared contact target for retargeting."""
import numpy as np
from p3d.body import Body
from p3d.pairs import pull_up
from p3d.actor import Actor
from p3d import looks
from p3d import bodymath as bm
from p3d import motion as motion_lib


class ConsiderationPair:
    def __init__(self, start=3.0, points=85000):
        self.start = start
        common = dict(shape="man", height=1.73, garment="tunic", hair="short",
            points=points, detail=dict(hand=3.5, head=1.8), bright=1.35,
            look=dict(name="glitter", seams=.65, glints=.0004),
            color="#efb85f", color2="#ffe4ad", wind=(.07,0,.025), gust=.08)
        refs = {}
        # Independent raw reference actors prevent the living-hand lag layer
        # from recursively consulting the partner's contact gesture history.
        proxies=[Actor("man",height=1.73,motion=[(start,name)],life=False,seed=seed)
                 for name,seed in (("pull_up",13.0),("helped_up",27.0))]
        def grip(t):
            return .5*(proxies[0].where(t,"palm.R",raw=True)+proxies[1].where(t,"palm.R",raw=True))
        contact = (start+1.8,start+4.65,"handshake",
            dict(side="R",to=grip,grip=.9,ease_in=.36,ease_out=.32,lean=0,look=False,antic=0,over=0))
        ka = {**common,"seed":13.0,"gesture":[contact,
              (start+7.4,start+8.5,"nod",dict(amount=4,period=1.2,ease=.35))]}
        kb = {**common,"seed":27.0,"color":"#f6cb83","gesture":[contact,
              (start+6.4,start+9.0,"hand_on_heart",dict(side="L",ease=.8,amount=.5))]}
        self.a,self.b=pull_up(start,a=ka,b=kb)
        # The capture ends in a departing step. Preserve the complete 6.5 s
        # performance, then settle at its final root positions into a mutual
        # acknowledgement rather than holding a raised foot indefinitely.
        settle=start+6.5
        frozen=[body.actor.base_pose(settle).copy() for body in (self.a,self.b)]
        for i,body in enumerate((self.a,self.b)):
            original=body.actor.base_pose
            end=frozen[i]
            direction=frozen[1-i].pos-end.pos
            yaw=np.arctan2(direction[0],direction[2])
            def settled(t,original=original,end=end,actor=body.actor,yaw=yaw):
                if t<=settle:
                    return original(t)
                rest=actor.mo.pose("stand",t,t-settle,seed=actor.seed)
                rest.pos=end.pos.copy()
                rest.pos[1]=0
                rest.rot=bm.qy(yaw)
                return motion_lib.blend(end,rest,float(bm.smoother((t-settle)/1.2)))
            body.actor.base_pose=settled
            body.actor._cache.clear()
        # Two overlapping hands need less emitted energy than two separate
        # silhouettes. Keep geometry detail while preventing a white knot.
        for body in (self.a,self.b):
            for layer in body.layers:
                hand=body.cloud["part"][layer["idx"]]==looks.HAND
                layer["alpha"]=np.asarray(layer["alpha"])*np.where(hand,.52,1.0)
        refs.update(a=self.a,b=self.b)
        self.refs=refs

    def add(self,scene):
        self.a.add(scene,"consideration_helper")
        self.b.add(scene,"consideration_recipient")

    def grip(self,t):
        return .5*(self.a.where(t,"palm.R")+self.b.where(t,"palm.R"))

    def evidence(self,t):
        return {"time":float(t),"palm_distance_m":float(np.linalg.norm(self.a.where(t,"palm.R")-self.b.where(t,"palm.R"))),
            "helper":{k:self.a.where(t,k).tolist() for k in ("pelvis","head","palm.R","foot.L","foot.R")},
            "recipient":{k:self.b.where(t,k).tolist() for k in ("pelvis","head","palm.R","foot.L","foot.R")}}
