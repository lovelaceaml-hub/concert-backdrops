"""Authored scenery and causal light for When Love Becomes Light."""
import numpy as np
from p3d.api import ribbon,lin
from p3d.master_sky import ss,sc

TAU=2*np.pi
GOLD=lin('#fbd48b')
PEARL=lin('#fff2d8')


def envelope(t,a,b,fade=.8):
    return sc(a,a+fade,t)*(1-sc(b-fade,b,t))


def stroke(p,width=.025,color=GOLD,alpha=1,emit=1.7):
    return ribbon(p,width=width,color=color,alpha=alpha,emit=emit,twinkle=0,dof=.1)


class HeartPass:
    """The same warm light travels between the performers, then wakes their world."""
    def __init__(self,source,target,a,b,color='#ffd28a'):
        self.source=source;self.target=target;self.a=a;self.b=b;self.color=lin(color)
    def point(self,t):
        u=sc(self.a,self.b,t)
        a=np.asarray(self.source(self.a));b=np.asarray(self.target(self.b))
        return a*(1-u)+b*u+np.array([0,.48*np.sin(np.pi*u),.18*np.sin(np.pi*u)])
    def sample(self,t):
        g=envelope(t,self.a-.1,self.b+.7,.22)
        if g<.001:return None
        tt=np.linspace(max(self.a,t-.60),min(t,self.b),55)
        if tt[-1]<tt[0]:return None
        p=np.array([self.point(float(q)) for q in tt]);u=np.linspace(0,1,len(p))
        head=self.point(min(t,self.b))[None]
        return [stroke(p,.035*(.1+u),self.color,.8*g*u,2),
                dict(pos=head,size=.065,color=PEARL,alpha=g,emit=3,kind='spark',twinkle=0),
                dict(pos=head,size=.40,color=self.color,alpha=.16*g,kind='soft',twinkle=0)]


class PrayerLights:
    def __init__(self,origin,a,b,n=1100,seed=33):
        r=np.random.default_rng(seed);self.o=np.array(origin);self.a=a;self.b=b
        self.ang=r.uniform(0,TAU,n);self.rad=r.uniform(2,22,n)
        self.birth=a+r.uniform(0,4,n);self.phase=r.uniform(0,TAU,n);self.speed=r.uniform(.7,1.6,n)
    def sample(self,t):
        if t<self.a or t>self.b:return None
        age=np.maximum(0,t-self.birth);g=ss(0,.8,t-self.birth)*(1-sc(self.b-1,self.b,t))
        p=self.o+np.stack([np.sin(self.ang)*self.rad+.2*np.sin(t+self.phase),
                          .4+self.speed*age+.10*age*age,np.cos(self.ang)*self.rad],1)
        return [dict(pos=p,size=.026,color=PEARL,alpha=.8*g,emit=2,kind='spark',twinkle=0),
                dict(pos=p,size=.25,color=GOLD,alpha=.055*g,kind='soft',twinkle=0)]
