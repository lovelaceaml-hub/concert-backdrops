"""A native-frame, code-drawn promo design sample using the shared camera API.

Run on a cloud CPU. This is an isolated proposal, not an approved-film revision.
All scene geometry is procedural; the land mask is the existing Natural Earth data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
os.environ.setdefault("LP_NUM_THREADS", "2")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import moderngl
import numpy as np
from PIL import Image

from pipeline.motion import CameraTrack
from tools.promo_design_example.typography import build_overlay
from tools.promo_design_example.world_geometry import sphere_mesh, make_ribbon_paths, star_points
from tools.promo_design_example.symbols import symbol_vertices

VERT = """#version 330
in vec2 in_pos;
out vec2 uv;
void main(){uv=in_pos*.5+.5;gl_Position=vec4(in_pos,0.,1.);}
"""

NOISE = """
float hash(vec3 p){p=fract(p*.3183099+vec3(.1,.2,.3));p*=17.;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
float fbm(vec3 p){float n=0.;float a=.53;for(int i=0;i<5;i++){n+=a*noise(p);p=p*2.03+vec3(4.3,7.1,1.7);a*=.48;}return n;}
"""

SKY = """#version 330
in vec2 uv;out vec4 frag;uniform float u_time;uniform float u_accent;
""" + NOISE + """
void main(){
 vec2 p=uv;float y=p.y;
 vec3 col=mix(vec3(.12,.045,.13),vec3(.022,.016,.065),smoothstep(.19,.95,y));
 float aurora=exp(-pow((y-.48-.12*sin(p.x*3.1))/.24,2.));
 col+=vec3(.12,.028,.09)*aurora;
 vec2 sun=vec2(.77,.43);float d=length((p-sun)*vec2(1.5,1.));
 col+=vec3(.26,.13,.045)*exp(-d*d*9.);
 float cloud=fbm(vec3(p*vec2(4.8,7.5)+vec2(u_time*.006,0.),1.8));
 float fine=fbm(vec3(p*vec2(13.,22.)-vec2(u_time*.009,0.),6.1));
 float band=exp(-pow((y-.18)/.19,2.));
 float density=smoothstep(.31,.72,cloud+.17*fine)*band;
 vec3 shade=mix(vec3(.21,.15,.30),vec3(.66,.40,.25),smoothstep(.32,.72,cloud));
 col=mix(col,shade,density*.90);
 float near=fbm(vec3(p*vec2(6.2,12.5)+vec2(u_time*.013,0.),11.2));
 float low=1.-smoothstep(.03,.21,y-.035*sin(p.x*12.));
 col=mix(col,mix(vec3(.18,.12,.26),vec3(.56,.34,.25),smoothstep(.20,.82,near)),low*.83);
 float shafts=pow(.5+.5*sin(atan(p.x-.76,y-.36)*24.),10.);
 col+=vec3(.09,.055,.025)*shafts*exp(-d*3.)*smoothstep(.20,.62,y);
 col+=vec3(.045,.024,.01)*u_accent*exp(-d*d*11.);
 frag=vec4(col*.52,1.);
}
"""

MESH_VERT = """#version 330
in vec3 in_pos;in vec3 in_normal;in vec2 in_uv;
uniform mat4 mvp;uniform mat3 rotation;uniform float scale;
out vec3 normal;out vec3 world;out vec2 texcoord;
void main(){world=rotation*in_pos*scale;normal=rotation*in_normal;texcoord=in_uv;
gl_Position=mvp*vec4(world,1.);}
"""

EARTH = """#version 330
in vec3 normal;in vec3 world;in vec2 texcoord;out vec4 frag;
uniform sampler2D land_tex;uniform vec3 camera;uniform float u_time;uniform float u_accent;
""" + NOISE + """
void main(){
 vec3 n=normalize(normal),v=normalize(camera-world);float facing=max(dot(n,v),0.);
 vec3 light=normalize(vec3(-.7,-.7,.9));float ndl=max(dot(n,light),0.);
 float land=texture(land_tex,texcoord).r;
 vec3 ocean=mix(vec3(.008,.025,.085),vec3(.022,.16,.28),ndl);
 float top=smoothstep(-.55,.8,n.z);
 ocean+=vec3(.014,.025,.065)*top;
 float detail=fbm(n*18.);
 vec3 ground=mix(vec3(.29,.10,.018),vec3(1.05,.55,.13),.25+.75*ndl);
 ground*=.78+.28*detail;
 vec3 col=mix(ocean,ground,land*.89);
 float cloud=fbm(n*4.7+vec3(u_time*.006,3.8,1.9));
 float wisps=smoothstep(.57,.77,cloud+fbm(n*17.)*.12);
 col=mix(col,vec3(.50,.63,.68)*(.55+.45*ndl),wisps*.18);
 vec2 grid=vec2(texcoord.x*420.,texcoord.y*210.);
 float dotlight=1.-smoothstep(.08,.35,length(fract(grid)-.5));
 float sparkle=(.72+.28*sin(texcoord.x*94.+texcoord.y*68.));
 col+=land*dotlight*vec3(.24,.18,.07)*sparkle;
 float rim=pow(1.-facing,3.6);
 col+=vec3(.09,.43,.68)*rim;
 col+=vec3(.18,.14,.055)*land*u_accent;
 frag=vec4(col,1.);
}
"""

ATMOS = """#version 330
in vec3 normal;in vec3 world;in vec2 texcoord;out vec4 frag;
uniform vec3 camera;
void main(){vec3 n=normalize(normal),v=normalize(camera-world);
float a=pow(1.-abs(dot(n,v)),4.2);
vec3 c=mix(vec3(.15,.55,.9),vec3(.85,.53,.23),smoothstep(-.1,.85,n.z));
frag=vec4(c*a*.7,1.);}
"""

RIBBON_VERT = """#version 330
in vec3 in_pos;in vec3 in_next;in vec2 in_uv;
uniform mat4 mvp;uniform vec2 resolution;uniform float thickness;
out vec2 uv;
void main(){vec4 p=mvp*vec4(in_pos,1.),q=mvp*vec4(in_next,1.);
vec2 direction=normalize((q.xy/q.w-p.xy/p.w)*resolution+vec2(.000001));
vec2 offset=vec2(-direction.y,direction.x)*in_uv.y*thickness*2./resolution;
gl_Position=p+vec4(offset*p.w,0.,0.);uv=in_uv;}
"""

RIBBON_FRAG = """#version 330
in vec2 uv;out vec4 frag;uniform vec3 colour;uniform float phase;uniform float u_accent;
void main(){float soft=pow(max(0.,1.-abs(uv.y)),1.7);
float core=exp(-uv.y*uv.y*26.);
float tip=smoothstep(0.,.07,uv.x)*(1.-smoothstep(.93,1.,uv.x));
float packet=exp(-pow((uv.x-phase)/.045,2.));
vec3 c=colour*(.32*soft+1.25*core)+mix(colour,vec3(1.,.91,.75),.68)*packet*core*4.5;
frag=vec4(c*tip*(1.+.12*u_accent),1.);}
"""

POINT_VERT = """#version 330
in vec3 in_pos;in vec3 in_colour;in float in_size;
uniform mat4 mvp;uniform float pixel_scale;
out vec3 colour;
void main(){gl_Position=mvp*vec4(in_pos,1.);gl_PointSize=in_size*pixel_scale;colour=in_colour;}
"""
POINT_FRAG = """#version 330
in vec3 colour;out vec4 frag;
void main(){vec2 q=gl_PointCoord*2.-1.;float r=length(q);if(r>1.)discard;
float a=exp(-r*r*6.);frag=vec4(colour*a,1.);}
"""

BLUR = """#version 330
in vec2 uv;out vec4 frag;uniform sampler2D image;uniform vec2 step_size;uniform bool extract;
vec3 sample_at(vec2 p){vec3 c=texture(image,p).rgb;return extract?max(c-vec3(.55),vec3(0.)):c;}
void main(){vec3 c=sample_at(uv)*.227027;
c+=(sample_at(uv+step_size*1.384615)+sample_at(uv-step_size*1.384615))*.316216;
c+=(sample_at(uv+step_size*3.230769)+sample_at(uv-step_size*3.230769))*.070270;
frag=vec4(c,1.);}
"""
FINISH = """#version 330
in vec2 uv;out vec4 frag;uniform sampler2D scene;uniform sampler2D bloom;uniform sampler2D type;
uniform float weight;
vec3 aces(vec3 x){return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.);}
vec3 display(vec3 x){return mix(x*12.92,1.055*pow(max(x,vec3(0.)),vec3(1./2.4))-.055,step(vec3(.0031308),x));}
void main(){vec3 c=texture(scene,uv).rgb+texture(bloom,uv).rgb*.58;
c=display(aces(c*.93));
vec4 text=texture(type,uv);c=mix(c,text.rgb,text.a);
frag=vec4(c*weight,weight);}
"""


def smooth(u):
    u = min(1., max(0., u))
    return u*u*u*(10.+u*(-15.+6.*u))


def projection(aspect):
    f = 1 / math.tan(math.radians(41) / 2)
    near, far = .08, 120.
    p = np.array([[f/aspect, 0, -.37, 0], [0, f, 0, 0],
                  [0, 0, -(far+near)/(far-near), -2*far*near/(far-near)],
                  [0, 0, -1, 0]], dtype="f4")
    return p


def look_at(eye, target):
    eye, target = np.array(eye), np.array(target)
    forward = target-eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, [0, 0, 1])
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    view = np.eye(4, dtype="f4")
    view[:3, :3] = np.array([right, up, -forward])
    view[:3, 3] = -view[:3, :3] @ eye
    return view


def linear(rgb):
    a = np.asarray(rgb, dtype=float)
    return tuple(np.where(a <= .04045, a/12.92, ((a+.055)/1.055)**2.4))


def source_hashes():
    paths = [*Path(__file__).parent.glob("*.py"), *ROOT.joinpath("pipeline/motion").glob("*.py"),
             ROOT/"engine/p3d/brand.py", ROOT/"engine/p3d/brand_symbols.py",
             ROOT/"assets/p3d/brand/land_2048.png", *ROOT.joinpath("fonts").glob("*.ttf")]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


class PromoRenderer:
    def __init__(self, width=1920, height=1080, temporal_samples=2):
        self.width, self.height = width, height
        self.samples = temporal_samples
        self.ctx = c = moderngl.create_standalone_context(backend="egl")
        self.renderer_name = c.info["GL_RENDERER"]
        self.quad = c.buffer(np.array([[-1,-1],[1,-1],[-1,1],[1,1]], "f4").tobytes())
        self.sky, self.v_sky = self.fullscreen(SKY)
        self.blur, self.v_blur = self.fullscreen(BLUR)
        self.finish, self.v_finish = self.fullscreen(FINISH)
        self.scene_tex = c.texture((width,height), 4, dtype="f2")
        self.scene_fbo = c.framebuffer([self.scene_tex], c.depth_renderbuffer((width,height)))
        self.small = (max(1,width//3),max(1,height//3))
        self.blur_tex = [c.texture(self.small,4,dtype="f2") for _ in range(2)]
        self.blur_fbo = [c.framebuffer([t]) for t in self.blur_tex]
        self.out_tex = c.texture((width,height),4,dtype="f2")
        self.out_fbo = c.framebuffer([self.out_tex])
        for tex in [self.scene_tex, *self.blur_tex, self.out_tex]:
            tex.filter = (moderngl.LINEAR,moderngl.LINEAR)
            tex.repeat_x = tex.repeat_y = False
        overlay = build_overlay(width,height).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.type_tex = c.texture((width,height),4,overlay.tobytes())
        self.type_tex.filter = (moderngl.LINEAR,moderngl.LINEAR)
        mask = Image.open(ROOT/"assets/p3d/brand/land_2048.png").convert("L")
        self.land_tex = c.texture(mask.size,1,mask.tobytes())
        self.land_tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR,moderngl.LINEAR)
        self.land_tex.build_mipmaps()
        sphere = c.buffer(sphere_mesh().tobytes())
        self.earth = c.program(vertex_shader=MESH_VERT,fragment_shader=EARTH)
        self.v_earth = c.vertex_array(self.earth,[(sphere,"3f 3f 2f","in_pos","in_normal","in_uv")])
        self.atmos = c.program(vertex_shader=MESH_VERT,fragment_shader=ATMOS)
        self.v_atmos = c.vertex_array(self.atmos,[(sphere,"3f 3f 8x","in_pos","in_normal")])
        self.ribbon = c.program(vertex_shader=RIBBON_VERT,fragment_shader=RIBBON_FRAG)
        self.ribbon_buffer = c.buffer(reserve=224*2*8*4,dynamic=True)
        self.v_ribbon = c.vertex_array(self.ribbon,[(self.ribbon_buffer,"3f 3f 2f","in_pos","in_next","in_uv")])
        self.points = c.program(vertex_shader=POINT_VERT,fragment_shader=POINT_FRAG)
        rng = np.random.default_rng(2026)
        xyz = star_points(1900)
        colours = np.tile([1.0,.82,.61],(len(xyz),1))*rng.uniform(.3,1.3,(len(xyz),1))
        sizes = rng.uniform(1.6,4.2,(len(xyz),1))
        colours[:18]*=3.;sizes[:18]*=2.2
        star = np.c_[xyz,colours,sizes].astype("f4")
        self.star_buffer = c.buffer(star.tobytes())
        self.v_stars = c.vertex_array(self.points,[(self.star_buffer,"3f 3f 1f","in_pos","in_colour","in_size")])
        self.dynamic_points = c.buffer(reserve=8000*7*4,dynamic=True)
        self.v_dynamic = c.vertex_array(self.points,[(self.dynamic_points,"3f 3f 1f","in_pos","in_colour","in_size")])
        self.track = CameraTrack([0,3.1,6.8,10],
            [(-2.8,-8.8,2.8),(-1.2,-8.0,1.8),(1.2,-8.1,1.1),(2.4,-8.8,1.2)],
            [(0,0,.10)],easing="smootherstep")
        self.p = projection(width/height)
        self.earth["land_tex"].value = 0
        self.blur["image"].value = 0
        for name,unit in (("scene",0),("bloom",1),("type",2)):
            self.finish[name].value = unit

    def fullscreen(self,fragment):
        prog=self.ctx.program(vertex_shader=VERT,fragment_shader=fragment)
        return prog,self.ctx.vertex_array(prog,[(self.quad,"2f","in_pos")])

    def scene(self,t):
        c = self.ctx
        s = self.track.sample(t)
        mvp = self.p @ look_at(s.position,s.target)
        mat = mvp.T.astype("f4").tobytes()
        accent = math.exp(-((t-8.11)/.65)**2)*.55 + math.exp(-((t-5.11)/.8)**2)*.18
        self.scene_fbo.use(); c.viewport=(0,0,self.width,self.height)
        self.scene_fbo.depth_mask=True
        self.scene_fbo.clear(0,0,0,1,depth=1.)
        c.disable(moderngl.DEPTH_TEST|moderngl.BLEND|moderngl.CULL_FACE)
        self.sky["u_time"].value=t;self.sky["u_accent"].value=accent
        self.v_sky.render(moderngl.TRIANGLE_STRIP)
        c.enable(moderngl.PROGRAM_POINT_SIZE|moderngl.BLEND)
        c.blend_func=(moderngl.ONE,moderngl.ONE)
        self.points["mvp"].write(mat);self.points["pixel_scale"].value=self.height/1080
        self.v_stars.render(moderngl.POINTS)
        c.disable(moderngl.BLEND)
        c.enable(moderngl.DEPTH_TEST|moderngl.CULL_FACE)
        self.scene_fbo.depth_mask=True
        angle=math.radians(-39-8*smooth(t/10))
        a,b=math.cos(angle),math.sin(angle)
        rot=np.array([[a,-b,0],[b,a,0],[0,0,1]],"f4").T.tobytes()
        self.earth["mvp"].write(mat);self.earth["rotation"].write(rot)
        self.earth["scale"].value=1.;self.earth["camera"].value=s.position
        self.earth["u_time"].value=t;self.earth["u_accent"].value=accent
        self.land_tex.use(0);self.v_earth.render()
        c.enable(moderngl.BLEND);self.scene_fbo.depth_mask=False
        c.blend_func=(moderngl.ONE,moderngl.ONE)
        self.atmos["mvp"].write(mat);self.atmos["rotation"].write(rot)
        self.atmos["scale"].value=1.025;self.atmos["camera"].value=s.position
        self.v_atmos.render()
        c.disable(moderngl.CULL_FACE)
        self.ribbon["mvp"].write(mat);self.ribbon["resolution"].value=(self.width,self.height)
        self.ribbon["u_accent"].value=accent
        paths=make_ribbon_paths(t)
        particles=[]
        for j,path in enumerate(paths):
            xyz=path["positions"];n=len(xyz)
            following=np.vstack([xyz[1:],xyz[-1]+(xyz[-1]-xyz[-2])])
            u=np.linspace(0,1,n,dtype="f4")
            left=np.c_[xyz,following,u,np.full(n,-1)].astype("f4")
            right=np.c_[xyz,following,u,np.full(n,1)].astype("f4")
            vertices=np.stack([left,right],axis=1).reshape(-1,8)
            self.ribbon_buffer.write(vertices.tobytes())
            self.ribbon["colour"].value=linear(path["colours"])
            self.ribbon["phase"].value=path["phase"]
            self.ribbon["thickness"].value=(4.5+path["width"]*70)*self.height/1080
            self.v_ribbon.render(moderngl.TRIANGLE_STRIP,vertices=n*2)
            # Continuous light packets, with no random value or lifetime resets.
            u=np.linspace(.025,.975,120)
            wave=.014*np.sin(t*.9+u*17+j*.83)
            sample=np.clip(u+wave,0.,1.)*(n-1)
            low=np.floor(sample).astype(int);high=np.minimum(low+1,n-1)
            xyzp=xyz[low]*(1.-(sample-low)[:,None])+xyz[high]*(sample-low)[:,None]
            spread=.011*np.c_[np.sin(u*83+j),np.cos(u*97+j),np.sin(u*119+j)]
            xyzp+=spread
            packet=np.exp(-((u-path["phase"])/.09)**2)
            intensity=.10+.9*packet
            colour=np.array(linear(path["colours"]))*.9+np.array([.38,.28,.15])
            colours=intensity[:,None]*colour[None,:]
            sizes=1.6+packet*4.3
            particles.append(np.c_[xyzp,colours,sizes])
        symbols=symbol_vertices(t,s.position)
        symbols[:,3:6]*=2.4
        symbols[:,6]=2.6
        data=np.concatenate([*particles,symbols]).astype("f4")
        self.dynamic_points.write(data.tobytes());self.v_dynamic.render(moderngl.POINTS,vertices=len(data))
        self.scene_fbo.depth_mask=True
        c.disable(moderngl.DEPTH_TEST|moderngl.BLEND)
        c.viewport=(0,0,*self.small)
        self.scene_tex.use(0);self.blur_fbo[0].use()
        self.blur["extract"].value=True;self.blur["step_size"].value=(1.5/self.small[0],0)
        self.v_blur.render(moderngl.TRIANGLE_STRIP)
        for i in range(3):
            source,target=(0,1) if i%2==0 else (1,0)
            self.blur_tex[source].use(0);self.blur_fbo[target].use()
            self.blur["extract"].value=False
            self.blur["step_size"].value=(0,2./self.small[1]) if i%2==0 else (2./self.small[0],0)
            self.v_blur.render(moderngl.TRIANGLE_STRIP)
        self.out_fbo.use();c.viewport=(0,0,self.width,self.height)
        c.enable(moderngl.BLEND);c.blend_func=(moderngl.ONE,moderngl.ONE)
        self.scene_tex.use(0);self.blur_tex[1].use(1);self.type_tex.use(2)
        self.finish["weight"].value=1./self.samples
        self.v_finish.render(moderngl.TRIANGLE_STRIP)
        c.disable(moderngl.BLEND)

    def frame(self,index):
        self.out_fbo.clear(0,0,0,0)
        for i in range(self.samples):
            dt=((i+.5)/self.samples-.5)*.5/60
            self.scene(min(10.,max(0.,index/60+dt)))
        raw=self.out_fbo.read(components=3,alignment=1,dtype="f1")
        return np.frombuffer(raw,dtype=np.uint8).reshape(self.height,self.width,3)[::-1].copy()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--width",type=int,default=1920)
    ap.add_argument("--height",type=int,default=1080)
    ap.add_argument("--samples",type=int,default=2)
    ap.add_argument("--stills",help="Comma-separated seconds")
    ap.add_argument("--start",type=int,default=0)
    ap.add_argument("--end",type=int,default=600)
    ap.add_argument("--out",default="work/promo-design-example/preview.mp4")
    a=ap.parse_args()
    if sys.platform == "darwin":ap.error("This sample is configured for cloud CPU rendering.")
    if not 0<=a.start<a.end<=600 or a.samples<1:ap.error("Invalid range or temporal samples")
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    inputs=source_hashes()
    renderer=PromoRenderer(a.width,a.height,a.samples)
    print(json.dumps({"renderer":renderer.renderer_name,"size":[a.width,a.height],"temporal_samples":a.samples}),flush=True)
    if a.stills:
        out.mkdir(parents=True,exist_ok=True)
        for t in map(float,a.stills.split(",")):
            started=time.monotonic();frame=min(599,round(t*60))
            data=renderer.frame(frame)
            p=out/f"frame-{frame:04d}.png";Image.fromarray(data).save(p)
            print(json.dumps({"frame":frame,"path":str(p),"seconds":round(time.monotonic()-started,3)}),flush=True)
        return
    command=["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{a.width}x{a.height}","-framerate","60","-i","pipe:0",
        "-vf","zscale=matrixin=gbr:transferin=iec61966-2-1:primariesin=bt709:rangein=full:matrix=bt709:transfer=bt709:primaries=bt709:range=limited,format=yuv420p",
        "-c:v","libx264","-preset","medium","-crf","15","-profile:v","high","-threads","2",
        "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-color_range","tv","-movflags","+faststart",str(out)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    started=time.monotonic()
    try:
        for index in range(a.start,a.end):
            process.stdin.write(renderer.frame(index).tobytes())
            if (index-a.start)%30==0:
                print(json.dumps({"frame":index,"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
        process.stdin.close()
        if process.wait()!=0:raise RuntimeError("FFmpeg failed")
    except BaseException:
        process.kill();process.wait();raise
    record={"frames":a.end-a.start,"start":a.start,"end":a.end,"fps":60,"width":a.width,"height":a.height,
        "temporal_samples":a.samples,"renderer":renderer.renderer_name,"seconds":time.monotonic()-started,
        "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"camera":renderer.track.diagnostics(120),
        "source_sha256":inputs}
    if source_hashes()!=inputs:raise RuntimeError("Scene inputs changed during rendering; this part is unverified.")
    out.with_suffix(".json").write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps(record),flush=True)


if __name__=="__main__":main()
