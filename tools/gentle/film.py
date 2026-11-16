"""A World Made Gentle: a new 62-second garden of light, built on the engine.

The previous Astra cast supplies reusable, reviewed human performances only.
The camera, scenery, chronology, light choreography and score are independent.
This module is loaded by tools/gentle/render.py without changing engine/songs.
"""
import numpy as np

from songs.master_astra import *  # noqa: F401,F403
from songs import master_astra as CAST
from p3d import brand as BR, words as PW
from p3d import master_sky as SKY, master_brand as MB
from p3d.api import CameraState, lin, ribbon
from p3d.camera import Move, Rig

TOTAL = 62.0
NFRAMES = int(TOTAL*FPS)
MUSIC_END = 61.8
SONG_END = TOTAL
TEXT_SHADOW = 0.0
BOTTOM_CALM = 0.0
STARTS = np.arange(9)*4.0+8.0
STAGE = np.array([2.15, 0.06, 0.0])
COLORS = [PW.COLORS[k] for k in PW.LABELS]


def smooth(a,b,t):
    u = np.clip((np.asarray(t)-a)/max(b-a,1e-9),0,1)
    return u*u*u*(u*(u*6-15)+10)


def window(a,b,t,fade=.65):
    return smooth(a,a+fade,t)*(1-smooth(b-fade,b,t))


class GentleCamera(Move):
    def __init__(self):
        super().__init__(0.0,62.0)

    def pose(self,t):
        rise = float(smooth(43.8,48.0,t))
        settle = float(smooth(53.0,60.5,t))
        p = np.array([.24*np.sin(t*.095)*(1-settle), 2.65+1.05*rise,
                      8.3+2.0*rise-.25*settle])
        q = np.array([.04*np.sin(t*.1),2.2+.65*rise,-.6])
        return p,q


CAMERA = Rig([GentleCamera()],fov=45,handheld=0.0,aperture=0.015,shutter=.65)

SPECS = [dict(expr=label,t_in=float(t),t_read0=float(t+.42),t_read1=float(t+3.60),
              t_out=float(t+3.98),ride=(.5,.66,8.0),
              em=PW.em_for(CAMERA,float(t+2),8.0,87),face='screen',
              arrive='reveal',edge='out',soft=.20,leave='rise',speed=.35,
              color=PW.COLORS[label],paint=True,tint=1.0,bright=.65,halo=.12,sparkle=.02,
              pill=True,sharp=1.0,n='auto',n_label=5000)
         for label,t in zip(PW.LABELS,STARTS)]
WORDS = PW.Words(SPECS,camera=CAMERA)


class Clear:
    """Protect the actual reading planes and the lower-left signature."""
    wants_camera = True

    def __init__(self,inner):
        self.inner=inner

    def sample(self,t,cam):
        got = self.inner.sample(t,cam) if getattr(self.inner,'wants_camera',False) else self.inner.sample(t)
        if got is None:return None
        batches = got if isinstance(got,list) else [got]
        out=[]
        for original in batches:
            b=dict(original)
            if 'pos' not in b:
                out.append(b)
                continue
            xy,depth=cam.project(np.asarray(b['pos']))
            x,y=xy[:,0],xy[:,1]
            keep=np.ones(len(x))
            if 7.4<t<54.7:
                keep *= 1-window(-.12,.64,x,.12)*window(-.12,.315,y,.12)
            if t<8.0:
                keep *= 1-window(.15,.85,x,.03)*window(.39,.99,y,.03)*(1-smooth(7,8,t))
            for s in SPECS:
                strength=window(s['t_in'],s['t_out'],t,.25)
                if strength>0:
                    keep *= 1-strength*window(.07,.93,x,.025)*window(.51,.80,y,.025)
            b['alpha']=np.asarray(b.get('alpha',1))*keep
            out.append(b)
        return out


class Performance:
    """Re-stage a whole reviewed performance; no changes to shared acting files."""
    def __init__(self,people,origin,source_times,times,yaw=0,opening=False):
        self.people,self.origin=people,np.asarray(origin)
        self.source_times,self.times=source_times,times
        a=np.radians(yaw)
        self.rotation=np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
        self.opening=opening

    def sample(self,t):
        a,b=self.times
        if not a<=t<=b:return None
        u=(t-a)/(b-a)
        source=self.source_times[0]+u*(self.source_times[1]-self.source_times[0])
        alpha=float(window(a,b,t,.45)) if not self.opening else float(1-smooth(6.8,7.7,t))
        center=np.array([1.45,.85,-.8]) if self.opening else STAGE
        scale=1.0 if self.opening else 1.15
        out=[]
        for person in self.people:
            got=person.sample(float(source))
            if got is None:continue
            for original in got if isinstance(got,list) else [got]:
                batch=dict(original)
                for k in ('pos','pos2'):
                    if k in batch:batch[k]=scale*((np.asarray(batch[k])-self.origin)@self.rotation.T)+center
                for k in ('normal','vel'):
                    if k in batch:batch[k]=np.asarray(batch[k])@self.rotation.T
                batch['alpha']=np.asarray(batch.get('alpha',1))*alpha
                if 'size' in batch:batch['size']=np.asarray(batch['size'])*scale
                if batch.get('kind')=='spark':batch['alpha']*=.18
                batch['twinkle']=min(float(batch.get('twinkle',0)),.12)
                out.append(batch)
        return out


class Garden:
    """Nine luminous petals awaken, then carry their colours toward the world."""
    def __init__(self):
        rng=np.random.default_rng(408)
        self.u=np.linspace(0,2*np.pi,420)
        self.jitter=rng.normal(0,.035,(9,420,3))
        self.seed=rng.random((9,420))

    def sample(self,t):
        if t>54.4:return None
        out=[]
        lift=float(smooth(43.6,47.5,t))
        gone=float(1-smooth(51.6,54.4,t))
        for k,(start,color) in enumerate(zip(STARTS,COLORS)):
            lit=.035+.42*float(smooth(start+.8,start+2.2,t))
            theta=2*np.pi*k/9+.12*np.sin(t*.06)
            u=self.u
            radial=5.5*np.sin(u*.5)
            lateral=.85*np.sin(u)
            px=radial*np.cos(theta)+lateral*np.sin(theta)
            py=radial*np.sin(theta)-lateral*np.cos(theta)
            p=np.stack([1.3*px,3.8+py,-8+1.4*np.sin(u+theta)],axis=1)
            p+=self.jitter[k]
            angle=u+theta+.38*(t-43.6)
            r=3.4+.25*np.sin(2*u+theta)
            target=np.stack([r*np.cos(angle),3+.65*np.sin(2*angle)+.8*np.sin(u),r*np.sin(angle)],axis=1)
            p=p*(1-lift)+target*lift
            col=lin(color)*.72+lin('#ffc66d')*.28
            out.append(dict(pos=p,size=.025,color=col,alpha=lit*gone,emit=1.1,
                            kind='disc',dof=0.0,fog=.04,seed=self.seed[k],twinkle=0))
            out.append(ribbon(p[::3],width=.045,color=col,alpha=.20*lit*gone,emit=.7))
            out.append(dict(pos=p[::7],size=.32,color=col,alpha=.016*lit*gone,kind='soft',dof=0,fog=0))
        return out


class LightWays:
    """Broad, flowing paths below the garden, with deterministic drifting pollen."""
    def __init__(self):
        r=np.random.default_rng(412)
        self.u=np.linspace(-1,1,600)
        self.p=r.uniform([-12,.2,-22],[12,7,-3],(4500,3))
        self.phase=r.uniform(0,2*np.pi,4500)
        self.size=r.uniform(.012,.035,4500)

    def sample(self,t):
        fade=float(1-smooth(52,54.3,t))
        if fade<=0:return None
        out=[]
        for j in range(4):
            x=self.u*18
            z=-8-3*j+2.5*np.sin(self.u*2.3+j*.8+t*.025)
            p=np.stack([x,np.full(len(x),.04+.01*j),z],1)
            glow=.12+.10*(.5+.5*np.sin(self.u*12-t*.8+j))
            out.append(ribbon(p,width=.06+.03*j,color=lin('#ffc56e'),alpha=glow*fade,emit=.8))
        p=self.p.copy()
        p[:,0]+=.28*np.sin(t*.20+self.phase)
        p[:,1]+=.14*np.sin(t*.24+self.phase*1.3)
        out.append(dict(pos=p,size=self.size,color=lin('#ffe0a0'),alpha=.22*fade,
                        kind='disc',dof=.3,fog=.1,twinkle=0))
        return out


class KindnessHearts:
    def __init__(self):
        self.effects=[BR.HeartDrift(STAGE+np.array([0,1.35,0]),float(t+1.5),float(t+3.4),
                                  color=color,rate=2.1,life=2.1,rise=.35,spread=.25,
                                  size=(.045,.085)) for t,color in zip(STARTS,COLORS)]

    def sample(self,t):
        out=[]
        for effect in self.effects:
            b=effect.sample(t)
            if b is not None:out.extend(b if isinstance(b,list) else [b])
        return out


class OpeningDrop:
    def __init__(self):
        self.u=np.linspace(0,2*np.pi,600)

    def sample(self,t):
        if t>10:return None
        release=float(smooth(5.5,7.4,t))
        p=np.array([1.45,.98*(1-release)+.08,-.65])
        if t<7.5:
            return [dict(pos=p[None],size=.12,color=lin('#fff1c4'),alpha=.8,kind='disc',emit=2),
                    dict(pos=p[None],size=.55,color=lin('#ffca62'),alpha=.2,kind='soft')]
        r=.15+3.0*(t-7.5)
        a=float(1-smooth(8.0,10,t))
        points=np.stack([1.45+r*np.sin(self.u),np.full(600,.04),-.65+r*np.cos(self.u)],1)
        return ribbon(points,width=.06,color=lin('#ffd58d'),alpha=a*.45)


FINALE=BR.Finale(pos=(0,3.0,0),radius=2.35,camera=CAMERA,look='night',
                 t_world=46.8,spin=3.0,front=-115.14-3*47.6,shrink=.48,
                 hearts=dict(t0=47.7,t1=51.7,n=27),t_settle=(51.4,53.2),
                 t_logo=(52.2,54.0),bloom=dict(t=53.7,strength=.035,glow=.22),look_after='gentle_end',blend=1.8,
                 end=dict(t=(54.0,54.6),ride=(.5,.862,14),frac=.157),
                 logo=dict(reflect=False),n=45000)


def setup(scene):
    cast=CAST._cast()
    scenes=[('greeting',CAST.P1,(8.3,12.7),(8,12)),
            ('gratitude',CAST.P1b,(11.8,15.9),(12,16)),
            ('embrace',CAST.P2,(15.0,22.2),(16,24)),
            ('concession',CAST.P3+np.array([-1,0,2]),(22.3,25.8),(24,28)),
            ('respect',CAST.P3b,(25.5,29.0),(28,32)),
            ('encouragement',CAST.P4,(29.5,33.8),(32,36)),
            ('consideration',CAST.P5,(35.0,39.2),(36,40)),
            ('compliment',CAST.P5b,(38.7,42.8),(40,44))]
    for name,origin,source,times in scenes:
        old_cam=CAST.CAMERA.state(sum(source)/2)
        delta=np.asarray(old_cam.pos)-origin
        yaw=-np.degrees(np.arctan2(delta[0],delta[2]))
        scene.add('gentle '+name,Clear(Performance(cast[name],origin,source,times,yaw)),reflect=True)
    scene.add('opening hands',Clear(Performance(cast['hands0'],CAST.H0,(.8,7.6),(0,7.8),opening=True)),reflect=False)
    scene.add('the first kindness',Clear(OpeningDrop()),reflect=True)
    scene.add('nine petal cathedral',Clear(Garden()),reflect=True)
    scene.add('paths of light',Clear(LightWays()),reflect=True)
    scene.add('hearts from the acts',Clear(KindnessHearts()),reflect=False)
    clouds=[]
    for j in range(18):
        theta=2*np.pi*j/18
        clouds.append(dict(center=(17*np.cos(theta),-.4+1.7*np.sin(theta*3),-10+10*np.sin(theta)),
                           width=5+(j%4),height=2+(j%3)*.5,n=160,bright=.8))
    scene.add('rose cloud garden',Clear(SKY.Billows(clouds,seed=421,alpha=.07,body=.18,
        top='#ffe1a0',warm='#ffbf78',rose='#ed8e9b',lilac='#a98ac0',drift=(.02,0,0),
        gain=lambda t:1-float(smooth(52.5,54.4,t)))),reflect=True)
    for k,(label,t) in enumerate(zip(PW.LABELS,STARTS)):
        scene.add('garden symbol '+label,Clear(BR.Traced(label,pos=(-3.8,1.8,-2),size=.9,
            camera=CAMERA,t0=float(t+.5),dur=1.0,hold=1.7,out=.7,intensity=.24,
            color=PW.COLORS[label],n=900)),reflect=False)
    FINALE.add_to(scene)
    scene.add('nine colours bless the world',MB.SymbolSwirl((0,3,0),2.35,PW.LABELS,COLORS,
              47.1,52.1,CAMERA,scale=FINALE.scale,size=.34,orbit=(1.9,1.65),
              turns=.35,n=550,life=1.8,bright=.45,glow_world=.35),reflect=False)
    place=lambda t: (np.array([0,3,0]),np.array([1,0,0]),np.array([0,1,0]))
    scene.add('closing chord glow',MB.FinalGlow(place,57.5,width=11,height=7,ring=.012,glint=.02),reflect=False)
    # Only the active word owns a paint fill; the engine has two fill slots.
    for word in WORDS:
        mask=word.mask()
        mask.strength=lambda t,a=word.t_in,b=word.t_out: float(a<=t<=b)
        scene.add('word '+word.name,word,reflect=False,depth_of_field=True,mask=mask)
        scene.add('word '+word.name+' light',word.lights,reflect=False)
    WORDS.check(CAMERA,min_read=3.0)


WORLD=dict(look=[(0,'gentle'),(43.8,'lift',2.0)],
           looks=dict(gentle=dict(base='predawn',sky_top='#69486f',sky_mid='#a16b8b',
                      sky_hor='#edb68d',water='#5e4b70',haze_color='#e7ac91',
                      sun_color='#ffe4b1',sun_el=8,sun_az=228,sun_int=.55),
                      lift=dict(base='dawn',sky_top='#a87592',sky_mid='#d4a5ae',
                      sky_hor='#ffe0ab',water='#a38eae',sun_int=.5,sun_el=16,sun_az=228),
                      gentle_end=dict(base='dawn',sky_top='#eed8ce',sky_mid='#ffe8ce',
                      sky_hor='#fff1d6',water='#ddc8ce',haze_color='#ffe5cc',
                      sun_int=.18,sun_el=16,sun_az=228)),
           stars=0,milky=0,clouds=.18,cloud_speed=.06,hills=0,mirror=.32,ripple=.25,
           haze=.15,mist=.10,lanterns=0,floats=0,dust=0,bokeh=0,
           dust_color='#ffdda4',dust_color2='#f6af91',keep_hue=.75,
           react=dict(beat=.09,level=.08),
           shafts=[dict(base=(-4,-9),radius=1.4,top=25,color='#ffce8b',strength=.16),
                   dict(base=(7,-12),radius=1.2,top=28,color='#ffddad',strength=.12)])
P3D=dict(camera=CAMERA,world=FINALE.world(WORLD),setup=setup,
         bursts=FINALE.bursts(),motion_blur=.65,motion_samples=1)
TITLES=dict(opening=dict(t_end=8,dissolve=1,y=.30,palette='night'),
            signature=dict(windows=[(7.0,54.8,'bl','night')],fade=.4,protect=dict(keep=0)),
            end_card=dict(t_in=54.5,fade=.5,scale=1.0,backdrop=True,veil=.65,ambient_motes=True))
