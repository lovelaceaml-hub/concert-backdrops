"""Projected environment paintings, animated atmosphere and measured dolly drift."""
from pathlib import Path
import numpy as np
import moderngl
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
VERT='''#version 330
in vec2 pos;out vec2 uv;
void main(){uv=pos*.5+.5;gl_Position=vec4(pos,.999,1);}
'''
FRAG='''#version 330
in vec2 uv;out vec4 frag;
uniform sampler2D plate;
uniform vec2 pan;
uniform float zoom,time,exposure,opacity,sky;
vec3 inverseTone(vec3 c){
 vec3 y=pow(max(c,vec3(0)),vec3(2.2));
 vec3 a=2.51-2.43*y,b=.03-.59*y;
 return (-b+sqrt(b*b+.56*a*y))/(2*a);
}
void main(){
 vec2 q=(uv-.5)/zoom+.5+pan;
 float atmosphere=sky>.5?1.0:smoothstep(.32,.6,q.y)*(1-smoothstep(.55,.78,q.x));
 q.x+=sin(time*.15+q.y*7)*.0012*atmosphere;
 q.y+=sin(time*.11+q.x*9)*.0006*atmosphere;
 vec3 c=texture(plate,q).rgb;
 vec3 radiance=inverseTone(c)/max(exposure,.2);
 frag=vec4(radiance*opacity,opacity);
}
'''

class Environments:
    def __init__(self,ctx):
        self.ctx=ctx;self.prog=ctx.program(vertex_shader=VERT,fragment_shader=FRAG)
        buf=ctx.buffer(np.array([[-1,-1],[1,-1],[-1,1],[1,1]],'f4').tobytes())
        self.vao=ctx.vertex_array(self.prog,[(buf,'2f','pos')]);self.textures={}
        for name in ['garden','reconciliation','cathedral','ascent']:
            path=ROOT/'work/sol3/environments'/f'{name}.png'
            im=Image.open(path).convert('RGB').transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            tex=ctx.texture(im.size,3,im.tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR)
            tex.repeat_x=tex.repeat_y=False;self.textures[name]=tex
    def draw(self,t,film,P):
        j=film.shot_at(t) if film.SHOT is None else film.SHOT
        if t>=49.425:return False
        bounds=[0]+film.CUTS+[62]
        a,b=bounds[j],bounds[j+1]
        u=film.film.sc(a-.35,b+.35,t)
        name='garden' if j in (0,1,2,8) else 'reconciliation' if j in (3,4,5,7) else 'cathedral' if j==6 else 'ascent'
        zoom=1.04+.08*u if j!=10 else 1.08+.23*u
        pan=((u-.5)*(.034 if j%2 else -.034),.003*np.sin(.22*t))
        if j==0:pan=(-.005,-.018);zoom=1.04+.06*u
        if j==10:pan=((u-.5)*.02,-.015+.035*u)
        # The owner's Film 10 reference leads. Paintings are supporting atmosphere.
        weights=[.18,.0,.30,.34,.0,.08,.35,.05,.12,.0,.0,.0]
        opacity=weights[j]
        if j==10:opacity*=1-film.film.sc(44.6,45.5,t)
        self.textures[name].use(0)
        for key,val in dict(plate=0,pan=pan,zoom=zoom,time=t,exposure=float(P['exposure']),opacity=opacity,sky=float(j>=9)).items():
            self.prog[key].value=val
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        return True
