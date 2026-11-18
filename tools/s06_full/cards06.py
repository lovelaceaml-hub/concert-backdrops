"""The opening title of the song 06 backdrop and its small signature (engine/titles.py, R3 type and glow).

Opening: HEALING CONCERT small and tracked, the song title "Heavenly Mother Tells Us / to Be Grains" in the
Cormorant serif, a gold hairline and the concert title in italic beneath. Whole from frame 0, held, then it
crumbles into golden dust (the grains). Signature: as Revision 3, small, bottom left, for the rest of the video.
"""
import numpy as np
import titles
from PIL import Image, ImageDraw

SONG_TITLE = ("Heavenly Mother Tells Us", "to Be Grains")


class SongCards(titles.Titles):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.veil_program = self.ctx.program(vertex_shader=titles.FULL_VS, fragment_shader='''
        #version 330
        in vec2 vUV; out vec4 o; uniform float uK;
        void main(){
          vec2 q = vec2((vUV.x-.5)/.42, (1.-vUV.y-.27)/.26);
          float m = exp(-pow(abs(q.x),6.)-pow(abs(q.y),6.));
          o = vec4(0.,0.,0.,uK*m);
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
        total = 330.0
        top = self.op["y"] * H - total * s / 2.0
        titles._tracked(d, (cx, top), "HEALING CONCERT", titles.JO(500, 30 * s), acc + (255,), 9 * s)
        d.text((cx, top + 44 * s), SONG_TITLE[0], font=titles.CG(600, 104 * s), fill=col + (255,), anchor="ma")
        d.text((cx, top + 156 * s), SONG_TITLE[1], font=titles.CG(600, 104 * s), fill=col + (255,), anchor="ma")
        y = top + 290 * s
        d.line((cx - 60 * s, y, cx + 60 * s, y), fill=acc + (200,), width=max(1, int(round(2 * s))))
        d.text((cx, y + 18 * s), titles.CONCERT, font=titles.CG(500, 46 * s, it=True), fill=col + (245,),
               anchor="ma")
        return self._finish(L, 14, 0.55, pal, noise=True, prot=(40.0, 16.0))

    def _signature(self, corner, pal):
        scale = self.s
        try:
            self.s *= .65
            return super()._signature(corner, pal)
        finally:
            self.s = scale

    def overlay(self, t):
        a, front, progress = self._op_state(t)
        if a > 0 and progress < 1:
            # a very soft warm-neutral shade under the opening lockup so the cream letters read on the bright sky
            self.R.f_out.use()
            self.ctx.enable(self.mgl.BLEND)
            self.ctx.blend_func = self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA
            self.veil_program['uK'].value = float(0.26 * (1 - progress))
            self.veil_vao.render(self.mgl.TRIANGLE_STRIP)
        return super().overlay(t)
