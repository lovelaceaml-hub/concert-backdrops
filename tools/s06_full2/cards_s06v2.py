"""Song 06 backdrop v2: the opening lockup and the concert signature (engine/titles.py type, glow and protection).

Opening (DESIGN-SYSTEM 7, PHASEB 16), whole from frame 0 and held: the campaign logo (brand.py) above, the small
label HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (the second line in italic), and the song
title large. Warm white with gold accents on the harvest evening sky.

Signature, the same block in all 11 songs, small in the TOP LEFT from the end of the opening to the last frame:
a small logo mark, the song title, "The Words of Mother's Love That Bring Peace", "DEC 6 · 4:30 PM" (the
brightest line, capitals about 24 px tall at 1080p) and "HEALING CONCERT · LAS VEGAS". It never flashes: one
window, faded in once.

No em dash or en dash anywhere in this file.
"""
import numpy as np
from PIL import Image, ImageDraw

import titles

SONG_TITLE = "Heavenly Mother Tells Us to Be Grains"
SONG_LINES = ("Heavenly Mother Tells Us", "to Be Grains")
CONCERT_LINES = ("The Words of Mother’s Love", "That Bring Peace")
SIG_BOX = {}          # the signature's box in 1080p pixels (x0, y0, x1, y1), for the checks


class SongCards(titles.Titles):
    def __init__(self, renderer):
        super().__init__(renderer)
        # a very soft warm veil behind the opening so the cream letters read on the evening sky (never dark)
        self.veil_program = self.ctx.program(vertex_shader=titles.FULL_VS, fragment_shader='''
        #version 330
        in vec2 vUV; out vec4 o; uniform float uK;
        void main(){
          vec2 q = vec2((vUV.x-.5)/.40, (1.-vUV.y-.36)/.33);
          float m = exp(-pow(abs(q.x),6.)-pow(abs(q.y),6.));
          o = vec4(.10*uK*m,.05*uK*m,.03*uK*m,uK*m);
        }
        ''')
        self.veil_quad = self.ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], 'f4').tobytes())
        self.veil_vao = self.ctx.vertex_array(self.veil_program, [(self.veil_quad, '2f', 'aPos')])

    def _opening(self, pal):
        s, W, H = self.s, self.w, self.h
        P = titles.PALETTES[pal]
        col, acc = P["col"], P["acc"]
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        cx = W / 2.0
        lh = 104.0
        total = lh + 22 + 44 + 58 + 84 + 26 + 96 + 96
        top = self.op["y"] * H - total * s / 2.0
        lg = self._logo("opening", lh * s, pal)
        self.op_logo = None
        if lg is not None:
            im, ox, oy, lw = lg
            bx, by = cx - lw / 2.0, top + lh * s - (im.height - 2 * oy)
            L.alpha_composite(im, (int(round(bx - ox)), int(round(by - oy))))
            self.op_logo = (int(round(bx - ox)), int(round(by - oy)), im.width, im.height)
        y = top + (lh + 22) * s
        titles._tracked(d, (cx, y), "HEALING CONCERT", titles.JO(500, 30 * s), acc + (255,), 9 * s)
        y += 44 * s
        d.text((cx, y), CONCERT_LINES[0], font=titles.CG(500, 58 * s), fill=col + (255,), anchor="ma")
        y += 58 * s
        d.text((cx, y), CONCERT_LINES[1], font=titles.CG(500, 52 * s, it=True), fill=col + (255,), anchor="ma")
        y += 84 * s
        d.line((cx - 70 * s, y, cx + 70 * s, y), fill=acc + (210,), width=max(1, int(round(2 * s))))
        y += 26 * s
        d.text((cx, y), SONG_LINES[0], font=titles.CG(600, 96 * s), fill=col + (255,), anchor="ma")
        y += 96 * s
        d.text((cx, y), SONG_LINES[1], font=titles.CG(600, 96 * s), fill=col + (255,), anchor="ma")
        return self._finish(L, 14, 0.55, pal, noise=True, prot=(40.0, 16.0))

    def _signature(self, corner, pal):
        """Top left: the logo mark, then four lines aligned left beside it."""
        s, W, H = self.s, self.w, self.h
        P = titles.PALETTES[pal]
        col, acc = P["col"], P["acc"]
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        mx, my = 62 * s, 50 * s
        blk = 140.0 * s
        lg = self._logo("signature", 92 * s, pal)
        gap = 20 * s
        if lg is not None:
            im, ox, oy, lw = lg
            lhh = im.height - 2 * oy
            L.alpha_composite(im, (int(round(mx - ox)), int(round(my + (blk - lhh) / 2.0 - oy))))
            gap = lw + 20 * s
        tx = mx + gap
        y = my - 4 * s
        d.text((tx, y), SONG_TITLE, font=titles.CG(600, 32 * s, it=True), fill=col + (245,), anchor="la")
        d.text((tx, y + 38 * s), titles.CONCERT, font=titles.CG(500, 25 * s), fill=col + (225,), anchor="la")
        titles._tracked(d, (tx, y + 72 * s), "DEC 6" + titles.SEP + "4:30 PM", titles.JO(600, 34 * s),
                        (255, 252, 244, 255), 4 * s, align="left")
        titles._tracked(d, (tx, y + 116 * s), "HEALING CONCERT" + titles.SEP + "LAS VEGAS", titles.JO(500, 19 * s),
                        acc + (240,), 4 * s, align="left")
        a = np.asarray(L)[..., 3]
        ys, xs = np.nonzero(a > 8)
        if len(xs):
            SIG_BOX.update(box=(xs.min() / s, ys.min() / s, xs.max() / s, ys.max() / s))
        return self._finish(L, 9, 0.5, pal, prot=(36.0, 14.0))

    def overlay(self, t):
        a, front, progress = self._op_state(t)
        if a > 0 and progress < 1:
            self.R.f_out.use()
            self.ctx.enable(self.mgl.BLEND)
            self.ctx.blend_func = self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA
            self.veil_program['uK'].value = float(0.22 * (1 - progress))
            self.veil_vao.render(self.mgl.TRIANGLE_STRIP)
        return super().overlay(t)
