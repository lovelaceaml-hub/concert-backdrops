"""Only the requested expression symbols and world-to-logo addition."""
import numpy as np
from p3d import brand as B
from p3d.camera import Rig, hold


def ease(a, b, t):
    x = np.clip((t-a)/(b-a), 0, 1)
    return x*x*(3-2*x)


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
        if not 49.7 < t < 52.65:
            return None
        rows = []
        for i, (name, shape) in enumerate(self.shapes):
            a = 2*np.pi*i/9 + .28*(t-49.7)
            center = np.array([4.7*np.cos(a), 2.6+3.65*np.sin(a), .3])
            xy = shape['xy']*.85
            pos = center + np.column_stack([xy, np.zeros(len(xy))])
            alpha = ease(49.7+.06*i, 50.55+.06*i, t)
            alpha *= 1-ease(52.15, 52.65, t)
            lit = np.clip((t-49.7-.06*i)/.8-shape['order']*.45, 0, 1)
            rows.append(dict(pos=pos, size=.025, color=B.show(B.EXPRESSION_COLORS[name]),
                             alpha=alpha*lit, paint=.8, paint_light=.1, emit=.35,
                             kind='soft', reflect=False, fog=False, dof=False, streak=False))
        return rows


def install(film):
    original_setup = film.P3D['setup']
    camera = film.CAMERA
    virtual = Rig([hold(t0=0, t1=62, pos=(0, 0, 20), target=(0, 0, 0))],
                  min_height=None, fov=50)
    finale = B.Finale(pos=(0, 2.6, 0), radius=2.9, camera=virtual, look='day',
                      t_world=49.55, spin=6, front=-40, shrink=.52,
                      hearts=False,
                      t_settle=(50.4, 51.2), t_logo=(51.0, 52.1), bloom=False,
                      end=dict(t=(52.0, 52.5), ride=(.5, .8542, 20), frac=.148),
                      logo=dict(reflect=False), n=50000)

    def setup(scene):
        original_setup(scene)
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

    film.P3D = dict(film.P3D, setup=setup)
    return finale
