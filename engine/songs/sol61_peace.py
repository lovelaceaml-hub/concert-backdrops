"""Sol's independent v6 edit: lyrical dissolves, restrained acting, a living close.

The v6 scenery, approved campaign copy and brand geometry remain the foundation.
Overrides are local to this song's Python process; no baseline file is changed.
Use tools/sol61/render.py to composite both moving views at each dissolve.
"""
import types
import numpy as np
from songs import master_peace as film
from p3d.api import CameraState
from p3d.body import Body
from p3d import pairs

CUTS = [8.65, 12.4, 15.6, 19.0, 22.25, 25.7, 28.9, 35.4, 38.95, 42.2, 44.6, 49.2]
DISSOLVE = 0.8
SHOT = None
v = film._v


def shot_at(t):
    return int(np.searchsorted(CUTS, t, side='right'))


def portrait(o, offset, subject_y, t, a, b, sx=0.70, sy=0.70, fov=46):
    u = film.sc(a - 0.4, b + 0.4, t)
    p = o + np.asarray(offset) + v(0.22 * u, -0.04 * u, -0.38 * u)
    q = film._aim(p, o + v(0, subject_y, 0), sx, sy, fov)
    return p, q, fov


def pose(t, j):
    if j == 0:
        p = film.C0 + v(0.12 * t / 9, 0.015 * t, -0.035 * t)
        return p, v(0, 54.2, -40), 50
    shots = {
        1: (film.P1, (-0.7, 1.65, 5.3), 1.18, 8.65, 12.4),
        2: (film.P1b, (-1.0, 1.55, 5.1), 1.17, 12.4, 15.6),
        3: (film.P2, (-1.2, 1.65, 5.8), 1.18, 15.6, 19.0),
        4: (film.P2, (-0.5, 1.6, 5.5), 1.18, 19.0, 22.25),
        5: (film.P3, (-1.6, 1.65, 8.0), 1.2, 22.25, 25.7),
        6: (film.P3b, (-1.0, 1.6, 5.8), 1.18, 25.7, 28.9),
        7: (film.P4, (-1.0, 1.55, 7.0), 1.00, 28.9, 35.4),
        8: (film.P5, (-4.0, 1.7, 4.7), 1.0, 35.4, 38.95),
        9: (film.P5b, (-1.5, 1.6, 6.0), 1.18, 38.95, 42.2),
    }
    if j in shots:
        return portrait(*shots[j][:3], t, *shots[j][3:])
    if j == 10:
        u = film.sc(41.8, 45, t)
        p = film.A7 + v(0.5 + u, 3.2 + 0.6 * u, 17 + 2 * u)
        return p, film.PEARL + v(0, 0.7, 0), 52
    if j == 11:
        u = film.sc(44.2, 49.6, t)
        az = np.radians(200 + 24 * u)
        p = film.A7 + v(np.sin(az) * 20, 9 + 132 * u, np.cos(az) * 20)
        q = p + 100 * film._unit(film.HV + v(0, -0.055, 0))
        return p, q, 56
    # The globe is already framed when the dissolve arrives. No long flight to it.
    u = film.sc(48.8, 53.85, t)
    p = film._fin_cam(-12 + 20 * u, -4 + 5 * u, (4.45 - 0.55 * u) * film.FIN_R)
    drop = film._LOGO_DROP * film.sc(51.9, 53.85, t)
    p = p - v(0, drop, 0)
    q = film.FIN_C - v(0, film.FIN_LIFT + drop, 0)
    drift = max(t - 54.4, 0)
    return p + v(0.10 * drift, 0.20 * drift, 0), q + v(0, 0.20 * drift, 0), 50


def state(self, t, aspect=16/9, ref=None):
    p, q, fov = pose(t, shot_at(t) if SHOT is None else SHOT)
    return CameraState(pos=p, target=q, fov=fov, aspect=aspect, aperture=0, focus=np.linalg.norm(q-p))


# Preserve object identity: words, logo, world and renderer share these rigs.
for rig in (film.CAMERA, film._LAYOUT):
    rig.state = types.MethodType(state, rig)
    rig.handheld = 0
    rig.cuts = lambda: list(CUTS)

GOLD = dict(look=dict(name='glitter', glints=0, seams=0.45), color='#f2a640', color2='#ffdc96', bright=1.30)
IVORY = dict(look=dict(name='glitter', glints=0, seams=0.45), color='#ffc664', color2='#fff0c8', bright=1.30)


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
    # Both stay standing. The apology is an open, low-handed bow, without a reach at a face or a stray knee.
    refs = pairs.Refs()
    a = dict(shape='woman',at=(film.P2[0]-0.31,film.P2[2]),facing=72,garment='dress',hair='bun',
        points=70000, show=(15.0,22.9),fade=0.7,seed=61, **GOLD,
        gesture=[(15.6,19.3,'open_hands',dict(bow=10,ease=1.0)),
                 (16.2,19.2,'bow',dict(amount=9,ease=1.1)),
                 (19.0,22.8,'arm_round',dict(side='L',to=lambda t: refs['b'].where(t,'shoulder.L',raw=True),ease=1.25))])
    b = dict(shape='woman',at=(film.P2[0]+0.31,film.P2[2]),facing=312,garment='dress',hair='tied',
        points=70000,show=(15.0,22.9),fade=0.7,seed=62, **IVORY,
        gesture=[(16.1,19.7,'listen',dict(ease=1.2)),(16.7,19.8,'nod',dict(amount=3,period=3)),
                 (19.2,22.8,'hand_on_heart',dict(side='R',bow=3,ease=1.2))])
    C['embrace'] = refs.build(('a','b'),a=a,b=b)
    C['concession'] = [person(film.P3,-1,2,facing=5,shape='man',show=(21.7,26.2),seed=51,
        gesture=[(22.7,26.1,'after_you',dict(side='L',bow=7,ease=1.3,
                  to=film.P3+v(0.0,0.85,2.3)))])]
    # Standing listeners read clearly above their reflections; small, slow nods avoid bobbing.
    refs2=pairs.Refs()
    ra=dict(shape='woman',at=(film.P3b[0]-0.43,film.P3b[2]),facing=72,garment='dress',hair='bun',
        points=65000,show=(25.1,29.5),fade=0.7,seed=71,**IVORY,
        gesture=[(25.6,29.4,'listen',dict(ease=1.1)),(26.3,29.4,'nod',dict(amount=3,period=3.1))])
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
        a=ka,b=kb,rise=2.0,reach=1.1,apart=0.66))
    # The praised person receives the compliment; the second person applauds at chest height.
    C['compliment']=[person(film.P5b,0.25,facing=335,show=(38.3,42.8),seed=101,ivory=True,
        gesture=[(39.0,42.7,'hand_on_heart',dict(bow=4,ease=1.2)),(39.8,42.7,'bow',dict(amount=6,ease=1.2))]),
        person(film.P5b,-0.65,-0.10,facing=65,show=(38.3,42.8),seed=102,
        gesture=[(38.9,42.7,'clap',dict(period=0.85,height=0,width=0.13,ease=1.0))])]
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
        if name in ('river','crowd5','clouds_dive','pillar7'): return
        if name in ('door','petals3'):
            ps=film._Fade(ps,lambda t: 1-0.88*film.sc(22.4,22.9,t)*(1-film.sc(25.45,25.65,t)))
        if name=='tree': ps=film.NearFade(ps,8)
        self.scene.add(name,Steady(ps),**kw)


_original_setup=film._setup
film._cast=cast

def setup(scene):
    _original_setup(Stage(scene))

# Gentle colour transitions instead of the two zero-duration look switches in v6.
film.LOOK_KEYS[:]=[(a,b,1.4 if len(k)<3 or k[2]==0 else k[2]) for k in film.LOOK_KEYS for a,b in [k[:2]]]
film.P3D['world']['look']=[(k[0],k[1],1.4) if len(k)>2 and k[2]==0 else k
                            for k in film.P3D['world']['look']]
film.TITLES['end_card'].update(t_out=62.0,backdrop=None,veil=0.65)
film.P3D.update(setup=setup,motion_blur=0.6)
# The baseline setup builds all Body layers before returning. Retain the soft body grain with no twinkle.
for name,value in vars(film).items():
    if not name.startswith('__'): globals().setdefault(name,value)
AUDIO_FILE='work/sol61/sol61-medley.wav'
