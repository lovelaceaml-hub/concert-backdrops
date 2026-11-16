"""The Light That Reaches You: a journey from a tender act to a radiant world.

Independent staging, camera, atmosphere and light choreography. Shared cast
performances and renderer APIs are read only. All motion is a function of time.
"""
import numpy as np
from songs.master_astra import *  # noqa: F401,F403
from songs import master_astra as CAST
from p3d import brand as BR, words as PW, master_brand as MB
from tools.radiance.colours import NineColours, StarGarden
from p3d.api import lin, ribbon
from tools.radiance.flight import make_camera
from tools.radiance.celebration import Celebration
from tools.radiance.actors import standing_encouragement, standing_consideration

TOTAL = SONG_END = 62.0
NFRAMES = int(TOTAL*FPS)
MUSIC_END = 62.0
TEXT_SHADOW = BOTTOM_CALM = 0.0
STARTS = 8.6 + np.arange(9)*3.9
CENTERS = np.array([[4*np.sin(k*.7),0,-20-16*k] for k in range(9)])
WORLD_CENTER = np.array([0,50,-174])
COLORS = [PW.COLORS[k] for k in PW.LABELS]


def smooth(a,b,t):
    u = np.clip((np.asarray(t)-a)/(b-a),0,1)
    return u*u*u*(u*(u*6-15)+10)


def window(a,b,t,fade=.5):
    return smooth(a,a+fade,t)*(1-smooth(b-fade,b,t))


def aim(p,c,where=(.65,.63)):
    return CAST._aim(np.asarray(p),np.asarray(c),*where,fov=44)


CAMERA, FLIGHT = make_camera(CENTERS, STARTS, aim)
SPECS=[]
for label,a,color in zip(PW.LABELS,STARTS,COLORS):
    reference=CAMERA.state(float(a+1.65))
    position=PW.place(reference,float(a+1.65),.5,.66,9)
    forward=reference.basis()[2]
    facing=np.degrees(np.arctan2(-forward[0],-forward[2]))
    SPECS.append(dict(expr=label,t_in=float(a+.05),t_read0=float(a+.4),
        t_read1=float(a+3.0),t_out=float(a+4.0),
        pos=position,em=PW.em_for(CAMERA,float(a+1.65),9,83),
        face='fixed',facing=float(facing),arrive='reveal',edge='out',soft=.18,leave='fade',
        color=color,paint=False,tint=.40,bright=.85,halo=.25,sparkle=.025,
        pill=True,sharp=1,n='auto',n_label=4000))
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
                xy,depth=cam.project(np.asarray(b[position]))
                x,y=xy.T
                keep=smooth(.8,2.1,depth)
                if t<8.1:
                    keep*=1-.9*(1-smooth(7,8.1,t))*window(.12,.88,x,.1)*window(.4,.98,y,.08)
                if 7<t<54.8:
                    keep*=1-window(-.1,.55,x,.06)*window(-.1,.24,y,.04)
                for a in STARTS:
                    hold=window(a+.1,a+3.15,t,.3)
                    keep*=1-.75*hold*window(.56,.78,x,.04)*window(.38,.55,y,.04)
                for word in WORDS:
                    strength=window(word.t_in,word.t_read1+.2,t,.25)
                    if strength>0:
                        box=PW.screen_box(word,cam,t)
                        if box[4]:
                            keep*=1-strength*window(box[0]-.02,box[1]+.02,x,.02)*window(box[2]-.02,box[3]+.02,y,.02)
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
        else:
            # The camera leaves along the river. Dissolve the encounter before
            # passing its stage, while the expression completes its read.
            fade*=float(1-smooth(b-1.4,b-.7,t))
        if fade<=.0001:return None
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


FINALE=BR.Finale(pos=tuple(WORLD_CENTER),radius=3.2,camera=CAMERA,look='night',
                 t_world=48.9,spin=3,front=-115.14-3*50,shrink=.48,
                 hearts=dict(t0=49.4,t1=52.5,n=27),t_settle=(51,53),
                 t_logo=(52,54),bloom=dict(t=53.8,strength=.10,glow=.45),
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
        yaw=-np.degrees(np.arctan2(delta[0],delta[2]))+np.degrees(FLIGHT.angles[k])
        a=float(STARTS[k])
        scene.add('encounter '+str(k),Performance(cast[name],origin,source,(a,a+3.85),CENTERS[k],yaw),reflect=True)
    for people,source,k in [(standing_encouragement(),(32,36),6),(standing_consideration(),(36,40),7)]:
        a=float(STARTS[k])
        scene.add('encounter '+str(k),Performance(people,(0,0,0),source,(a,a+3.85),CENTERS[k],np.degrees(FLIGHT.angles[k])),reflect=True)
    scene.add('nine colours of love',KeepWords(NineColours(CENTERS,STARTS,COLORS,FLIGHT)),reflect=True)
    scene.add('stars around the journey',KeepWords(StarGarden()),reflect=True)
    scene.add('kindness spreading',KeepWords(Blessing()),reflect=True)
    FINALE.add_to(scene)
    scene.add('expressions reach the world',MB.SymbolSwirl(tuple(WORLD_CENTER),3.2,PW.LABELS,COLORS,
              49.3,52.8,CAMERA,scale=FINALE.scale,size=.42,orbit=(1.9,1.65),
              turns=.35,n=600,life=1.8,bright=.55,glow_world=.3),reflect=False)
    place=lambda t:(WORLD_CENTER,np.array([1,0,0]),np.array([0,1,0]))
    scene.add('final chord',MB.FinalGlow(place,60.2,width=11,height=7,ring=.12,glint=.2),reflect=False)
    for word in WORDS:
        mask=word.mask()
        if mask is not None:
            mask.strength=lambda t,a=word.t_in,b=word.t_out:float(a<=t<=b)
        scene.add('word '+word.name,word,reflect=True,depth_of_field=True,mask=mask)
        scene.add('word '+word.name+' light',word.lights,reflect=True)
    WORDS.check(CAMERA,min_read=2.5)


WORLD=dict(look=[(0,'radiance'),(16,'rose_space',1.8),(24,'blue_space',1.8),
                (28,'ember_space',1.8),(35.5,'violet_space',1.8),(46.5,'radiance',1.5)],
    looks=dict(radiance=dict(base='night',sky_top='#020414',sky_mid='#060b28',
                sky_hor='#1a2051',water='#01030b',haze_color='#161b44',
                sun_int=0,sun_el=55,sun_disc=0,sun_glow=0),
               rose_space=dict(base='night',sky_top='#05031a',sky_mid='#21102b',
                sky_hor='#58243f',water='#08020d',sun_int=0,sun_el=55,sun_disc=0),
               blue_space=dict(base='night',sky_top='#02041a',sky_mid='#091548',
                sky_hor='#25275b',water='#010413',sun_int=0,sun_el=55,sun_disc=0),
               ember_space=dict(base='night',sky_top='#05051a',sky_mid='#251229',
                sky_hor='#63352c',water='#08040a',sun_int=0,sun_el=55,sun_disc=0),
               violet_space=dict(base='night',sky_top='#030218',sky_mid='#171039',
                sky_hor='#33205c',water='#02020b',sun_int=0,sun_el=55,sun_disc=0),
               radiance_end=dict(base='cream',sky_top='#d8e6f3',sky_mid='#f4e5e5',
                sky_hor='#fff0da',water='#cdd9ea',sun_int=.15,sun_el=55,
                sun_disc=0,stars=.08,milky=.05)),
    stars=1,milky=.8,clouds=.05,cloud_speed=.08,hills=.08,mirror=.65,ripple=.16,
    haze=.06,mist=.04,mist_color='#2a2048',lanterns=0,floats=0,dust=.12,bokeh=.02,
    dust_color='#dfdfff',dust_color2='#f8b6d5',keep_hue=.95,
    react=dict(beat=.06,level=.06))
P3D=dict(camera=CAMERA,world=FINALE.world(WORLD),setup=setup,
         bursts=FINALE.bursts(),motion_blur=.72,motion_samples=1)
TITLES=dict(opening=dict(t_end=8.1,dissolve=1.1,y=.30,palette='night'),
            signature=dict(windows=[(7,54.8,'bl','night')],fade=.4,protect=dict(keep=0)),
            end_card=dict(t_in=54.5,fade=.5,scale=1,backdrop=True,veil=.65,ambient_motes=True))
