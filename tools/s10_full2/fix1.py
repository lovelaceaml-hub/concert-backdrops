"""Song 10 backdrop version 2, fix 1 (the coordinator's notes on "10 backdrop v2 stills.jpg"), applied at load
by tools/s10_full2/render.py. Nothing in the engine snapshot is edited: its shader text is changed in memory
before the programs are built.

1. Bottom third calm (Never 9): the lake's mirror fades out below about two thirds of the frame height, so
   the lamp's gold column, the lamp's pool of light and the low lantern and star images no longer reach
   down to the bottom edge. Three places: the lake itself (sky mirror, sun glint, the light pools on the
   water, the shafts' image), mirrored point sprites and mirrored segments. Above the line nothing changes.
2. Reading boxes (Never 3) are fixed in s10v2_song.py (the medium shots frame the people lower and a little
   smaller, so their heads stay clearly below the words).
3. Speed only (no change to any picture): the touching pairs ask each other's bodies for their pose at many
   times per frame and the actor's 64-entry pose cache thrashed (about 40 s a frame in an embrace). The
   cache is made larger; the poses it returns are the same.

No em dash or en dash anywhere in this file.
"""

# screen height in normalised device units (y up, -1 bottom edge, +1 top edge): the mirror is whole above
# -0.20 (0.60 of the height from the top) and gone below -0.40 (0.70 from the top)
FADE = (-0.40, -0.20)
KEEP = 0.06            # what is left of the mirror in the bottom third (the water stays water, never a hole)


def _sub(text, old, new):
    assert text.count(old) == 1, f'shader text not found once: {old[:60]}'
    return text.replace(old, new)


def patch_shaders(K):
    a, b = FADE
    fade = f'smoothstep({a:.3f}, {b:.3f}, %s)'
    # mirrored point sprites
    old = '  vCol = uPaint > 0.5 ? vec4(aColor, col.r) : vec4(col, glint);'
    K.SPRITE_VS = _sub(K.SPRITE_VS, old, '  if(uMirror > 0.5) col *= ' + fade % 'ndc.y' + ';\n' + old)
    # mirrored segments (lines, ribbons)
    old = '  float h = R + 3.0*S;\n'
    K.SEG_VS = _sub(K.SEG_VS, old, '  if(uMirror > 0.5) b *= ' + fade % '(first ? s1 : s2).y*2.0/uRes.y' + ';\n'
                    + old)
    # the lake: its mirror, the sun's glint, the pools of moving lights and of the shafts
    old = '  vec2 ndc = vUV*2.0-1.0;\n'
    K.BG_FS = _sub(K.BG_FS, old, old + '  float mb = mix(%.3f, 1.0, ' % KEEP + fade % 'ndc.y' + ');\n')
    old = '*lk.y;\n    col = mix(uWater, c, fres);'
    K.BG_FS = _sub(K.BG_FS, old, '*lk.y*mb;\n    col = mix(uWater, c, fres);')
    old = '      col += uLightC[i]*0.35*r*r/(dot(q, q) + r*r);'
    K.BG_FS = _sub(K.BG_FS, old, '      col += uLightC[i]*0.35*r*r/(dot(q, q) + r*r)*mb;')
    old = '      I += 1.6*exp(-dot(q, q)/(uShA[i].z*uShA[i].z));'
    K.BG_FS = _sub(K.BG_FS, old, '      I += 1.6*exp(-dot(q, q)/(uShA[i].z*uShA[i].z))*mb;')


class _Cache(dict):
    """The actor's pose cache, reporting a sixteenth of its size so that its 64-entry limit holds about 1000."""

    def __len__(self):
        return super().__len__() // 16


def patch_actor(Actor):
    init = Actor.__init__

    def __init__(self, *a, **k):
        init(self, *a, **k)
        self._cache = _Cache(self._cache)

    Actor.__init__ = __init__


def apply():
    from p3d import shaders
    from nine_reference_p3d import actor
    patch_shaders(shaders)
    patch_actor(actor.Actor)
