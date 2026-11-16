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


class Arcade:
    """Nested luminous vaults with depth, small star joints, and a reflecting aisle."""
    def __init__(self,origin,a,b,count=5,span=5,height=7,spacing=4,seed=17):
        self.o=np.array(origin);self.a=a;self.b=b
        self.paths=[]
        theta=np.linspace(0,np.pi,100)
        for j in range(count):
            for shift in [-.075,.075]:
                x=(span+shift)*np.cos(theta)
                y=height*np.sin(theta)**.72
                p=self.o+np.stack([x,y,np.full(len(x),-j*spacing-3)],1)
                self.paths.append(p)
        self.seed=seed
    def sample(self,t):
        g=envelope(t,self.a,self.b)
        if g<.001:return None
        out=[]
        for j,p in enumerate(self.paths):
            u=np.linspace(0,1,len(p))
            wave=.62+.38*np.exp(-((u-(.5+.25*np.sin(.55*t+j*.3)))/.14)**2)
            out.append(stroke(p,.025,GOLD,g*.68*wave,1.7))
            out.append(dict(pos=p[::5],size=.18,color=GOLD,alpha=.045*g,kind='soft',twinkle=0))
        joints=np.concatenate([p[::12] for p in self.paths])
        out.append(dict(pos=joints,size=.025,color=PEARL,alpha=.65*g,emit=1.8,kind='spark',twinkle=0))
        return out


class Lotus:
    """A large pearlescent flower grows from an act of kindness."""
    def __init__(self,origin,a,b,radius=3.7,seed=31):
        self.o=np.array(origin);self.a=a;self.b=b;self.radius=radius
        u=np.linspace(0,1,80)
        self.paths=[]
        for ring in range(2):
            for k in range(10):
                az=TAU*(k+.5*ring)/10
                radial=np.sin(np.pi*u)*radius*(1-.28*ring)
                y=.12+(.5+.45*ring)*np.sin(np.pi*u)**1.8
                azimuth=az+.20*np.sin(TAU*u)
                self.paths.append(np.stack([radial*np.sin(azimuth),y,radial*np.cos(azimuth)],1))
    def sample(self,t):
        g=envelope(t,self.a,self.b,.9)
        if g<.001:return None
        growth=sc(self.a,self.a+1.7,t)
        out=[]
        for j,p in enumerate(self.paths):
            pp=self.o+p*np.array([growth,.4+.6*growth,growth])
            out.append(stroke(pp,.012,GOLD*.75+PEARL*.25,g*.18,1.1))
            out.append(dict(pos=pp[::3],size=.15,color=GOLD,alpha=.025*g,kind='soft',twinkle=0))
        return out


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


class LivingCanopy:
    """Branches draw outward and unfurl little leaves above a reflecting garden."""
    def __init__(self,origin,a,b,seed=44):
        self.o=np.array(origin);self.a=a;self.b=b
        r=np.random.default_rng(seed);self.paths=[];self.leaves=[]
        for k in range(9):
            u=np.linspace(0,1,70);az=k*2.39996
            radius=4*u**1.7
            p=self.o+np.stack([radius*np.sin(az+.45*u),.3+3.2*u-.6*u*u,radius*np.cos(az+.45*u)],1)
            self.paths.append(p)
            for j in range(18,65,4):
                theta=np.linspace(0,TAU,24)
                d=np.array([np.cos(az),.45,-np.sin(az)])
                leaf=p[j]+np.sin(theta)[:,None]*d*.12+np.cos(theta)[:,None]*np.array([0,.22,0])
                self.leaves.append(leaf)
    def sample(self,t):
        g=envelope(t,self.a,self.b)
        if g<.001:return None
        out=[];grow=sc(self.a,self.a+1.5,t)
        for p in self.paths:
            out.append(stroke(self.o+(p-self.o)*grow,.016,GOLD,.22*g,1.25))
        gg=g*sc(self.a+.6,self.a+2.1,t)
        for p in self.leaves:
            out.append(stroke(p,.010,GOLD*.6+PEARL*.4,.16*gg,1.15))
        return out


class Constellation:
    """Nine broad silk currents rise with the camera, without shader flicker."""
    def __init__(self,origin,camera_y,colors):
        self.o=np.array(origin);self.y=camera_y;self.colors=[lin(c) for c in colors]
    def sample(self,t):
        g=envelope(t,44.25,49.45,.65)
        if g<.001:return None
        out=[]
        for k in range(9):
            tt=np.linspace(max(44.2,t-1.25),t,95)
            u=tt-44.2;az=TAU*k/9+.38*u
            rad=8+.8*u
            yy=np.array([self.y(float(z)) for z in tt])+7+2*k/9
            p=self.o+np.stack([np.sin(az)*rad,yy,np.cos(az)*rad],1)
            taper=np.linspace(0,1,len(p))
            out.append(stroke(p,.12*taper+.01,self.colors[k],g*.65*taper,2.1))
            out.append(dict(pos=p[::3],size=.25,color=self.colors[k],alpha=.035*g*taper[::3],kind='soft',twinkle=0))
        return out
