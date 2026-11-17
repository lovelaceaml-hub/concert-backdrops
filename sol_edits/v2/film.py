"""The Light We Pass: Sol V2's independent creative treatment from v6.

One standing apology grows into an embrace; a gentle camera carries the light
through listening, prayer and practical kindness into the world. All approved
campaign copy and brand geometry comes from the untouched v6 engine.
"""
import types
import numpy as np
from songs import master_peace as film
from p3d.api import CameraState
from p3d.body import Body
from p3d import pairs

CUTS = [8.45, 12.30, 15.65, 22.25, 25.75, 29.10, 35.40, 39.00, 42.35, 44.65, 49.0]
DISSOLVE = 0.90
SHOT = None
v = film._v


def shot_at(t):
    return int(np.searchsorted(CUTS, t, side='right'))


def portrait(o, offset, t, a, b, sx=0.72, sy=0.62, height=1.05):
    u = film.sc(a - 0.5, b + 0.5, t)
    p = o + np.asarray(offset) + v(0.24*u, -0.03*u, -0.30*u)
    return p, film._aim(p, o + v(0,height,0), sx, sy, 46), 46


def pose(t, j):
    if j == 0:
        p = film.C0 + v(0.10*t/9, 0.012*t, -0.035*t)
        return p, v(0,54.2,-40), 50
    shots = {
        1: (film.P1, (-0.65,1.75,5.9), 8.45,12.30),
        2: (film.P1b, (-0.8,1.65,5.7), 12.30,15.65),
        4: (film.P3, (-1.5,1.65,7.6), 22.25,25.75),
        5: (film.P3b, (-0.8,1.75,6.0), 25.75,29.10),
        6: (film.P4, (-1.1,1.65,7.6), 29.10,35.40),
        7: (film.P5, (-4.2,1.85,5.4), 35.40,39.0),
        8: (film.P5b, (-1.25,1.7,6.4), 39.0,42.35),
    }
    if j in shots:
        o,off,a,b=shots[j]
        return portrait(o,off,t,a,b,height=0.95 if j in (6,7) else 1.05)
    if j == 3:
        # A single unbroken view for the apology, acceptance and embrace.
        u=film.sc(15.2,22.7,t)
        az=np.radians(-19+12*u)
        p=film.P2+v(np.sin(az)*6.2,1.8,np.cos(az)*6.2)
        return p,film._aim(p,film.P2+v(0,1.02,0),0.72,0.62,46),46
    if j == 9:
        u=film.sc(41.9,45.1,t)
        p=film.A7+v(0.8+u,3.5+0.6*u,18+2*u)
        return p,film.PEARL+v(0,0.6,0),52
    if j == 10:
        u=film.sc(44.2,49.5,t)
        az=np.radians(204+30*u)
        p=film.A7+v(np.sin(az)*19,8+10*u,np.cos(az)*19)
        inward=film.A7+v(0,5+9*u,0)
        return p,inward,56
    u=film.sc(48.6,53.85,t)
    p=film._fin_cam(-10+18*u,-4+5*u,(4.5-0.6*u)*film.FIN_R)
    drop=film._LOGO_DROP*film.sc(51.9,53.85,t)
    drift=film.sc(54.5,61.4,t)
    return p-v(0,drop,0)+v(0.15*drift,0.8*drift,0),film.FIN_C-v(0,film.FIN_LIFT+drop-0.8*drift,0),50


def state(self, t, aspect=16/9, ref=None):
    p, q, fov = pose(t, shot_at(t) if SHOT is None else SHOT)
    return CameraState(pos=p, target=q, fov=fov, aspect=aspect, aperture=0, focus=np.linalg.norm(q-p))


# Preserve object identity: words, logo, world and renderer share these rigs.
for rig in (film.CAMERA, film._LAYOUT):
    rig.state = types.MethodType(state, rig)
    rig.handheld = 0
    rig.cuts = lambda: list(CUTS)

GOLD = dict(look=dict(name='glitter', glints=0, seams=0.45), color='#f2a640', color2='#ffdc96', bright=1.30)
IVORY = dict(look=dict(name='glitter', glints=0, seams=0.45), color='#efb75d', color2='#ffe5af', bright=1.30)


def person(o, x, z=0, facing=0, shape='woman', show=(0,62), gesture=(), motion='stand', seed=1, ivory=False, **kw):
    return Body(shape, at=(o[0]+x, o[2]+z), facing=facing, garment='dress' if shape=='woman' else 'tunic',
                hair='bun' if shape=='woman' else 'short', points=65000, show=show, fade=0.65,
                gesture=gesture, motion=motion, seed=seed, wind=None, **(IVORY if ivory else GOLD), **kw)


def cast():
    if film._CAST:
        return film._CAST
    C = film._CAST
    C['hands0'] = film._mother_hands()
    C['greeting'] = [person(film.P1, -0.52 if k==0 else 0.52, shape='man', facing=78 if k==0 else 282,
        show=(8.1,13), seed=21+k, ivory=bool(k), gesture=[
            (9.1+0.35*k,12.7,'bow',dict(amount=12, ease=1.15)),
            (10.2+0.35*k,12.7,'nod',dict(amount=3,period=3))]) for k in range(2)]
    C['gratitude'] = [person(film.P1b,0, facing=25, show=(11.8,16.2), seed=33,
        gesture=[(12.3,16,'hand_on_heart',dict(bow=6,ease=1.05)),(12.9,16,'bow',dict(amount=11,ease=1.1))])]
    # A low-handed apology, then a small step into a true same-gender embrace.
    o=film.P2
    a=dict(shape='woman',facing=90,garment='dress',hair='bun',height=1.64,
        at=[(0,(o[0]-0.48,o[2]-0.09)),(18.9,(o[0]-0.48,o[2]-0.09)),(19.65,(o[0]-0.19,o[2]-0.09))],
        motion=[(-1e9,'stand'),(18.85,'shuffle',dict(blend=0.3)),(19.7,'stand',dict(blend=0.4))],
        points=70000,show=(15.0,22.9),fade=0.75,seed=61,**GOLD,
        gesture=[(15.6,19.2,'open_hands',dict(bow=9,ease=1.15)),(16.1,19.2,'bow',dict(amount=8,ease=1.2))])
    b=dict(shape='woman',facing=270,garment='dress',hair='tied',height=1.60,
        at=[(0,(o[0]+0.48,o[2]+0.09)),(18.9,(o[0]+0.48,o[2]+0.09)),(19.65,(o[0]+0.19,o[2]+0.09))],
        motion=[(-1e9,'stand'),(18.85,'shuffle',dict(blend=0.3)),(19.7,'stand',dict(blend=0.4))],
        points=70000,show=(15.0,22.9),fade=0.75,seed=62,**IVORY,
        gesture=[(16.1,19.4,'listen',dict(amount=0.45,ease=1.2)),(16.8,19.5,'nod',dict(amount=3,period=3.2))])
    C['embrace']=list(pairs.embrace(19.35,at=(o[0],o[2]),facing=90,a=a,b=b,until=22.8,gap=0.38,side=0.09,ease=1.15))
    o=film.P3
    C['concession']=[Body('man',at=[(0,(o[0]-1.0,o[2]+2)),(22.6,(o[0]-1.0,o[2]+2)),(23.5,(o[0]-1.45,o[2]+2.05))],
        facing=[(22.6,5),(23.5,15)],garment='tunic',hair='short',points=70000,show=(21.6,26.3),fade=0.7,seed=51,**GOLD,
        motion=[(-1e9,'stand'),(22.55,'shuffle',dict(blend=0.35)),(23.6,'stand',dict(blend=0.45))],
        gesture=[(22.8,26.1,'after_you',dict(side='L',bow=7,ease=1.3,to=o+v(-1.0,0.90,2.35)))])]
    # Standing listeners read clearly above their reflections; small, slow nods avoid bobbing.
    refs2=pairs.Refs()
    ra=dict(shape='man',at=(film.P3b[0]-0.43,film.P3b[2]),facing=72,garment='tunic',hair='short',
        points=65000,show=(25.1,29.5),fade=0.7,seed=71,**IVORY,
        gesture=[(25.6,29.4,'listen',dict(amount=0.55,ease=1.1)),(26.3,29.4,'nod',dict(amount=3,period=3.1))])
    rb=dict(shape='man',at=(film.P3b[0]+0.43,film.P3b[2]),facing=288,garment='tunic',hair='short',
        points=65000,show=(25.1,29.5),fade=0.7,seed=72,**GOLD,
        gesture=[(25.6,29.4,'explain',dict(side='R',period=3.2,ease=1.3))])
    C['respect']=refs2.build(('a','b'),a=ra,b=rb)
    C['encouragement']=[person(film.P4,0.25,facing=35,show=(28.3,35.9),seed=81,ivory=True,
        motion=[(-1e9,'kneel',dict(dur=0.01,sit=0.75,hands='pray'))],
        gesture=[(29.4,35.8,'bow',dict(amount=7,ease=1.5))]),
        person(film.P4,-0.40,-0.16,facing=45,show=(28.3,35.9),seed=82,
        gesture=[(29.2,35.8,'hand_on_heart',dict(bow=6,ease=1.5))])]
    ka=dict(shape='man',points=70000,show=(34.8,39.5),fade=0.7,seed=91,**GOLD)
    kb=dict(shape='man',points=70000,show=(34.8,39.5),fade=0.7,seed=92,**IVORY)
    C['consideration']=list(pairs.helped_up(36.2,at=(film.P5[0],film.P5[2]),facing=67,
        a=ka,b=kb,rise=1.9,reach=1.1,apart=0.70))
    # The praised person receives the compliment; the second person applauds at chest height.
    C['compliment']=[person(film.P5b,0.25,facing=335,show=(38.3,42.8),seed=101,ivory=True,
        gesture=[(39.0,42.7,'hand_on_heart',dict(bow=4,ease=1.2)),(39.8,42.7,'bow',dict(amount=6,ease=1.2))]),
        person(film.P5b,-0.65,-0.10,facing=65,show=(38.3,42.8),seed=102,
        gesture=[(38.9,42.7,'clap',dict(period=0.78,height=0,width=0.10,ease=1.0))])]
    # Contact references must omit secondary hand motion as well as gestures.
    # The baseline raw reference calls living hands, which re-enters the other
    # person's gestures at earlier times. Keep ordinary performed hands alive.
    for group in ('embrace','consideration'):
        for body in C[group]:
            original=body.actor.frame
            def frame(self,t,lock=True,gest=True,life=True,original=original):
                return original(t,lock=lock,gest=gest,life=life if gest else False)
            body.actor.frame=types.MethodType(frame,body.actor)
            body.actor._cache.clear()
    return C


class Steady:
    """Keep the golden grain, remove shader twinkle and hard glints from scenery."""
    def __init__(self,inner):
        self.inner=inner
        self.wants_camera=getattr(inner,'wants_camera',False)
        if hasattr(inner,'gain'): self.gain=inner.gain
    def sample(self,t,cam=None):
        res=self.inner.sample(t,cam) if self.wants_camera else self.inner.sample(t)
        if res is None: return None
        out=[]
        for b in res if isinstance(res,(tuple,list)) else [res]:
            if b is None: continue
            b=dict(b,twinkle=0)
            if b.get('kind')=='spark': b.update(kind='soft',emit=np.minimum(b.get('emit',1),1.5))
            out.append(b)
        return out


class Stage:
    def __init__(self,scene): self.scene=scene
    def add(self,name,ps,**kw):
        # No sparkling carpet behind Respect; the scene keeps its tree and mirror.
        if name in ('river','crowd5','clouds_dive','hearts5') or name.startswith('hearts_'): return
        if name=='pillar7': ps=film._Fade(ps,lambda t: 0.42)
        if name=='rain':
            ps=film._Fade(ps,lambda t: 1-0.78*film.sc(15.1,15.8,t)*(1-film.sc(21.8,22.5,t)))
        if name in ('door','petals3'):
            ps=film._Fade(ps,lambda t: 1-0.92*film.sc(22.2,22.8,t)*(1-film.sc(25.4,25.8,t)))
        if name=='tree': ps=film.NearFade(ps,8)
        self.scene.add(name,Steady(ps),**kw)


_original_setup=film._setup
film._cast=cast

def setup(scene):
    _original_setup(Stage(scene))
    # Hearts arise from the real performed gesture, never from a fixed icon above it.
    from p3d import brand as BR
    from p3d import master_brand as MB
    # Nine visible currents carry the nine expressions into the final world.
    heads=[]
    for k in range(9):
        def path(t,k=k):
            age=max(0,t-44.5)
            az=2*np.pi*k/9+0.65*age
            radius=2.2+1.15*age
            return film.A7+v(radius*np.sin(az),3+2.8*age,radius*np.cos(az))
        gain=lambda t: film.sc(44.45,45.05,t)*(1-film.sc(48.4,49.4,t))
        heads.append((path,film.NINE_GLOW[k],gain,0.65))
    scene.add('nine currents',Steady(MB.Rivers(heads,cuts=[44.45],tail=1.6,seed=615)),reflect=False)
    C=cast()
    plan=[('greeting',0,'Greeting',10.2,11.8),('gratitude',0,'Gratitude',13.4,15.0),
          ('embrace',0,'Apology',17.2,18.5),('embrace',1,'Inclusiveness',20.3,21.7),
          ('concession',0,'Concession',23.5,25.1),('respect',0,'Respect',26.7,28.3),
          ('encouragement',0,'Encouragement',31.0,33.4),('consideration',1,'Consideration',37.0,38.5),
          ('compliment',0,'Compliment',40.1,41.8)]
    for k,(group,index,label,a,b) in enumerate(plan):
        body=C[group][index]
        src=lambda t,body=body: body.where(t,'heart')
        ps=BR.HeartDrift(src,a,b,color=film.GLOWC[label],rate=2.0,life=3.0,rise=0.38,
                         spread=0.22,size=(0.045,0.085),style='heart',seed=810+k)
        scene.add('passed light '+label,film.Clear(Steady(ps)),reflect=False)

# Gentle colour transitions instead of the two zero-duration look switches in v6.
film.LOOK_KEYS[:]=[(a,b,1.4 if len(k)<3 or k[2]==0 else k[2]) for k in film.LOOK_KEYS for a,b in [k[:2]]]
film.P3D['world']['look']=[(k[0],k[1],1.4) if len(k)>2 and k[2]==0 else k
                            for k in film.P3D['world']['look']]
film.TITLES['end_card'].update(t_out=63.0,backdrop=None,veil=0.65)
film.FINAL_HIT=55.72
film.P3D.update(setup=setup,motion_blur=0.6)
# The baseline setup builds all Body layers before returning. Retain the soft body grain with no twinkle.
for name,value in vars(film).items():
    if not name.startswith('__'): globals().setdefault(name,value)
AUDIO_FILE='work/sol2/sol-v2-score.wav'
