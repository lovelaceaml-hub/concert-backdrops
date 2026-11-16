"""Only the requested expression symbols and world-to-logo addition."""
import numpy as np
from p3d import brand as B
from p3d.camera import Rig, hold
from respect import Gate, ListeningLight


def ease(a, b, t):
    x = np.clip((t-a)/(b-a), 0, 1)
    return x*x*(3-2*x)


class OpeningRig(Rig):
    """Lower the opening light below the card; rejoin the original camera."""

    def __init__(self, original):
        self.__dict__.update(original.__dict__)

    def state(self, t, aspect=16.0/9.0):
        cam = super().state(t, aspect)
        if t < 1.4:
            cam.target[1] += 1.5*(1-ease(.45, 1.4, t))
        return cam


class CameraAttached:
    """Place the added brand scene in the original view without moving its camera."""
    wants_camera = True

    def __init__(self, inner, original, virtual, fade_out=None):
        self.inner, self.original, self.virtual = inner, original, virtual
        self.fade_out = fade_out

    def sample(self, t, cam):
        gain = 1-ease(*self.fade_out, t) if self.fade_out else 1
        if gain <= 0:
            return None
        batch = self.inner.sample(t, self.virtual.state(t))
        if batch is None:
            return None
        right, up, forward = cam.basis()
        center = np.asarray(cam.pos) + 20*forward
        scale = np.tan(np.radians(cam.fov/2))/np.tan(np.radians(25))
        rot = np.stack([right, up, -forward], axis=0)
        result = []
        for b in batch if isinstance(batch, (list, tuple)) else [batch]:
            if b is None:
                continue
            b = dict(b)
            b['alpha'] = np.asarray(b.get('alpha', 1))*gain
            for key in ('pos', 'pos2'):
                if key in b:
                    b[key] = center + scale*np.asarray(b[key])@rot
            for key in ('size', 'size2'):
                if key in b:
                    b[key] = scale*np.asarray(b[key])
            for key in ('normal', 'vel'):
                if key in b:
                    b[key] = np.asarray(b[key])@rot
            b.update(reflect=False, fog=False, dof=False, streak=False)
            result.append(b)
        return result


class SymbolRing:
    wants_camera = True

    def __init__(self):
        self.shapes = [(name, B.symbol_points(name, n=650)) for name in B.LABELS]

    def sample(self, t, cam=None):
        if not 49.35 < t < 52.4:
            return None
        rows = []
        for i, (name, shape) in enumerate(self.shapes):
            a = 2*np.pi*i/9 + .48*(t-49.35)
            center = np.array([5.25*np.cos(a), .2+3.8*np.sin(a), .8])
            xy = shape['xy']*1.05
            pos = center + np.column_stack([xy, np.zeros(len(xy))])
            alpha = ease(49.35+.035*i, 49.95+.035*i, t)
            alpha *= 1-ease(51.7, 52.4, t)
            lit = np.clip((t-49.35-.035*i)/.55-shape['order']*.4, 0, 1)
            color = B.lin(B.EXPRESSION_COLORS[name])
            rows.append(dict(pos=pos, size=.037, color=color*1.15,
                             alpha=alpha*lit*.8, paint=0, emit=1.2,
                             kind='soft', reflect=False, fog=False, dof=False, streak=False))
            angles = a-np.linspace(0, .7, 240)
            trail = np.column_stack([5.25*np.cos(angles), .2+3.8*np.sin(angles),
                                     np.full(len(angles), .7)])
            rows.append(dict(pos=trail, size=.028, color=color,
                             alpha=alpha*np.linspace(.35, 0, len(angles)), kind='soft',
                             emit=.7, reflect=False, fog=False, dof=False, streak=False))
        return rows


def install(film):
    original_setup = film.P3D['setup']
    camera = film.CAMERA
    virtual = Rig([hold(t0=0, t1=66, pos=(0, 0, 20), target=(0, 0, 0))],
                  min_height=None, fov=50)
    finale = B.Finale(pos=(0, .2, 0), radius=3.3, camera=virtual, look='night',
                      t_world=49.35, spin=9, front=-110, shrink=.86,
                      hearts=False,
                      t_settle=(50.8, 51.4), t_logo=(51.35, 52.35), bloom=False,
                      end=dict(t=(52.35, 52.7), ride=(.5, .8542, 20), frac=.148),
                      logo=dict(reflect=False), n=50000)

    def setup(scene):
        original_setup(scene)
        scene.remove('speaker')
        scene.remove('listener')
        for name in ('comets', 'lanterns', '_lanterns'):
            # Keep the original draw order and reflection/LOD flags. Calling
            # Scene.add here would append this existing entry to the end.
            entry = next(e for e in scene.entries() if e.name == name)
            entry.pointset = Gate(entry.pointset)
        # The original arch is obscured by the new globe chapter; the card's
        # moving pastel world supplies its own mountains and drifting hearts.
        scene.remove('_arch')
        scene.add('addition listening light', CameraAttached(ListeningLight(), camera, virtual), reflect=False)
        for i, word in enumerate(film.WORDS):
            x = .13 if i % 2 == 0 else .87
            symbol = B.Traced(word.name, camera=camera, ride=(x, .48, 20),
                              face='screen', frac=.065, t0=word.t_read0,
                              dur=.75, hold=max(.5, word.t_read1-word.t_read0-1.1),
                              out=.5, intensity=.32, n=600, dof=False, reflect=False)
            scene.add('addition symbol '+word.name, symbol, reflect=False)
        for name, obj in [('world', finale.globe), ('logo', finale.logo), ('symbol ring', SymbolRing())]:
            scene.add('addition '+name, CameraAttached(obj, camera, virtual,
                      fade_out=(52.5, 53.0) if name == 'logo' else None), reflect=False)

    world = dict(film.P3D['world'])
    looks = dict(world['looks'])
    looks['listening'] = dict(base='night', sky_top='#050719', sky_mid='#151238',
                              sky_hor='#302649', stars=.85, milky=.5, mist=.12,
                              mist_color='#322448', haze=.12, lanterns=0)
    looks['globe_chapter'] = dict(base='night', sky_top='#03091c', sky_mid='#0c2051',
                                  sky_hor='#27234a', stars=1.0, milky=.8,
                                  sun_int=0, sun_glow=0, mist=.08, haze=.1)
    looks['pastel_card'] = dict(base='day', sky_top='#9bdbf6', sky_mid='#efcfeb',
                                sky_hor='#ffd9b6', sun_int=.3, sun_glow=.3,
                                hill_color='#e7afaa', mist=.14, haze=.14, stars=.2)
    look_keys = []
    for key in world['look']:
        if abs(key[0]-33.36) < .001:
            look_keys.append((key[0], 'listening', .65))
        elif abs(key[0]-49.47) < .001:
            look_keys.append((key[0], 'globe_chapter', .5))
        else:
            look_keys.append(key)
    look_keys.append((52.0, 'pastel_card', .8))
    world.update(looks=looks, look=look_keys)
    bursts = [dict(b) for b in film.P3D['bursts']]
    for burst in bursts:
        if abs(burst['t']-.25) < .001:
            burst.update(strength=.25)
        elif abs(burst['t']-33.36) < .001:
            burst.update(strength=.35)
        elif abs(burst['t']-49.47) < .001:
            burst.update(strength=.18, rise=.4, fall=.55)
    film.P3D = dict(film.P3D, setup=setup, camera=OpeningRig(camera), world=world, bursts=bursts)
    return finale
