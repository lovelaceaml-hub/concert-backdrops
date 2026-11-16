"""The Light That Reaches You: a journey from a tender act to a radiant world.

Independent staging, camera, atmosphere and light choreography. Shared cast
performances and renderer APIs are read only. All motion is a function of time.
"""
import numpy as np
from songs.master_astra import *  # noqa: F401,F403
from songs import master_astra as CAST
from p3d import brand as BR, words as PW, master_sky as SKY, master_brand as MB
from p3d.api import lin, ribbon
from p3d.camera import Move, Rig
from tools.radiance.actors import standing_encouragement, standing_consideration

TOTAL = SONG_END = 62.0
NFRAMES = int(TOTAL*FPS)
MUSIC_END = 61.8
TEXT_SHADOW = BOTTOM_CALM = 0.0
STARTS = 8.6 + np.arange(9)*3.9
CENTERS = np.array([[3*np.sin(k*.65),0,-6-6*k] for k in range(9)])
COLORS = [PW.COLORS[k] for k in PW.LABELS]


def smooth(a,b,t):
    u = np.clip((np.asarray(t)-a)/(b-a),0,1)
    return u*u*u*(u*(u*6-15)+10)


def window(a,b,t,fade=.5):
    return smooth(a,a+fade,t)*(1-smooth(b-fade,b,t))


def aim(p,c,where=(.65,.63)):
    return CAST._aim(np.asarray(p),np.asarray(c),*where,fov=44)


def camera_path():
    keys=[(0,(0,9.8,12),(0,11,-10)),(6.9,(.5,9.4,10),(0,10.5,-10))]
    for k,(a,c) in enumerate(zip(STARTS,CENTERS)):
        for dt,side,dist in [(.25,-1.2,7.0),(2.65,1.1,6.5)]:
            p=c+np.array([side,1.9,dist])
            keys.append((float(a+dt),p,aim(p,c+[0,1.4,0])))
    keys.extend([(44.7,(-.5,3.1,-47),(0,3,-64)),
                 (47.0,(4,10,-48),(0,12,-68)),
                 (49.7,(7,16,-49),(0,12,-68)),
                 (52.0,(3,14,-53),(0,12,-68)),
                 (55.0,(0,13.3,-52),(0,12,-68)),
                 (62.0,(0,13.1,-52.4),(0,12,-68))])
    return CAST._pchip(keys)


class Journey(Move):
    def __init__(self):
        super().__init__(0,62)
        self.path=camera_path()

    def pose(self,t):
        return self.path(t)


CAMERA=Rig([Journey()],fov=44,aperture=.035,handheld=0,shutter=.65)
SPECS=[dict(expr=label,t_in=float(a+.15),t_read0=float(a+.5),
            t_read1=float(a+3.10),t_out=float(a+3.50),
            ride=(.5,.66,8),em=PW.em_for(CAMERA,float(a+1.8),8,87),
            face='screen',arrive='reveal',edge='out',soft=.18,leave='fade',
            color=color,paint=False,tint=.30,bright=.85,halo=.25,sparkle=.025,
            pill=True,sharp=1,n='auto',n_label=4000)
       for label,a,color in zip(PW.LABELS,STARTS,COLORS)]
WORDS=PW.Words(SPECS,camera=CAMERA)


class KeepWords:
    """Keep atmospheric foreground points out of actual reading regions."""
    wants_camera=True

    def __init__(self,inner):
        self.inner=inner

    def sample(self,t,cam):
        got=self.inner.sample(t,cam) if getattr(self.inner,'wants_camera',False) else self.inner.sample(t)
        if got is None:return None
        out=[]
        for original in got if isinstance(got,list) else [got]:
            b=dict(original)
            for position,alpha in [('pos','alpha'),('pos2','alpha2')]:
                if position not in b:continue
                xy,_=cam.project(np.asarray(b[position]))
                x,y=xy.T
                keep=np.ones(len(x))
                if t<8.1:
                    keep*=1-.9*(1-smooth(7,8.1,t))*window(.12,.88,x,.1)*window(.4,.98,y,.08)
                if 7<t<54.8:
                    keep*=1-window(-.1,.55,x,.06)*window(-.1,.24,y,.04)
                for s in SPECS:
                    strength=window(s['t_in'],s['t_out'],t,.3)
                    if strength>0:
                        keep*=1-strength*window(.1,.9,x,.04)*window(.53,.79,y,.04)
                b[alpha]=np.asarray(b.get(alpha,b.get('alpha',1)))*keep
            out.append(b)
        return out


class Performance:
    def __init__(self,people,origin,source,times,center,yaw=0,scale=1.35):
        self.people,self.origin,self.source,self.times=people,np.asarray(origin),source,times
        self.center,self.scale=np.asarray(center),scale
        a=np.radians(yaw)
        self.rotation=np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])

    def sample(self,t):
        a,b=self.times
        if not a<=t<=b:return None
        u=(t-a)/(b-a)
        source=self.source[0]+u*(self.source[1]-self.source[0])
        fade=float(window(a,b,t,.35))
        if a==0:fade=float(1-smooth(b-.7,b,t))
        out=[]
        for person in self.people:
            got=person.sample(float(source))
            if got is None:continue
            for original in got if isinstance(got,list) else [got]:
                d=dict(original)
                for name in ('pos','pos2'):
                    if name in d:d[name]=self.scale*((np.asarray(d[name])-self.origin)@self.rotation.T)+self.center
                for name in ('normal','vel'):
                    if name in d:d[name]=np.asarray(d[name])@self.rotation.T
                d['alpha']=np.asarray(d.get('alpha',1))*fade
                if 'size' in d:d['size']=np.asarray(d['size'])*self.scale
                if d.get('kind')=='spark':d['alpha']*=.28
                d['twinkle']=min(float(d.get('twinkle',0)),.14)
                out.append(d)
        return out


class River:
    """Thousands of fine gold filaments curl into a rising vault of light."""
    def __init__(self):
        r=np.random.default_rng(711)
        self.u=np.linspace(0,1,900)
        self.p=r.uniform([-22,.2,-110],[22,15,8],(15000,3))
        self.seed=r.random(15000)
        self.size=r.uniform(.012,.045,15000)

    def sample(self,t):
        fade=float(1-smooth(51,54.4,t))
        if fade<=0:return None
        out=[]
        z=10-120*self.u
        for k in range(19):
            phase=k*.28
            x=-3*np.sin((z+6)*(.65/6))+(.9+.16*k)*np.cos(self.u*11+phase+t*.08)
            y=.06+.018*k+(.12+.08*k)*np.sin(self.u*8+phase+t*.12)**2
            p=np.stack([x,y,z],1)
            a=(.12+.10*np.sin(self.u*30-t*.7+k)**2)*fade
            out.append(ribbon(p,width=.012+.002*(k%4),color=lin('#ffd486'),alpha=a,emit=1.3))
        # Broad arcs form a gold cathedral; their fine contour stays visible.
        lift=float(smooth(42,48.5,t))
        for j in range(7):
            u=np.linspace(0,np.pi,380)
            radius=7.5+j*.7
            p=np.stack([radius*np.cos(u)+.5*np.sin(u*3+t*.1),
                        1.8+radius*np.sin(u)*(1+.8*lift),
                        np.full(len(u),-10-j*8)+1.7*np.sin(u*2+t*.12)],1)
            out.append(ribbon(p,width=.035,color=lin('#ffd188'),alpha=.22*fade,emit=1.1))
            out.append(dict(pos=p[::3],size=.14,color=lin('#ffa96c'),alpha=.06*fade,kind='soft',dof=0))
        p=self.p.copy()
        p[:,0]+=.3*np.sin(t*.23+self.seed*20)
        p[:,1]+=.3*np.sin(t*.27+self.seed*17)
        out.append(dict(pos=p,size=self.size,color=lin('#ffdfa1'),alpha=.46*fade,
                        kind='disc',dof=.5,fog=.08,twinkle=.03,seed=self.seed))
        return out


class Blessing:
    """At each gesture a wave crosses the lake and joins the same river."""
    def __init__(self):
        self.u=np.linspace(0,2*np.pi,750)
        self.hearts=[BR.HeartDrift(c+[0,1.6,0],float(a+1.4),float(a+3.3),
                     color=color,rate=2,life=2,rise=.45,spread=.35,size=(.05,.10))
                     for c,a,color in zip(CENTERS,STARTS,COLORS)]

    def sample(self,t):
        out=[]
        for c,a,color,hearts in zip(CENTERS,STARTS,COLORS,self.hearts):
            age=t-a-1.1
            if 0<age<5:
                r=.3+age*2.0
                p=c+np.stack([r*np.sin(self.u),np.full(750,.035),r*np.cos(self.u)],1)
                alpha=float(smooth(0,.7,age)*(1-smooth(2,5,age)))
                out.append(ribbon(p,width=.04,color=lin('#ffe3a6'),alpha=.45*alpha))
            h=hearts.sample(t)
            if h is not None:out.extend(h if isinstance(h,list) else [h])
        return out


class LivingVeil:
    """A continuous flowing surface made of fine light, opening around people."""
    def __init__(self):
        rng=np.random.default_rng(741)
        self.u=rng.random(38000)
        self.v=rng.random(38000)
        self.seed=rng.random(38000)

    def sample(self,t):
        a=float(window(5.8,52.3,t,2.2))
        if a<=0:return None
        z=8-100*self.u
        angle=.12+2.65*self.v+.20*np.sin(self.u*18-t*.24)
        radius=3.8+.65*np.sin(self.u*12-t*.20)
        x=-8.5+radius*np.cos(angle)-3*np.sin((z+6)*(.65/6))
        y=.16+radius*np.sin(angle)*(1+.2*np.sin(self.u*14+t*.18))
        p=np.stack([x,y,z],1)
        col=lin('#ffc570')[None]*(.65+.35*self.v[:,None])+lin('#fff0c4')[None]*.22
        return [dict(pos=p,size=.018+.018*self.seed,color=col,alpha=.50*a,emit=1.2,
                     kind='disc',dof=.3,seed=self.seed,twinkle=0),
                dict(pos=p[::18],size=.14,color=lin('#ffb34e'),alpha=.025*a,kind='soft',dof=0)]


class FirstLight:
    def sample(self,t):
        if t>9:return None
        u=float(smooth(6.6,8.6,t))
        p=np.array([[0,7.8*(1-u)+.1,2-5*u]])
        a=1-float(smooth(8.5,9,t))
        return [dict(pos=p,size=.18,color=lin('#fff0c3'),alpha=.85*a,emit=2,kind='disc'),
                dict(pos=p,size=.75,color=lin('#ffcc6b'),alpha=.15*a,kind='soft')]


class RisingStreams:
    def __init__(self):
        rng=np.random.default_rng(753)
        self.phase=rng.random((9,1800))
        self.offset=rng.normal(0,.14,(9,1800,3))

    def sample(self,t):
        a=float(window(43,53.6,t,1.8))
        if a<=0:return None
        out=[]
        u=np.linspace(0,1,650)
        for k,color in enumerate(COLORS):
            theta=k*2*np.pi/9+u*3.5-t*.12
            r=9*(1-u)+3*u
            p=np.stack([r*np.cos(theta),.2+u*12,-68+r*np.sin(theta)],1)
            al=a*(.5+.5*np.sin(u*13-t*1.4+k)**2)
            out.append(ribbon(p,width=.055,color=lin(color)*.35+lin('#ffcf88')*.65,alpha=al*.65,emit=1.3))
            out.append(dict(pos=p[::2],size=.045,color=lin('#ffe4b8'),alpha=al[::2]*.6,kind='disc',dof=0))
            v=(self.phase[k]+t*.13)%1
            th=k*2*np.pi/9+v*3.5-t*.12
            radius=9*(1-v)+3*v
            q=np.stack([radius*np.cos(th),.2+12*v,-68+radius*np.sin(th)],1)+self.offset[k]
            out.append(dict(pos=q,size=.024,color=lin('#ffe5af'),alpha=a*.7*np.sin(np.pi*v),
                            emit=1.4,kind='disc',dof=.1,twinkle=0))
        if t<49:
            out.append(dict(pos=np.array([[0,12,-68]]),size=.4,color=lin('#fff0c7'),
                            alpha=a*(1-float(smooth(47.5,49,t))),kind='disc',emit=1.5))
        return out


FINALE=BR.Finale(pos=(0,12,-68),radius=3.2,camera=CAMERA,look='night',
                 t_world=47.6,spin=3,front=-115.14-3*48,shrink=.48,
                 hearts=dict(t0=48,t1=51.8,n=27),t_settle=(51,53),
                 t_logo=(52,54),bloom=dict(t=53.8,strength=.035,glow=.2),
                 look_after='radiance_end',blend=1.8,
                 end=dict(t=(54,54.6),ride=(.5,.862,14),frac=.157),
                 logo=dict(reflect=False),n=60000)


def setup(scene):
    cast=CAST._cast()
    scenes=[('greeting',CAST.P1,(8.3,12.7),0),
            ('gratitude',CAST.P1b,(11.8,15.9),1),
            ('embrace',CAST.P2,(15,18.8),2),
            ('embrace',CAST.P2,(18.8,22.2),3),
            ('concession',CAST.P3+[-1,0,2],(22.3,25.8),4),
            ('respect',CAST.P3b,(25.5,29),5),
            ('compliment',CAST.P5b,(38.7,42.8),8)]
    for name,origin,source,k in scenes:
        delta=np.asarray(CAST.CAMERA.state(sum(source)/2).pos)-origin
        yaw=-np.degrees(np.arctan2(delta[0],delta[2]))
        a=float(STARTS[k])
        scene.add('encounter '+str(k),Performance(cast[name],origin,source,(a,a+3.85),CENTERS[k],yaw),reflect=True)
    for people,source,k in [(standing_encouragement(),(32,36),6),(standing_consideration(),(36,40),7)]:
        a=float(STARTS[k])
        scene.add('encounter '+str(k),Performance(people,(0,0,0),source,(a,a+3.85),CENTERS[k]),reflect=True)
    scene.add('opening hands of light',Performance(cast['hands0'],CAST.H0,(.8,7.6),(0,8.1),(0,7.4,2),scale=2.5),reflect=False)
    scene.add('the first light',KeepWords(FirstLight()),reflect=False)
    scene.add('the river',KeepWords(River()),reflect=True)
    scene.add('the living veil',KeepWords(LivingVeil()),reflect=True)
    scene.add('kindness spreading',KeepWords(Blessing()),reflect=True)
    scene.add('nine rising streams',KeepWords(RisingStreams()),reflect=True)
    clouds=[]
    rng=np.random.default_rng(733)
    for z in [-35,-85,-145]:
        for side in [-1,1]:
            clouds+=SKY.tower(rng,(side*28,0,z),19,36,n_layer=3,per=130)
    scene.add('lit cloud architecture',KeepWords(SKY.Billows(clouds,seed=732,alpha=.07,body=.22,
              top='#ffe1a0',warm='#ffb56c',rose='#ef7e9a',lilac='#8571cc',
              puff=.42,shade=.4,drift=(.018,0,0),gain=lambda t:1-float(smooth(51.5,54.5,t)))),reflect=True,depth_of_field=False)
    FINALE.add_to(scene)
    scene.add('expressions reach the world',MB.SymbolSwirl((0,12,-68),3.2,PW.LABELS,COLORS,
              48,52.2,CAMERA,scale=FINALE.scale,size=.42,orbit=(1.9,1.65),
              turns=.35,n=600,life=1.8,bright=.55,glow_world=.3),reflect=False)
    place=lambda t:(np.array([0,12,-68]),np.array([1,0,0]),np.array([0,1,0]))
    scene.add('final chord',MB.FinalGlow(place,57.5,width=11,height=7,ring=.012,glint=.02),reflect=False)
    for word in WORDS:
        mask=word.mask()
        if mask is not None:
            mask.strength=lambda t,a=word.t_in,b=word.t_out:float(a<=t<=b)
        scene.add('word '+word.name,word,reflect=False,depth_of_field=True,mask=mask)
        scene.add('word '+word.name+' light',word.lights,reflect=False)
    WORDS.check(CAMERA,min_read=2.5)


WORLD=dict(look=[(0,'radiance'),(44,'radiance_lift',3)],
    looks=dict(radiance=dict(base='predawn',sky_top='#0b1046',sky_mid='#38206c',
                sky_hor='#9a5068',water='#070818',haze_color='#7a4a6a',sun_color='#ffcf90',
                sun_el=-1.5,sun_az=190,sun_int=.55,sun_disc=0,sun_glow=.55),
               radiance_lift=dict(base='dawn',sky_top='#191253',sky_mid='#563477',
                sky_hor='#ce8271',water='#11152e',haze_color='#754461',
                sun_int=.55,sun_el=3,sun_az=190,sun_disc=1.2,sun_glow=.4),
               radiance_end=dict(base='dawn',sky_top='#eed8ce',sky_mid='#ffe8ce',
                sky_hor='#fff1d6',water='#ddc8ce',sun_int=.18,sun_el=16,sun_az=190)),
    stars=.7,milky=.12,clouds=.16,cloud_speed=.08,hills=.12,mirror=.7,ripple=.30,
    haze=.15,mist=.08,mist_color='#4a2a65',lanterns=0,floats=0,dust=.25,bokeh=.08,
    dust_color='#ffdda4',dust_color2='#f6af91',keep_hue=.8,react=dict(beat=.06,level=.06),
    shafts=[dict(base=(side*10,-15-j*18),radius=2,top=35,color='#ffd593',strength=.2)
            for j in range(4) for side in [-1,1]])
P3D=dict(camera=CAMERA,world=FINALE.world(WORLD),setup=setup,
         bursts=FINALE.bursts(),motion_blur=.65,motion_samples=1)
TITLES=dict(opening=dict(t_end=8.1,dissolve=1.1,y=.30,palette='night'),
            signature=dict(windows=[(7,54.8,'bl','night')],fade=.4,protect=dict(keep=0)),
            end_card=dict(t_in=54.5,fade=.5,scale=1,backdrop=True,veil=.65,ambient_motes=True))
