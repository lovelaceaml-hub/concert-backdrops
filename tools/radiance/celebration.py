"""Nine colored fountains frame the closing invitation without covering its type."""
import numpy as np


class Celebration:
    def __init__(self):
        rng = np.random.default_rng(916)
        self.seed = rng.random((3600, 5))
        self.palette = np.array([[234,90,94],[242,178,94],[246,206,70],
            [90,186,90],[98,178,250],[102,122,246],[158,106,246],
            [238,98,166],[54,78,150]], float)/255

    def points(self, t, width, height):
        if t < 54.4:
            return None
        s = self.seed
        # Repeating small fountains build toward a large double fan on the chord.
        launch = 54.4+s[:,0]*5.8
        age = t-launch
        hit = s[:,4] > .55
        launch = np.where(hit, 60.2+s[:,0]*.16, launch)
        age = t-launch
        life = np.where(hit, 2.8, 2.4)
        live = (age > 0) & (age < life)
        age = np.maximum(age, 0)
        side = np.where(s[:,1] < .5, 1., -1.)
        origin = np.where(side > 0, .035, .965)
        # Confine color to the outer sides. The full invitation remains readable.
        x = origin+side*(.025+.105*s[:,2])*np.sin(np.minimum(age/2.5,1)*np.pi/2)
        y = .98-(.38+.27*s[:,3])*age+.11*age**2
        live &= (y > .025) & (y < .99)
        xy = np.stack([x*width,y*height],1)[live]
        alpha = np.clip(age/.13,0,1)*np.clip((life-age)/.7,0,1)*.8
        col = self.palette[np.minimum((s[:,2]*9).astype(int),8)]
        rgba = np.c_[col*alpha[:,None],alpha][live].astype('f4')
        size = ((3.0+5.0*s[:,3])*(width/1920))[live].astype('f4')
        # Large flowing comet arcs carry the film's color into the invitation.
        trail = np.linspace(0, .55, 160)
        arcs, radii, colors = [xy], [size], [rgba]
        for k in range(9):
            phase = .65*(t-54.4)-trail+k*2*np.pi/9
            xx = .5+.49*np.cos(phase)
            yy = .5+.61*np.sin(phase)
            keep = ((xx < .18) | (xx > .82) | (yy < .025) | (yy > .96)) & (yy > 0) & (yy < 1)
            q = np.stack([xx*width,yy*height],1)[keep]
            strength = (1-trail/.55)*min(max((t-54.4)/.6,0),1)
            color = self.palette[k]
            a = strength[keep]*.62
            arcs.append(q)
            radii.append(np.full(len(q), 7*width/1920))
            colors.append(np.c_[np.broadcast_to(color,(len(q),3))*a[:,None],a])
        return np.concatenate(arcs).astype('f4'), np.concatenate(radii).astype('f4'), np.concatenate(colors).astype('f4')
