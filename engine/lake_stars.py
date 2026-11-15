"""Stars mirrored in the lake (optional): a night lake as a still mirror, a sea of stars.

A song switches it on with `LAKE_STARS` (a number or a Track, 0 = off; 1 = as bright as the stars above). Songs
without the key never load this module, so they render exactly as before.

The engine's own stars (render.py, the same buffer and the same twinkle) are drawn a second time, mirrored at the
water line with the same squeeze the composite uses when it mirrors the sky in the lake (1.22), a little dimmer
toward the bottom of the screen, breathing sideways with the water. They are light in the glow layer like the
stars above. BOTTOM_CALM dims them in the lower third as it dims every other light there, so a song that wants
the mirror lowers BOTTOM_CALM for its night (a Track). With a camera move they follow the lake.
How a song uses it: engine/UPGRADE-HOWTO.md, section U.
"""
import moderngl

import song as S
import shaders as G
import sky_camera as SKC

VS = """
#version 330
in vec2 aPos; in vec2 aSeed;
uniform float uT, uStars, uHi, uPx, uHorizon, uAmt, uCalm, uCalmY;
out float vA; out float vK;
void main(){
  float tw = 0.62+0.38*sin(uT*(0.7+2.6*aSeed.x)+aSeed.y*60.0);
  float sp = pow(0.5+0.5*sin(uT*(1.5+4.0*aSeed.y)+aSeed.x*90.0), 6.0)*uHi;
  float b = aSeed.x*aSeed.x*aSeed.x;
  float y = uHorizon-(aPos.y-uHorizon)/1.22;              // the lake's mirror, as the composite mirrors the sky
  float d = clamp((uHorizon-y)/uHorizon, 0.0, 1.0);       // 0 at the far shore, 1 at the bottom of the screen
  float x = aPos.x + 0.0014*sin(uT*0.9+aPos.y*140.0+aSeed.y*20.0)*(0.3+d);   // the water breathes
  float calm = 1.0-0.75*uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y));
  vA = uStars*uAmt*(0.16+0.84*b)*(tw+0.8*sp)*smoothstep(0.44,0.62,aPos.y)*(1.0-0.40*d)*calm
       *smoothstep(0.0, 0.012, uHorizon-y);
  vK = aSeed.y;
  gl_Position = vec4(vec2(x,y)*2.0-1.0,0.0,1.0);
  gl_PointSize = (1.7+4.2*b)*uPx;
}
"""


def _val(name, t, default):
    v = getattr(S, name, None)
    if v is None:
        return default
    return v(t) if callable(v) else v


class LakeStars:
    def __init__(self, R, stars):
        """R: the renderer. stars: its star array (n x 4: x, y, two seeds), the one the sky's stars are drawn from."""
        self.R = R
        ctx = R.ctx
        self.prog = ctx.program(vertex_shader=SKC.cam_vs(VS), fragment_shader=G.STAR_FS)
        self.vao = ctx.vertex_array(self.prog, [(ctx.buffer(stars.tobytes()), "2f 2f", "aPos", "aSeed")])

    def draw(self, t, P, calm):
        amt = float(_val("LAKE_STARS", t, 0.0) or 0.0)
        if amt <= 0.001 or P["stars"] <= 0.001:
            return
        p = self.prog
        vals = dict(uT=float(t), uStars=float(P["stars"]), uHi=float(P["hi"]), uPx=float(self.R.px),
                    uHorizon=float(S.HORIZON), uAmt=amt, uCalm=float(calm), uCalmY=0.335)
        sky = getattr(self.R, "sky", None)
        if sky is not None and "uCamAff" in p:
            # the mirror lies on the water: it moves with the middle of the lake
            vals["uCamAff"] = sky.aff(sky.ground_depth(float(S.HORIZON) * 0.5))
        for k, v in vals.items():
            if k in p:
                p[k].value = v
        self.vao.render(moderngl.POINTS)
