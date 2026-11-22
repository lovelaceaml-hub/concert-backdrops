"""Three native cinematic performances in the established luminous world.

01: a close solo with two substantial pleated fans and finite silk.
02: five performers travel, change levels and open a petal canon.
04: a calligrapher's actual hand draws spatial strokes and releases them.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter1d

from p3d.api import lin, ribbon
from p3d.body import Body
from p3d import looks
from p3d.camera import Rig, dolly, orbit
from tools.concert_fan.props import FanSilk
from tools.concert_kit.models import Willow, Flowers, Lantern, segments, smooth
from .dancers_motion import install

ROOT = Path(__file__).resolve().parents[2]


def _palette(body, upper, lower):
    for layer in body.layers:
        ids = layer["idx"]
        part, h = body.cloud["part"][ids], body.cloud["h"][ids]
        color = np.broadcast_to(np.array(layer["color"]), (len(ids), 3)).copy()
        cloth = (part == looks.CLOTH) | (part == looks.VEIL)
        mix = smooth(.43, .64, h)
        tint = lin(lower)[None] * (1-mix[:, None]) + lin(upper)[None] * mix[:, None]
        color[cloth] = tint[cloth]
        layer["color"] = color
        layer["alpha"] = np.asarray(layer["alpha"]) * np.where(part == looks.HAND, .40, np.where(part == looks.FOOT, .60, 1.0))


def _body(mode, at, role=0, delay=0, points=76000, palette=("#b9addf", "#ead7ca")):
    b = Body("woman", height=1.66 + .012 * (role % 3), at=at, facing=0,
             garment="dress" if mode != "script" else "robe", hair="bun",
             points=points, detail=dict(hand=3.6, head=1.8, foot=2.0),
             color="#e6bd78", color2="#ffe3b3", bright=1.26,
             wind=(.07, 0, .025), gust=.045, build=.95 + role * .008,
             seed=612 + role * 37 + (70 if mode == "script" else 0),
             look=[dict(name="glitter", bright=1.0, seams=.48, glints=.00016),
                   dict(name="rim", bright=.28, power=3.8)])
    _palette(b, *palette)
    install(b, mode=mode, role=role, delay=delay)
    return b


class PleatedFan:
    """A hand-bound, materially dense pleated fan, including rib and rim detail."""
    def __init__(self, grip, color="#d292d7", edge="#e9c1ed", seed=1):
        self.grip, self.color, self.edge = grip, lin(color), lin(edge)
        rng = np.random.default_rng(seed)
        n = 6400
        self.r = grip.radius * np.sqrt(rng.uniform(.015, 1, n))
        self.a = rng.uniform(-.5, .5, n) * grip.spread
        self.grain = rng.uniform(.75, 1.25, n)
        self.ribs = np.linspace(-.5, .5, 23) * grip.spread

    def sample(self, t):
        p, across, outward, normal = self.grip.hand_frame(t)
        pleat = .012 * np.sin(self.a / self.grip.spread * 44 * np.pi) * self.r / self.grip.radius
        points = p + self.r[:, None] * (np.sin(self.a)[:, None] * across + np.cos(self.a)[:, None] * outward) + pleat[:, None] * normal
        border = smooth(.79, .96, self.r / self.grip.radius)
        color = self.color[None] * (1-border[:, None]) + self.edge[None] * border[:, None]
        # A quiet radial pattern gives the fan substance and records wrist roll.
        scallop = .78 + .22 * np.cos(11 * self.a) ** 2
        col = color * scallop[:, None]
        a = np.linspace(-.5, .5, 190) * self.grip.spread
        rr = self.grip.radius * (1 + .024 * np.sin(23 * a))
        rim = p + rr[:, None] * (np.sin(a)[:, None] * across + np.cos(a)[:, None] * outward)
        ends = p + self.grip.radius * (np.sin(self.ribs)[:, None] * across + np.cos(self.ribs)[:, None] * outward)
        return [dict(pos=points, size=.0105, color=col, alpha=.20 * self.grain,
                     kind="soft", normal=np.broadcast_to(normal, points.shape), emit=.62, twinkle=0),
                dict(pos=np.broadcast_to(p, ends.shape).copy(), pos2=ends, kind="line", size=.0023,
                     color=lin("#e9c590"), alpha=.34, emit=.72, twinkle=0),
                ribbon(rim, width=.0050, color=self.edge, alpha=.45, emit=.8, twinkle=0)]


class SilkOnly(FanSilk):
    def _fan_batches(self, t):
        return []


class Stage:
    static = True
    def __init__(self, radius=2.2, center=(0, 0, 0), color="#a59bcc", seed=60):
        self.center, self.radius, self.color = np.asarray(center), radius, color
        rng = np.random.default_rng(seed)
        a, r = rng.uniform(0, 2*np.pi, 11500), np.sqrt(rng.random(11500)) * radius
        self.points = self.center + np.stack([r*np.cos(a), np.full(len(a), .004), .76*r*np.sin(a)], 1)
        self.size = rng.uniform(.006, .014, len(a))

    def sample(self, t):
        a = np.linspace(0, 2*np.pi, 320)
        curves = [self.center + np.stack([self.radius*k*np.cos(a), np.full(len(a), .010), .76*self.radius*k*np.sin(a)], 1) for k in (1, 1.012, 1.045)]
        return [dict(pos=self.points, size=self.size, color=lin(self.color), alpha=.10, kind="soft", emit=.8),
                segments(curves, self.color, width=.006, alpha=.25)]


class PetalArchitecture:
    """Large three-dimensional, sparse petal portals receding behind the cast."""
    def __init__(self, wide=False):
        self.wide = wide

    def sample(self, t):
        out = []
        u = np.linspace(0, np.pi, 240)
        for j in range(7):
            spread = (3.9 if self.wide else 2.6) + j*.32
            p = np.stack([spread*np.cos(u), .18+(3.8+j*.23)*np.sin(u)**.84,
                          -4.5-j*.9+.35*np.sin(u*2)], 1)
            c = ("#b7a0df", "#8baedc", "#e3c79b")[j%3]
            out.append(ribbon(p, width=.007 if j%3 else .012, color=lin(c),
                              alpha=.24 if j%3 else .31, emit=1.0, twinkle=0))
            # Moving points illuminate each structure without filling the hero.
            phase = (t*.09+j*.13) % 1
            k = int(phase*(len(p)-1))
            out.append(dict(pos=p[max(k-2, 0):k+3], size=.027, color=lin(c), alpha=.35, emit=1.4, kind="spark", twinkle=.1))
        return out


class PetalWake:
    """Small drifting petals leave the fans' upper edge with real provenance."""
    def __init__(self, grips, seed=80):
        self.grips = grips
        rng = np.random.default_rng(seed)
        self.birth = np.sort(rng.uniform(1, 18.7, 210))
        self.life = rng.uniform(1.6, 3.5, len(self.birth))
        self.owner = rng.integers(0, len(grips), len(self.birth))
        self.phase = rng.uniform(0, 6.28, len(self.birth))
        self.starts = np.array([grips[o].hand_frame(float(t))[0] + grips[o].hand_frame(float(t))[2]*grips[o].radius for o, t in zip(self.owner, self.birth)])

    def sample(self, t):
        age = t-self.birth
        keep = (age>0)&(age<self.life)
        if not keep.any():
            return None
        a, q = age[keep], self.phase[keep]
        p = self.starts[keep].copy()
        p[:, 0] += .15*a*np.sin(q+a*1.5)
        p[:, 1] += .34*a-.04*a*a
        p[:, 2] -= .22*a
        return dict(pos=p, size=.018+.009*np.sin(q)**2, color=lin("#d7a8db"),
                    alpha=.24*np.sin(np.pi*a/self.life[keep]), kind="petal", rot=q+a*1.1,
                    emit=.9, twinkle=.08)


class Calligraphy:
    """Spatial ink drawn by the solved wrist, retained then released upward."""
    def __init__(self, body):
        self.body = body
        self.times = np.arange(0, 20.0001, 1/60)
        self.track = np.array([body.where(float(t), "palm.R") for t in self.times])
        self.left = np.array([body.where(float(t), "palm.L") for t in self.times])
        # The brush retains its broad gesture while the small weight-transfer
        # corrections in the wrist no longer leave a serrated ink edge.
        self.ink = gaussian_filter1d(self.track, 9, axis=0, mode="nearest")
        rng = np.random.default_rng(422)
        self.brush_u = np.sort(rng.random(5200))
        self.brush_v = rng.uniform(-.5, .5, len(self.brush_u))
        self.brush_grain = rng.uniform(.70, 1.25, len(self.brush_u))

    def _sample(self, times, data):
        return np.stack([np.interp(times, self.times, data[:, j]) for j in range(3)], 1)

    def _brush(self, points, width, color, alpha):
        """Variable-pressure ribbon with a finite, softly grained brush face."""
        m = len(points)
        u = np.linspace(0, 1, m)
        width = np.broadcast_to(width, (m,))
        alpha = np.broadcast_to(alpha, (m,))
        tangent = np.gradient(points, axis=0)
        across = np.cross(tangent, np.array([0., 0., 1.]))
        across /= np.maximum(np.linalg.norm(across, axis=1), 1e-7)[:, None]
        p = np.stack([np.interp(self.brush_u, u, points[:, j]) for j in range(3)], 1)
        side = np.stack([np.interp(self.brush_u, u, across[:, j]) for j in range(3)], 1)
        w = np.interp(self.brush_u, u, width)
        a = np.interp(self.brush_u, u, alpha)
        p += side * (w*self.brush_v)[:, None]
        return [ribbon(points, width=width*.12, color=lin(color), alpha=alpha*.30,
                       emit=1.10, twinkle=0),
                dict(pos=p, size=.009, color=lin(color), alpha=a*.50*self.brush_grain,
                     kind="soft", emit=1.10, twinkle=0)]

    def sample(self, t):
        out = []
        # The live brush never detaches from the final solved palm.
        age = np.linspace(3.0, 0, 240)
        past = np.clip(t-age, 0, 20)
        p = self._sample(past, self.ink)
        p[:, 2] -= .08*age
        p[:, 1] += .075*age
        palm = self.body.where(t, "palm.R")
        p += (palm-p[-1])[None] * smooth(2.55, 3.0, 3.0-age)[:, None]
        alpha = .74*np.sqrt(np.linspace(0, 1, len(age))) * smooth(.15, 1.0, t)
        width = .026 + .080*np.sin(np.linspace(0, np.pi, len(age)))**1.3
        out.extend(self._brush(p, width, "#efc87e", alpha))
        # Written gestures enlarge after their brush has passed, tracing portals
        # through depth; they are abstract flourishes, not inaccurate lettering.
        for j, (start, end) in enumerate(((.8, 5.5), (6.1, 10.8), (11.4, 16.5))):
            if t<start:
                continue
            ts = np.linspace(start, min(t, end), 350)
            q = self._sample(ts, self.ink)
            center = q.mean(0)
            age2 = np.maximum(t-ts, 0)
            release = float(smooth(end, end+3.2, t))
            scale = 1+1.65*release
            q = center + (q-center)*scale
            q[:,0] += (-1.10, 1.05, .10)[j]*release
            q[:,1] += (1.0, 1.2, 1.85)[j]*release + .025*age2
            q[:,2] -= (1.5+j*.35)*release
            fade = (.52-.12*smooth(end+5, end+10, t)) * np.ones(len(q))
            pressure = .024 + .13*np.sin(np.linspace(0,np.pi,len(q)))**1.3
            taper = smooth(0,.07,np.linspace(0,1,len(q))) * (1-smooth(.94,1,np.linspace(0,1,len(q))))
            out.extend(self._brush(q, pressure*(.7+.3*release), ("#e2bf81", "#c2a5e4", "#91cce1")[j], fade*taper))
        return out


class ScriptGallery:
    """Tall floating scroll frames and their reflections make a distinct set."""
    static = True
    def sample(self, t):
        curves = []
        for side in (-1,1):
            for j in range(5):
                x, z, h = side*(2.7+j*.9), -3-j*2.3, 3.4+j*.3
                for off in (0,.055):
                    curves.append(np.array([[x-.50-off,.15,z], [x-.50-off,h,z], [x+.50+off,h,z], [x+.50+off,.15,z]]))
                a = np.linspace(0,2*np.pi,120)
                curves.append(np.stack([x+.26*np.cos(a), h+.31+.26*np.sin(a), np.full(len(a),z)],1))
        return segments(curves, "#93a8cf", .006, .27, emit=.85)


def _environment(scene, film_id):
    scene.add("dancer_stage", Stage(radius=4.9 if film_id==2 else 2.2, color="#93a6ce" if film_id==4 else "#b1a0cc", seed=film_id*77))
    if film_id==4:
        scene.add("script_gallery", ScriptGallery())
    else:
        scene.add("petal_architecture", PetalArchitecture(wide=film_id==2))
        for j, (x,z) in enumerate(((-5.5,-5.0),(6.1,-7.0))):
            tree = Willow(at=(x,0,z), height=4.5+j*.8, spread=2.4, variant="blossom", bloom=2+j, seed=891+j)
            tree.gain=lambda t:.55
            scene.add("blossom_tree_"+str(j),tree)
        for j, (x,z) in enumerate(((-3.5,1.2),(3.7,.6),(-4.8,-3.0),(5.0,-4.0))):
            if film_id==2:
                x *= 1.45
            flower=Flowers(at=(x,0,z),count=18,radius=.75,height=.35,bloom=1.2+j,seed=490+j)
            flower.gain=lambda t:.62
            scene.add("shore_flowers_"+str(j),flower)
    for j,(x,z) in enumerate(((-2.7,-1.8),(3.0,-2.5),(-4.4,-5.8),(4.8,-7.2))):
        if film_id==2:
            x *= 1.6
        scene.add("petal_lantern_"+str(j),Lantern(at=(x,.28,z),size=.14,seed=740+j,lit=0,variant="cup"))


def build(film_id):
    if film_id not in (1,2,4):
        raise ValueError("dancers builds films 1, 2 and 4")
    def setup(scene):
        _environment(scene,film_id)
        if film_id==4:
            body=_body("script",(0,0,.25),points=84000,palette=("#b8c6dc","#e6d8c1"))
            body.add(scene,"calligrapher",mask=dict(strength=.25,grow=0))
            scene.add("living_calligraphy",Calligraphy(body))
            return
        spec = [((0,0,.25),0,0,82000,("#bea9e0","#e9c6d3"))] if film_id==1 else [
            ((-3.0,0,-1.7),0,.42,34000,("#d0b2de","#edc9d8")),
            ((-1.5,0,-.8),1,.20,40000,("#a7bddb","#e6d2db")),
            ((0,0,.05),2,0,66000,("#dec4a3","#f0d5c9")),
            ((1.5,0,-.8),3,.32,40000,("#b8acd9","#e1c9e5")),
            ((3.0,0,-1.7),4,.60,34000,("#a8c7c9","#e0d7c8"))]
        grips=[]
        for at,role,delay,points,palette in spec:
            body=_body("solo" if film_id==1 else "ensemble",at,role,delay,points,palette)
            body.add(scene,"fan_performer_"+str(role),mask=dict(strength=.25,grow=0))
            for side in ("R","L"):
                color=("#bf8ece" if side=="R" else "#e1b6c9") if film_id==1 else ("#bc8fca","#a5bedb","#e8c68d","#b3a2db","#a5c8c5")[role]
                prop=SilkOnly(body,side=side,duration=20,color=color,
                     radius=.46 if film_id==1 else .43,spread=160,length=.75 if side=="R" else .55,
                     rows=21,cols=11,ribs=23,point_count=6500,alpha=.20,
                     seed=190+role*13+(side=="L"),fan_tilt=-5,
                     cache_dir=ROOT/"work/cinematic-ten/cloth-cache",
                     wind=(.18,.07,-.08),normal_drag=7.0,iterations=6)
                scene.add("pleated_fan_"+str(role)+side,PleatedFan(prop,color,edge="#ecc4de",seed=role*19+(side=="R")))
                if film_id==1:
                    prop.prebake()
                    scene.add("finite_silk_"+side,prop)
                grips.append(prop)
        scene.add("fan_petal_wake",PetalWake(grips,seed=381+film_id))
    if film_id==1:
        camera=Rig([
            dolly((.5,1.60,4.9),(-.35,1.65,4.6),0,6.3,look=(-.18,1.06,.10),fov=37,ease="smooth",blend=0),
            orbit((-.05,1.03,.0),radius=4.8,height=1.75,a0=-5,a1=28,t0=6.3,t1=14.0,look=(-.04,1.13,.05),fov=38,blend=1.5),
            dolly((2.25,1.75,4.24),(.7,2.30,6.15),14,20,look=[(0,1.15,.15),(0,1.50,-.3)],fov=38,ease="smooth",blend=1.6)],blend=1.5,aperture=.006,shutter=.35,near=.1)
    elif film_id==2:
        camera=Rig([
            dolly((-.65,2.0,7.5),(.4,2.1,6.9),0,7,look=(0,1.05,-.8),fov=40,ease="smooth",blend=0),
            orbit((0,1.0,-.65),radius=7.3,height=(2.1,3.0),a0=3,a1=-20,t0=7,t1=14,look=(0,1.0,-.6),fov=40,blend=1.7),
            dolly((-2.5,3.0,6.3),(0,4.3,8.5),14,20,look=[(0,1.0,-.6),(0,1.2,-.7)],fov=40,ease="smooth",blend=1.8)],blend=1.7,aperture=.005,shutter=.36,near=.1)
    else:
        camera=Rig([
            dolly((1.3,1.65,5.0),(-.45,1.7,4.8),0,7,look=(-.10,1.15,.0),fov=38,ease="smooth",blend=0),
            orbit((0,1.2,0),radius=5.1,height=(1.7,2.15),a0=-5,a1=20,t0=7,t1=14,look=(0,1.48,-.2),fov=40,blend=1.7),
            dolly((1.74,2.15,4.79),(.4,2.6,6.25),14,20,look=[(0,1.48,-.4),(0,1.73,-.7)],fov=40,ease="smooth",blend=1.6)],blend=1.5,aperture=.006,shutter=.35,near=.1)
    world=dict(look="night",sky_top="#030719",sky_mid="#111d37",sky_hor="#594563",
       sun_int=.10,sun_el=-6,sun_az=175,sun_glow=.35,sun_disc=0,
       stars=.32,milky=.18,clouds=.09,haze=.055,mist=.024,mist_height=.18,
       water="#060c20",mirror=.86,mirror_min=.25,ripple=.13,
       dust=.014,bokeh=.005,lanterns=0,floats=.025,hills=1,hill_height=.62,
       exposure=.97,keep_hue=.64,dust_field=dict(n=420,n_bokeh=8),
       float_field=dict(count=64,center=(0,-12),radius=(9,60)),lights=[])
    if film_id==2:
        world.update(sky_top="#081327",sky_mid="#283555",sky_hor="#b58a97",sun_int=.22,sun_el=1,sun_az=-40,sun_glow=.43,stars=.20,milky=.10,water="#151a30",clouds=.15)
    if film_id==4:
        world.update(sky_top="#020916",sky_mid="#0a2638",sky_hor="#3b687a",sun_int=.07,stars=.26,milky=.15,water="#031321",hills=1,hill_height=.46)
    return dict(camera=camera,setup=setup,world=world,motion_samples=2,bokeh_max=.025)
