"""Native dimensional wildlife and botanical performances for the ten films.

All geometry and motion is authored at absolute time. Approved models are reused
without edits; the new flight retains their existing anatomical articulation.
"""
from __future__ import annotations

import numpy as np
from p3d.api import lin, ribbon
from tools.concert_addons.geometry import ellipsoid, feather, lines, ry, rz, rx, smooth, unit, transform_batches
from tools.concert_addons.models import Dove

TAU = 2 * np.pi


def batch(points, color, size=.012, alpha=.22, **kw):
    d = dict(pos=np.asarray(points, dtype='f4'), color=lin(color), size=size,
             alpha=alpha, kind='soft', twinkle=.05)
    d.update(kw)
    return d


class BloomField:
    """Layered petals opening in a wave along the camera's garden path."""
    def __init__(self, seed=6006, count=60):
        rng = np.random.default_rng(seed)
        z = rng.uniform(-29, 4, count)
        side = rng.choice([-1, 1], count)
        x = side * rng.uniform(1.45, 5.5, count) + .4 * np.sin(z * .35)
        self.base = np.c_[x, np.zeros(count), z]
        self.h = rng.uniform(.45, 1.3, count)
        self.r = rng.uniform(.15, .36, count)
        self.phase = rng.uniform(0, TAU, count)
        self.birth = 1.5 + (-z + 1) * .30 + rng.uniform(-1.5, 1, count)
        self.color = np.array([lin(c) for c in ('#ed79bd', '#b7a0ff', '#f1bf87', '#b1ded0')])
        self.palette = rng.integers(0, 4, count)
        u, v = np.meshgrid(np.linspace(0, 1, 15), np.linspace(-1, 1, 9), indexing='ij')
        self.u, self.v = u.ravel(), v.ravel()
        self.stem_u = np.linspace(0, 1, 16)

    def sample(self, t):
        n = len(self.base)
        op = .06 + .94 * smooth(self.birth, self.birth + 3.2, t)
        wind = .055 * np.sin(.72 * t + self.phase)
        heads = self.base + np.c_[wind, self.h, .035 * np.cos(t*.6+self.phase)]
        stems = self.base[:, None, :] + self.stem_u[None, :, None] * (heads-self.base)[:, None, :]
        curves = list(stems)
        for side in (-1, 1):
            u = self.stem_u
            leaf = stems[:, 7:8, :] + np.stack([
                side * self.r[:, None]*1.15*u[None],
                self.r[:, None]*(.42*np.sin(np.pi*u)[None] + .15*u[None]),
                .18*self.r[:, None]*np.sin(np.pi*u)[None]], axis=2)
            curves.extend(leaf)
        points, colors, normals = [], [], []
        u, v = self.u, self.v
        for layer in range(2):
            for k in range(7):
                ang = self.phase + TAU * k/7 + layer*.34
                radius = self.r[:,None] * (1-.27*layer)
                opening = op[:,None]
                radial = radius * (.12 + opening * 1.8) * u[None]
                lateral = radius * .55 * np.sin(np.pi*u)[None] ** .7 * v[None]
                height = radius * (1.9*(1-opening)*u[None] + .55*np.sin(np.pi*u)[None] + .14*v[None]**2)
                q = heads[:,None,:] + np.stack([
                    radial*np.cos(ang)[:,None] - lateral*np.sin(ang)[:,None],
                    height + layer*.025,
                    radial*np.sin(ang)[:,None] + lateral*np.cos(ang)[:,None]], 2)
                points.append(q.reshape(-1,3))
                c = self.color[self.palette][:,None,:] * (.65+.35*u)[None,:,None]
                colors.append(np.broadcast_to(c, q.shape).reshape(-1,3))
                normal = np.stack([-.4*np.cos(ang), np.ones(n), -.4*np.sin(ang)],1)
                normals.append(np.broadcast_to(unit(normal)[:,None,:],q.shape).reshape(-1,3))
        pp = np.concatenate(points)
        return [lines(curves, '#81bca6', .008, .15),
                dict(pos=pp, color=np.concatenate(colors), normal=np.concatenate(normals),
                     size=.018, alpha=.19, kind='soft', rim=(.18,2.5), twinkle=.04),
                batch(heads, '#ffe6ae', .065, .48, emit=1.3)]


class ButterflyFlight:
    """Two pairs of shaped wing membranes articulate around the thorax."""
    def __init__(self, count=11, seed=33):
        rng = np.random.default_rng(seed)
        self.count=count
        self.phase = rng.uniform(0, TAU, count)
        self.scale = np.r_[1., rng.uniform(.42,.66,count-1)]
        self.offset = rng.uniform(-1,1,(count,3)) * [3.0,1.2,2.4]
        self.offset[0] = 0
        u, v = np.meshgrid(np.linspace(0,1,25),np.linspace(-1,1,15),indexing='ij')
        self.u,self.v=u.ravel(),v.ravel()
        self.colors=('#e6baff','#b8ddff','#f7d593','#eca9dc')
        self.body, self.norm = ellipsoid((0,0,0),(.018,.026,.16),180)

    @staticmethod
    def leader(t):
        return np.array([.45*np.sin(.42*t),1.25+.23*np.sin(.58*t)+.10*t,1.0-1.23*t])

    def sample(self,t):
        out=[]
        reveal=float(smooth(7,15,t))
        for j in range(self.count):
            delay=0 if j==0 else 1.2*self.phase[j]/TAU
            c=self.leader(t-delay)
            c+=self.offset[j]*(.25+.75*reveal)
            if j:
                c[0]+=.7*np.sin(t*.5+self.phase[j])*reveal
                c[1]+=.35*np.sin(t*.8+self.phase[j])
            alpha=1 if j==0 else float(smooth(3+j*.35,5+j*.35,t))
            if alpha<.001: continue
            sc=self.scale[j]
            pp=[]
            for side in (-1,1):
                flap=.78*np.sin(TAU*3.1*t+self.phase[j])
                for back in (0,1):
                    u,v=self.u,self.v
                    width=(.35 if not back else .28)*np.sin(np.pi*u)**.7
                    p=np.stack([side*(.025+(.44 if not back else .34)*u),
                                .035*np.sin(np.pi*u)*(1-v*v),
                                (.07 if not back else -.10)+width*v-.18*u*back],1)
                    a=side*(flap-.20*np.sin(TAU*3.1*t+self.phase[j]-.5)*u)
                    xx=p[:,0].copy(); yy=p[:,1].copy()
                    p[:,0]=xx*np.cos(a)-yy*np.sin(a)
                    p[:,1]=xx*np.sin(a)+yy*np.cos(a)
                    pp.append(p)
            heading=np.arctan2(.45*.42*np.cos(.42*(t-delay)), -1.23)
            rotation=ry(heading+.06*np.sin(.4*t+self.phase[j]))
            p=np.concatenate(pp)*sc@rotation.T+c
            out.append(batch(p,self.colors[j%4],.012*sc,.22*alpha,
                              rim=(.15,2),normal=np.broadcast_to([0,1,0],p.shape)))
            out.append(batch(self.body*sc@rotation.T+c,'#f7dda0',.011*sc,.42*alpha))
            antenna=[c+np.stack([side*.036*np.linspace(0,1,16),.05*np.linspace(0,1,16),
                                .14+.09*np.linspace(0,1,16)],1)*sc@rotation.T for side in (-1,1)]
            out.append(lines(antenna,'#e8cca7',.003*sc,.3*alpha))
        return out


class PollenRiver:
    def __init__(self, seed=57, count=1800):
        rng=np.random.default_rng(seed)
        self.u=rng.uniform(0,1,count); self.phase=rng.uniform(0,TAU,count)
        self.radius=rng.uniform(.1,1.2,count); self.size=rng.uniform(.012,.035,count)
    def sample(self,t):
        q=(self.u+t*.043)%1
        z=3-37*q
        x=.65*np.sin(q*9-t*.32)+self.radius*np.cos(self.phase+t*.55)
        y=.25+2.4*q+self.radius*.42*np.sin(self.phase+t*.43)
        p=np.stack([x,y,z],1)
        return batch(p,'#e7d8a5',self.size,.12+ .10*np.sin(np.pi*q)**2,
                      emit=1.2,kind='spark')


class AirborneDove(Dove):
    """Existing articulated anatomy carried by a continuous authored flight."""
    def __init__(self, index=0, scale=3.0, seed=7):
        super().__init__(scale=scale,launch=-1,land=22,seed=seed)
        self.index=index
        self.offset=np.array([0.,0.,0.]) if index==0 else np.array([
            (-1 if index%2 else 1)*(1.10+index*.28), .35*(index%3-1),.3+index*.40])
        self.phase_offset=index*.43
        # A continuous loft joins breast, neck and head. Separate ellipsoids
        # leave bright seams and make the animal read as a diagram at this scale.
        z = np.linspace(-.205, .245, 4800)
        nodes = np.array([-.205,-.18,-.13,-.05,.03,.09,.13,.165,.19,.21,.235,.245])
        cy = np.interp(z, nodes, [.142,.144,.148,.15,.17,.194,.218,.235,.248,.25,.25,.25])
        rad_x = np.interp(z, nodes, [0,.025,.05,.066,.069,.056,.041,.034,.034,.029,.017,0])
        rad_y = np.interp(z, nodes, [0,.035,.059,.078,.083,.076,.058,.04,.036,.033,.021,0])
        theta = np.arange(len(z))*np.pi*(3-np.sqrt(5))
        self.flight_body = np.stack([rad_x*np.cos(theta), cy+rad_y*np.sin(theta), z],1)
        dz = z[1]-z[0]
        normal = np.stack([rad_y*np.cos(theta), rad_x*np.sin(theta),
                           -rad_x*(np.gradient(cy,dz)*np.sin(theta)+
                                   np.gradient(rad_y,dz)*np.sin(theta)**2)-
                           rad_y*np.gradient(rad_x,dz)*np.cos(theta)**2],1)
        self.flight_normal = unit(normal)
        self.beak, self.beak_normal = ellipsoid((0,.246,.266),(.009,.008,.034),220)
        self.flight_tail=[]; self.flight_tail_normal=[]; self.flight_tail_lines=[]
        for v in np.linspace(-1,1,11):
            p,n,edges=feather([v*.025,.145,-.145], [v*.078,.125,-.355+.028*abs(v)],.012)
            self.flight_tail.append(p);self.flight_tail_normal.append(n);self.flight_tail_lines.extend(edges)

    @staticmethod
    def lead_path(t):
        u=float(smooth(0,3.2,t))
        return np.array([1.1*np.sin(.27*t), .85+1.1*u+.055*t+.22*np.sin(.52*t),
                         -1.65*t])

    def _state(self,t):
        t=float(t)
        p=self.lead_path(t)
        spread=.85+.15*float(smooth(7,15,t))
        p+=self.offset*spread
        tangent=self.lead_path(t+.02)-self.lead_path(max(0,t-.02))
        if np.linalg.norm(tangent)<1e-7: tangent=np.array([.12,.1,-1])
        yaw=np.arctan2(tangent[0],tangent[2])
        air=1.
        phase=TAU*(1.65*t+.07*np.sin(.5*t))+self.phase_offset
        glide=float(max(smooth(7.2,8.5,t)*(1-smooth(11.7,13.3,t)),smooth(15.5,17,t)))
        flap=air*(.66*np.sin(phase)*(1-.91*glide)+.08*glide)
        bank=.17*np.cos(.27*t)+.06*np.sin(.7*t+self.index)
        rotation=ry(yaw)@rz(bank)@rx(-.10+ .05*np.sin(.52*t))
        return dict(root=p,rotation=rotation,yaw=float(yaw),air=air,flap=flap,
                    phase=phase,glide=glide,landing=0.,progress=t/20)

    def _feet(self,t,state):
        return [state['root']+state['rotation']@(np.array([side*.031,.072,-.055])*self.scale)
                for side in (-1,1)]

    def sample(self,t):
        state=self._state(t)
        out=[batch(self.flight_body,'#efeada',.007,.085,normal=self.flight_normal,rim=(.15,2)),
             batch(self.beak,'#c8b288',.0045,.18,normal=self.beak_normal)]
        for side in (-1,1):
            wing,_=self._wing(side,state)
            out.extend(wing)
        out.extend([batch(np.concatenate(self.flight_tail),'#dbdedc',.0058,.055,
                          normal=np.concatenate(self.flight_tail_normal)),
                    lines(self.flight_tail_lines,'#f3e7ce',.003,.035),
                    batch(np.array([[-.031,.258,.211],[.031,.258,.211]]),'#201d1c',
                          .008,.98,paint=1.,paint_light=0.)])
        out=transform_batches(out,state['root'],state['rotation'],self.scale)
        gain=1 if not self.index else float(smooth(4+self.index*.25,6+self.index*.25,t))*.83
        for b in out: b['alpha']=np.asarray(b.get('alpha',1))*gain
        return out


class WingWake:
    """Sparse history of flight, separate from the physical feather surfaces."""
    def __init__(self,bird): self.bird=bird
    def sample(self,t):
        ages=np.linspace(0,2.6,110)
        times=np.maximum(0,t-ages)
        p=np.array([self.bird._state(s)['root'] for s in times])
        out=[]
        g=float(smooth(2,5,t))*.16
        for side in (-1,1):
            q=p+np.c_[np.full(len(p),side*.85),-.16*ages,np.zeros(len(p))]
            out.append(ribbon(q,width=.012,color=lin('#f5d494'),
                              alpha=g*(1-ages/2.6)**2,twinkle=.05))
        return out


class HaloCloud:
    def sample(self,t):
        u=np.linspace(-1,1,320)
        out=[]
        g=.14+.32*float(smooth(12,18,t))
        for j in range(5):
            z=-37-j*2.2
            p=np.stack([u*13,3.5+(1-u*u)*(2.9+j*.26)+.15*np.sin(u*6+t*.4),np.full(len(u),z)],1)
            out.append(ribbon(p,width=.024,color=lin(('#efb6c9','#e6c489','#b9cbf1')[j%3]),
                              alpha=g*(.35 if j%2 else .6),twinkle=.02))
        return out


class Jellyfish:
    """Dimensional scalloped bell, contracting rim and lagged tentacle curves."""
    def __init__(self, at=(0,4,0),scale=1,color='#d7adff',seed=1):
        self.at=np.array(at,float);self.scale=scale;self.color=color;self.seed=seed
        a,v=np.meshgrid(np.linspace(0,TAU,96,endpoint=False),np.linspace(0,1,36),indexing='ij')
        self.a,self.v=a.ravel(),v.ravel()
    def center(self,t):
        return self.at+np.array([.35*np.sin(.32*t+self.seed),.22*np.sin(.65*t+self.seed),-.18*t])
    def sample(self,t):
        a,v=self.a,self.v
        ph=1.55*t+self.seed
        contraction=.90+.10*np.sin(ph)
        radius=.64*np.sin(v*np.pi/2)*contraction
        y=.63*np.cos(v*np.pi/2)+.028*np.sin(14*a)*v**5
        p=np.stack([radius*np.cos(a),y,radius*np.sin(a)],1)
        c=self.center(t);s=self.scale
        normal=unit(np.stack([np.sin(v*np.pi/2)*np.cos(a),np.cos(v*np.pi/2),np.sin(v*np.pi/2)*np.sin(a)],1))
        cols=np.broadcast_to(lin(self.color),p.shape).copy()
        cols*= (.55+.45*v)[:,None]
        out=[dict(pos=p*s+c,color=cols,size=.019*s,alpha=.16,kind='soft',normal=normal,
                  rim=(.35,2),twinkle=.03,reflect=False)]
        curves=[]
        av=np.linspace(0,TAU,160)
        for delta in (0,.035):
            curves.append(c+s*np.stack([(.64-delta)*contraction*np.cos(av),
                .035*np.sin(14*av)+np.full(len(av),delta*.6),(.64-delta)*contraction*np.sin(av)],1))
        for theta in np.linspace(0,TAU,14,endpoint=False):
            vv=np.linspace(0,1,44)
            r=.64*np.sin(vv*np.pi/2)*contraction
            curves.append(c+s*np.stack([r*np.cos(theta),.63*np.cos(vv*np.pi/2),r*np.sin(theta)],1))
        out.append(lines(curves,self.color,.008*s,.25,reflect=False))
        tendrils=[]
        for j,theta in enumerate(np.linspace(0,TAU,18,endpoint=False)):
            u=np.linspace(0,1,65)
            length=1.8+.5*np.sin(j*2.12)
            r=.57*contraction
            xx=r*np.cos(theta)+.16*u*np.sin(5.5*u-ph+.7*j)
            zz=r*np.sin(theta)+.14*u*np.cos(6*u-ph+.55*j)
            yy=-length*u+.03*np.sin(ph-5*u)*u
            tendrils.append(c+s*np.stack([xx,yy,zz],1))
        out.append(lines(tendrils,self.color,.006*s,.19,reflect=False))
        for j in range(4):
            u=np.linspace(0,1,70); theta=j*np.pi/2
            pp=np.stack([.15*np.cos(theta)+.18*u*np.sin(u*10-ph),-1.4*u,
                         .15*np.sin(theta)+.17*u*np.cos(u*9-ph+.3)],1)*s+c
            out.append(ribbon(pp,width=.065*s,color=lin(self.color),alpha=.12,reflect=False))
        return out


class FishSchool:
    """Solid-shaped point fish with spine waves and articulated tails."""
    def __init__(self,count=92,seed=88):
        rng=np.random.default_rng(seed)
        self.phase=rng.uniform(0,TAU,count)
        self.scale=rng.uniform(.75,1.6,count)
        self.offset=rng.normal(0,1,(count,3))*[.85,.50,.8]
        self.body,self.normal=ellipsoid((0,0,0),(.055,.105,.24),1050)
        self.count=count
        u,v=np.meshgrid(np.linspace(0,1,14),np.linspace(-1,1,9),indexing='ij')
        self.tail=np.stack([np.zeros(u.size),(.025+.17*u.ravel())*v.ravel(),
                            -.20-.20*u.ravel()+.065*u.ravel()**3*(1-np.abs(v.ravel()))],1)
        fu,fv=np.meshgrid(np.linspace(0,1,16),np.linspace(0,1,9),indexing='ij')
        fu,fv=fu.ravel(),fv.ravel()
        fins=[]
        for side in (-1,1):
            fins.append(np.stack([.006*np.sin(np.pi*fu)*fv,
                                  side*(.075+.11*np.sin(np.pi*fu)*fv),-.15+.27*fu],1))
            fins.append(np.stack([side*(.038+.10*fu),-.02-.045*fu*fv,
                                  .025-.13*fu+.06*fv*fu],1))
        self.fins=np.concatenate(fins)
        self.color=np.array([lin(c) for c in ('#85e9ef','#b9afff','#a5d5ff','#efc796')])
    def sample(self,t):
        pos=[];norm=[];col=[];tail=[];eyes=[]
        for j in range(self.count):
            a=self.phase[j]+.18*t
            c=np.array([5.5*np.sin(a),3.3+.65*np.sin(2*a+.1*t)+.8*smooth(11,19,t),
                        -7-.75*t-4*smooth(9,17,t)+4.2*np.cos(a)])+self.offset[j]
            tangent=np.array([5.5*np.cos(a),1.3*np.cos(2*a+.1*t),-4.2*np.sin(a)])
            yaw=np.arctan2(tangent[0],tangent[2]);rot=ry(yaw)@rz(-.10*np.sin(a))
            p=self.body.copy(); pp=self.tail.copy()
            phase=TAU*(2.1*t)+j*.74
            p[:,0]+=.023*np.sin(phase-11*p[:,2])*(.25+np.clip(-p[:,2],0,1)*3)
            pp[:,0]=.06*np.sin(phase-11*pp[:,2])
            sc=self.scale[j]
            pos.append(p*sc@rot.T+c);norm.append(self.normal@rot.T)
            tail.append(pp*sc@rot.T+c)
            fp=self.fins.copy()
            fp[:,0]+=.012*np.sin(phase-10*fp[:,2])*np.abs(fp[:,1])/.15
            tail.append(fp*sc@rot.T+c)
            col.append(np.broadcast_to(self.color[j%4],p.shape))
            eyes.append(np.array([[.047,.026,.165],[-.047,.026,.165]])*sc@rot.T+c)
        return [dict(pos=np.concatenate(pos),normal=np.concatenate(norm),color=np.concatenate(col),
                     size=.010,alpha=.19,kind='soft',rim=(.20,2),twinkle=.04,reflect=False),
                batch(np.concatenate(tail),'#9be9ee',.010,.13,reflect=False),
                batch(np.concatenate(eyes),'#ffe5b5',.024,.58,reflect=False)]


class CoralGarden:
    static=True
    def __init__(self,seed=81):
        rng=np.random.default_rng(seed);curves=[];points=[];normals=[];colors=[];tips=[]
        palette=[lin(c) for c in ('#73aeb5','#a995bc','#84bcba','#b8ad8e')]
        for j in range(26):
            base=np.array([rng.choice([-1,1])*rng.uniform(3,10),.05,rng.uniform(-34,7)])
            height=rng.uniform(.7,2.4)
            color=palette[j%len(palette)]
            def grow(start,direction,length,depth):
                u=np.linspace(0,1,22)
                bend=rng.normal(0,1,3)*[.18,.04,.18]
                p=start+direction[None]*length*u[:,None]+length*bend[None]*u[:,None]**2
                curves.append(p)
                right=unit(np.cross(direction,[0,0,1]))
                other=unit(np.cross(direction,right))
                a=np.arange(9)*TAU/9
                radial=right[None]*np.cos(a)[:,None]+other[None]*np.sin(a)[:,None]
                radius=(.010+.008*depth)*height*(1-.40*u)
                tube=p[:,None]+radius[:,None,None]*radial[None]
                points.append(tube.reshape(-1,3))
                normals.append(np.broadcast_to(radial[None],tube.shape).reshape(-1,3))
                colors.append(np.broadcast_to(color,tube.shape).reshape(-1,3))
                if depth:
                    for side in (-1,1):
                        d=unit(direction+side*right*rng.uniform(.35,.75)+other*rng.uniform(-.35,.35))
                        grow(p[-1],d,length*.60,depth-1)
                else:
                    tips.append(p[-1])
            grow(base,unit(rng.normal(0,1,3)*[.20,0,.20]+[0,1,0]),height*.42,3)
        self.curves=curves;self.points=np.concatenate(points);self.normals=np.concatenate(normals)
        self.colors=np.concatenate(colors);self.tips=np.array(tips)
    def sample(self,t):
        return [dict(pos=self.points,color=self.colors,normal=self.normals,size=.014,alpha=.14,
                     kind='soft',rim=(.12,2),twinkle=.02,reflect=False),
                lines(self.curves,'#8bbdc6',.009,.09,reflect=False),
                batch(self.tips,'#c1d4cc',.033,.18,reflect=False)]


class OceanShafts:
    """Volumetric glimmer and shafts descending from a high surface."""
    def __init__(self,seed=881):
        rng=np.random.default_rng(seed)
        self.p=rng.uniform([-12,.1,-36],[12,15,10],(3400,3))
        self.phase=rng.uniform(0,TAU,len(self.p));self.size=rng.uniform(.012,.040,len(self.p))
    def sample(self,t):
        p=self.p.copy();p[:,1]+=.09*np.sin(t*.6+self.phase);p[:,0]+=.15*np.sin(t*.27+self.phase)
        out=[batch(p,'#95d7e8',self.size,.10,kind='spark',reflect=False)]
        for i in range(7):
            u=np.linspace(0,1,80)
            origin=np.array([-8+i*2.8,13,-16+i*.8])
            q=origin+np.stack([u*2.2+.18*np.sin(t*.22+i),-12*u,-3*u],1)
            out.append(ribbon(q,width=.12,color=lin('#7fb5c5'),
                              alpha=.025*np.sin(np.pi*u)**.5,reflect=False))
        return out
