"""Requested cards over the unaltered Film 10 picture."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import titles
from p3d import brand


class Cards(titles.Titles):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.intros = [self.build_intro(False), self.build_intro(True)]

    def _signature(self, corner, pal):
        scale = self.s
        try:
            self.s *= .65
            return super()._signature(corner, pal)
        finally:
            self.s = scale

    def build_intro(self, day):
        s = self.s
        layer = Image.new('RGBA', (self.w, self.h))
        d = ImageDraw.Draw(layer)
        white = (31, 42, 87, 255) if day else (255, 246, 232, 255)
        gold = (137, 90, 29, 255) if day else (247, 219, 164, 255)
        cx = self.w*.55
        def line(y, value, font, color):
            d.text((cx, y*s), value, font=font, anchor='mt', fill=color)
        line(26, 'HEALING CONCERT', titles.JO(500, 24*s), gold)
        line(57, "The Words of Mother's Love", titles.CG(500, 65*s), white)
        line(123, 'That Bring Peace', titles.CG(500, 50*s, it=True), white)
        line(183, 'SUNDAY, DECEMBER 6  ·  4:30 PM', titles.JO(500, 30*s), white)
        line(223, 'LAS VEGAS', titles.JO(500, 20*s), gold)
        mask = layer.getchannel('A').filter(ImageFilter.GaussianBlur(4*s))
        shadow = Image.new('RGBA', layer.size, (255, 249, 239, 0) if day else (12, 18, 35, 0))
        shadow.putalpha(mask.point(lambda v: round(v*.7)))
        shadow.alpha_composite(layer)
        layer = shadow
        logo = brand.logo_image(round(115*s), pad=.02, glow=0)
        layer.alpha_composite(logo, (round(490*s), round(68*s)))
        arr = np.asarray(layer, np.float32)/255
        arr[..., :3] *= arr[..., 3:4]
        return dict(tex=self._tex(arr), rect=(0, 0, 1, 1))

    def overlay(self, t):
        drew = super().overlay(t)
        if t < 7.2:
            a = 1-float(titles._ss(7.0, 7.2, t))
            self.R.f_out.use()
            self.ctx.enable(self.mgl.BLEND)
            self.ctx.blend_func = self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA
            raw = np.frombuffer(self.R.base_frame, np.uint8).reshape(self.h, self.w, 3)
            region = raw[:int(.25*self.h):16, int(.25*self.w):int(.8*self.w):16]
            day = float(titles._ss(.30, .68, region.mean()/255))
            for layer, weight in zip(self.intros, (1-day, day)):
                if weight > .001:
                    self._quad(self.p_ovl, self.v_ovl, layer, -1,
                               uAlpha=a*weight, uDis=(-1, 0, 0, 0))
            self.ctx.disable(self.mgl.BLEND)
            drew = True
        return drew
