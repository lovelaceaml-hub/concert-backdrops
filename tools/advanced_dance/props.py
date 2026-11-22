"""Articulated held fans and light released by the solved choreography."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import numpy as np

from p3d.api import lin, ribbon
from .anatomy import grip_frame
from .cache import motion_key,ROOT


class PerformanceFan:
    """A finite pleated fan with opening ribs and a transverse finger grip."""
    def __init__(self,body,side="R",radius=.42,color="#cf86ce",seed=1,points=8200):
        self.body,self.side,self.radius=body,side,float(radius)
        self.score=body.actor.advanced_score
        self.color=lin(color)
        self.edge=lin("#f2c8dc")
        rng=np.random.default_rng(seed)
        self.r=self.radius*np.sqrt(rng.uniform(.025,1,points))
        self.u=rng.uniform(-.5,.5,points)
        self.grain=rng.uniform(.76,1.20,points)
        self.rib_u=np.linspace(-.5,.5,25)
        self.handle_u=np.linspace(-.034,.034,18)
        self.handle_a=np.linspace(0,2*np.pi,12,endpoint=False)

    def hand_frame(self,t):
        return grip_frame(self.body,float(t),self.side)

    def geometry(self,t,diagnostic=False):
        p,across,outward,normal=self.hand_frame(t)
        spread=np.radians(162)*self.score.fan_open(t,self.side)
        if diagnostic:
            u=np.linspace(-.5,.5,15)
            r=np.linspace(.09,self.radius,5)
            rr,uu=np.meshgrid(r,u)
            a=uu.ravel()*spread
            return p+rr.ravel()[:,None]*(np.sin(a)[:,None]*across+np.cos(a)[:,None]*outward)
        a=self.u*spread
        pleat=.010*np.sin(self.u*48*np.pi)*self.r/self.radius
        pos=p+self.r[:,None]*(np.sin(a)[:,None]*across+np.cos(a)[:,None]*outward)+pleat[:,None]*normal
        return pos,(p,across,outward,normal),spread

    def tip(self,t):
        p,_,outward,_=self.hand_frame(t)
        return p+outward*self.radius

    def sample(self,t):
        pos,(p,across,outward,normal),spread=self.geometry(t)
        edge=np.clip((self.r/self.radius-.72)/.27,0,1)
        color=self.color[None]*(1-edge[:,None])+.90*self.edge[None]*edge[:,None]
        pattern=.78+.22*np.cos(self.u*12*np.pi)**2
        rim_a=np.linspace(-.5,.5,190)*spread
        rim_r=self.radius*(1+.018*np.cos(rim_a/spread*48*np.pi))
        rim=p+rim_r[:,None]*(np.sin(rim_a)[:,None]*across+np.cos(rim_a)[:,None]*outward)
        ra=self.rib_u*spread
        ribs=p+self.radius*(np.sin(ra)[:,None]*across+np.cos(ra)[:,None]*outward)
        hu,ha=np.meshgrid(self.handle_u,self.handle_a)
        handle=p+hu.reshape(-1,1)*across+.010*(np.cos(ha).reshape(-1,1)*outward+np.sin(ha).reshape(-1,1)*normal)
        trim=[]
        for scale in (.65,.81):
            trim.append(ribbon(p+(rim-p)*scale,width=.0023,color=lin("#f0c595"),alpha=.26,emit=.8,twinkle=0))
        return [dict(pos=pos,size=.0088,color=color*pattern[:,None],alpha=.24*self.grain,
                     kind="soft",normal=np.broadcast_to(normal,pos.shape),emit=.75,twinkle=0),
                dict(pos=p[None]+.15*(ribs-p[None]),pos2=ribs,size=.0021,
                     color=lin("#f1ca88"),alpha=.37,kind="line",emit=.78,twinkle=0),
                dict(pos=handle,size=.0032,color=lin("#d6b16c"),alpha=.22,kind="soft",emit=.45,twinkle=0),
                ribbon(rim,width=.0046,color=self.edge,alpha=.62,emit=.85,twinkle=0),*trim]


class GestureLight:
    """Short causal trails and sparks born at the moving fan tips.

    Light has a finite life and is deliberately separate from costume cloth.
    Every release uses an actual solved fan position at its recorded birth.
    """
    def __init__(self,fans,duration=32,seed=54,ensemble=False):
        self.fans=fans
        self.duration=duration
        self.times=np.arange(0,duration+1/60,1/60)
        keys={id(fan.body):motion_key(fan.body) for fan in fans}
        identity=dict(motion=[keys[id(f.body)] for f in fans],
                      side=[f.side for f in fans],radii=[f.radius for f in fans],
                      source=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        path=ROOT/"work/advanced-dance/trail-cache"/(key+".npy")
        if path.is_file():
            self.tracks=np.load(path,allow_pickle=False)
            if self.tracks.shape!=(len(fans),len(self.times),3) or not np.isfinite(self.tracks).all():
                raise ValueError("Invalid completed fan light track cache")
        else:
            self.tracks=np.empty((len(fans),len(self.times),3))
            for k,t in enumerate(self.times):
                for j,fan in enumerate(fans):
                    self.tracks[j,k]=fan.tip(float(t))
            path.parent.mkdir(parents=True,exist_ok=True)
            temp=path.with_name(path.stem+f".{os.getpid()}.partial.npy")
            np.save(temp,self.tracks,allow_pickle=False)
            temp.replace(path)
        self.vel=np.gradient(self.tracks,1/60,axis=1)
        rng=np.random.default_rng(seed)
        n=2400 if ensemble else 1400
        self.birth=np.sort(rng.uniform(.05,duration-.45,n))
        self.life=rng.uniform(.48,1.35,n)
        self.owner=rng.integers(0,len(fans),n)
        self.noise=rng.normal(0,.12,(n,3))
        self.size=rng.uniform(.008,.023,n)
        self.starts=np.stack([self.at(o,t) for o,t in zip(self.owner,self.birth)])
        self.speed=np.stack([self.at(o,t,self.vel) for o,t in zip(self.owner,self.birth)])
        self.colors=np.stack([fans[o].color*.6+lin("#f4cc91")*.4 for o in self.owner])

    def at(self,owner,t,data=None):
        track=self.tracks if data is None else data
        return np.array([np.interp(t,self.times,track[owner,:,j]) for j in range(3)])

    def sample(self,t):
        out=[]
        life=.26
        age=np.linspace(life,0,48)
        stamps=np.maximum(0,t-age)
        for j,fan in enumerate(self.fans):
            path=np.stack([np.interp(stamps,self.times,self.tracks[j,:,a]) for a in range(3)],1)
            path+=np.stack([np.zeros_like(age),.05*age, np.zeros_like(age)],1)
            speed=float(np.linalg.norm(self.at(j,t,self.vel)))
            gain=np.clip((speed-.25)/1.7,0,1)
            fade=(1-age/life)**1.4
            if gain>.01:
                out.append(ribbon(path,width=.008+fade*.010,color=fan.color*.6+lin("#f0c483")*.4,
                                  alpha=.28*fade*gain,emit=1.10,twinkle=0))
        age=t-self.birth
        keep=(age>0)&(age<self.life)
        a=age[keep]
        p=self.starts[keep]+(self.speed[keep]*.13+self.noise[keep])*a[:,None]
        p[:,1]+=.20*a-.33*a*a
        alpha=.46*np.sin(np.pi*a/self.life[keep])**1.1
        out.append(dict(pos=p,size=self.size[keep],color=self.colors[keep],alpha=alpha,
                        kind="spark",emit=1.3,twinkle=.15,reflect=True))
        return out
