"""Choreography-led concert light, depth and restrained musical accents."""
from __future__ import annotations

import numpy as np
from p3d.api import lin,ribbon


class LightArchitecture:
    def __init__(self,score,wide=False):
        self.score,self.wide=score,wide
        self.width=6.4 if wide else 3.8
        rng=np.random.default_rng(20261121)
        self.fall=rng.uniform(0,1,(1900,3))
        self.spark_size=rng.uniform(.008,.022,1900)

    def sample(self,t):
        b=self.score.beat(t)
        phrase=min(int(b//8),7)
        accent=np.exp(-((b%1)/.17)**2)
        wave=.5+.5*np.sin(t*.45)
        palette=("#bc8ad5","#8caedf","#edb982")
        out=[]
        u=np.linspace(0,np.pi,250)
        for j in range(7):
            w=self.width+j*.32
            y=.12+(4.2+j*.28)*np.sin(u)**.91
            z=np.full(len(u),-4.8-j*.85)+.28*np.sin(u*2)
            p=np.stack([w*np.cos(u),y,z],1)
            out.append(ribbon(p,width=.006 if j%3 else .011,color=lin(palette[j%3]),
                alpha=.22+.07*accent,emit=.9,twinkle=0))
            phase=(b*.08+j*.11)%1
            k=round(phase*(len(u)-1))
            out.append(dict(pos=p[max(0,k-3):k+3],size=.022,color=lin(palette[j%3]),
                alpha=.48,emit=1.4,kind="spark",twinkle=.12))
        # Thin stage beams sweep in the background. They never cross the lens
        # as full-screen flashes or cover the central facial silhouette.
        for side in (-1,1):
            for j in range(4):
                base=np.array([side*(self.width+.55+j*.32),.07,-2.4-j*.7])
                tip=np.array([side*(self.width*.8+j*.62+.4*np.sin(t*.48+j)),5.8,-7.0-j*.9])
                out.append(dict(pos=base[None],pos2=tip[None],size=.016,
                    color=lin(palette[(j+phrase)%3]),alpha=.08+.025*accent,kind="line",emit=1.0,twinkle=0))
        # A traveling canopy holds detail behind the bodies and leaves their
        # immediate hands and feet clear for the movement to read.
        q=self.fall.copy()
        p=np.stack([(q[:,0]-.5)*(self.width*2.9),
                    2.8+4.1*((q[:,1]-t*.036)%1),-4.0-q[:,2]*8],1)
        p[:,0]+=.30*np.sin(q[:,2]*11+t*.5)
        final=np.clip((b-55)/9,0,1)
        out.append(dict(pos=p,size=self.spark_size,color=lin("#dcc39a"),
            alpha=.12+.13*final,kind="spark",emit=1.1,twinkle=.35))
        # Floor light supports the count without hiding planted contacts.
        a=np.linspace(0,2*np.pi,360)
        for j in range(3):
            radius=(4.8 if self.wide else 2.0)+j*.12
            p=np.stack([radius*np.cos(a),np.full(len(a),.009),radius*.72*np.sin(a)-.2],1)
            out.append(ribbon(p,width=.005,color=lin(palette[j]),alpha=.19+.04*accent,emit=.85,twinkle=0))
        return out


class LandingLight:
    def __init__(self,bodies):
        self.events=[]
        for body in bodies:
            score=body.actor.advanced_score
            for step in score.steps:
                p=body.where(step.end,"ankle."+step.side).copy()
                p[1]=.009
                self.events.append((step.end,p,step.phrase))

    def sample(self,t):
        out=[]
        a=np.linspace(0,2*np.pi,70)
        for birth,center,phrase in self.events:
            age=t-birth
            if not 0<=age<.45:
                continue
            r=.07+.24*age
            p=center+np.stack([r*np.cos(a),np.zeros(len(a)),r*np.sin(a)],1)
            out.append(ribbon(p,width=.0035,color=lin("#ddc3a0"),
                alpha=.16*(1-age/.45)**2,emit=.8,twinkle=0))
        return out
