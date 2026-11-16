"""Claude Final v1 typography, on this film's original expression clock."""
import reference  # noqa: F401
from nine_reference_p3d import words as PW


def install(film):
    specs = []
    widths = [.30, .40, .60, .48, .41, .44, .58, .45, .51]
    for source, frac in zip(film._SPECS, widths):
        spec = dict(source)
        for key in ('pos', 'source', 'to'):
            spec.pop(key, None)
        middle = .5*(spec['t_read0']+spec['t_read1'])
        spec.update(ride=(.5, .625, 7), face='screen',
                    width=film._width(middle, 7, frac), pill=True,
                    arrive='pen', nib=False, leave='fade')
        spec['t_out'] = spec['t_read1']+.25
        specs.append(spec)
    specs[2].update(t_read1=16.85, t_out=16.95)
    specs[5].update(t_read1=30.15, t_out=30.3)
    specs[6].update(t_in=30.3, t_read0=30.75)

    def clean_leave(t, info):
        if info['state'] == 'leave':
            return dict(pos=info['home'], assist=1.0)

    film.PW = PW
    film.WORDS = PW.Words(specs, camera=film._LAYOUT, reflect=False, drive=clean_leave)
    return film.WORDS


class Clear:
    """Dim the light inside reading bounds, including long ribbon segments."""
    wants_camera = True

    def __init__(self, inner, words):
        self.inner, self.words = inner, words

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, 'gain') else 1

    def sample(self, t, cam):
        import numpy as np
        got = self.inner.sample(t, cam) if getattr(self.inner, 'wants_camera', False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = []
        for word in self.words:
            if word.t_in <= t <= word.t_out:
                x0, x1, y0, y1, front, *_ = PW.screen_box(word, cam, t)
                if front:
                    boxes.append((x0-.02, x1+.02, y0-.035, y1+.035))
        out = []
        for source in got if isinstance(got, (list, tuple)) else [got]:
            if source is None:
                continue
            b = dict(source)
            if t >= 47.8:
                # A ribbon straddling the lens projects into a large triangle.
                # Keep the continuous trail, but fade its near-plane segments.
                p = np.asarray(b['pos']).reshape(-1,3)
                forward = cam.basis()[2]
                depth = (p-np.asarray(cam.pos))@forward
                if b.get('pos2') is not None:
                    depth = np.minimum(depth,(np.asarray(b['pos2'])-cam.pos)@forward)
                u = np.clip((depth-1.0)/3.0,0,1)
                transition = np.clip((t-47.8)/.8,0,1)
                transition = transition*transition*(3-2*transition)
                close = 1-transition*(1-u*u*(3-2*u))
                b['alpha'] = np.asarray(b.get('alpha',1))*close
                if 'alpha2' in b:
                    b['alpha2'] = np.asarray(b['alpha2'])*close
                b['streak'] = np.asarray(b.get('streak',1))*(1-transition)
            if boxes:
                p = np.asarray(b['pos']).reshape(-1, 3)
                xy, z = cam.project(p)
                gain = np.ones(len(p))
                end = None
                if b.get('pos2') is not None:
                    end, _ = cam.project(np.asarray(b['pos2']).reshape(-1, 3))
                for u in np.linspace(0, 1, 9) if end is not None else [0]:
                    q = xy if end is None else xy*(1-u)+end*u
                    for x0,x1,y0,y1 in boxes:
                        dx = np.minimum(q[:,0]-x0, x1-q[:,0])
                        dy = np.minimum(q[:,1]-y0, y1-q[:,1])
                        f = np.clip(np.minimum(dx,dy)/.02+.5, 0, 1)
                        gain = np.minimum(gain, 1-.98*f*(z>0))
                b['alpha'] = np.asarray(b.get('alpha',1))*gain
                if 'alpha2' in b:
                    b['alpha2'] = np.asarray(b['alpha2'])*gain
            out.append(b)
        return out
