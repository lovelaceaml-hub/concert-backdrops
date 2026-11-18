"""Centered opening and campaign end card matching the owner's screenshots."""
import numpy as np
import titles
from PIL import Image, ImageDraw


class Cards(titles.Titles):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.veil_program = self.ctx.program(vertex_shader=titles.FULL_VS, fragment_shader='''
        #version 330
        in vec2 vUV; out vec4 o; uniform float uK;
        void main(){
          vec2 q = vec2((vUV.x-.5)/.44, (1.-vUV.y-.25)/.34);
          float m = exp(-pow(abs(q.x),6.)-pow(abs(q.y),6.));
          o = vec4(0.,0.,0.,uK*m);
        }
        ''')
        self.veil_quad = self.ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1], 'f4').tobytes())
        self.veil_vao = self.ctx.vertex_array(self.veil_program, [(self.veil_quad,'2f','aPos')])

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
            self.R.f_out.use()
            self.ctx.enable(self.mgl.BLEND)
            self.ctx.blend_func = self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA
            self.veil_program['uFlip'].value = -1
            self.veil_program['uK'].value = float((.12+.5*np.exp(-((t-6.45)/.65)**2))*(1-progress))
            self.veil_vao.render(self.mgl.TRIANGLE_STRIP)
        drew = super().overlay(t)
        ea, _ = self._ec_state(t)
        if ea > .002:
            if not hasattr(self, 'hearts'):
                self.hearts = []
                theta = np.linspace(0, 2*np.pi, 160)
                x = 16*np.sin(theta)**3
                y = 13*np.cos(theta)-5*np.cos(2*theta)-2*np.cos(3*theta)-np.cos(4*theta)
                points = list(zip(32+x*1.7, 30-y*1.7))
                for color in ['#f6a2d5', '#9dbff2', '#c0a4ec', '#f5ce86']:
                    im = Image.new('RGBA', (64, 64))
                    ImageDraw.Draw(im).polygon(points, fill=color)
                    rgba = np.asarray(im, np.float32)/255
                    rgba[..., :3] *= rgba[..., 3:]
                    self.hearts.append(self._tex(rgba))
            self.ctx.enable(self.mgl.BLEND)
            self.ctx.blend_func = self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA
            age = t-58.5
            for j in range(18):
                x = (.025+.03*(j%4)) if j%2 == 0 else (.86+.029*(j%4))
                x += .009*np.sin(age*.5+j)
                y = .14+(j//2)*.097-.012*age
                size = .012+.003*(j%3)
                layer = dict(tex=self.hearts[j%4], rect=(x,y,size,size*self.w/self.h))
                self._quad(self.p_ovl,self.v_ovl,layer,-1,uAlpha=float(ea*.65),
                           uDis=(-1.,0.,0.,0.))
            self.ctx.disable(self.mgl.BLEND)
        return drew
