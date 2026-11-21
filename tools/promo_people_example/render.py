"""Native cloud CPU renderer for the isolated thirty-second people proposal.

The full human assets, cloth and motion come from the existing project. Every
frame is evaluated at absolute song time, with linear-light shutter sampling.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
os.environ.setdefault("LP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import moderngl
import numpy as np
from PIL import Image

from pipeline.motion import CameraTrack
from tools.promo_design_example.render import (
    VERT, SKY, BLUR, RIBBON_VERT, RIBBON_FRAG, POINT_VERT, POINT_FRAG, look_at, smooth,
)
from tools.promo_design_example.world_geometry import star_points
from tools.promo_people_example.environment import static_mesh, environment_points, ribbon_paths
from tools.promo_people_example.people import PeopleScene
from tools.promo_people_example.typography import build_overlay

FPS = 60
FRAMES = 1800
CUTS = (612, 1168)
PEOPLE_SKY = SKY.replace("(y-.18)/.19", "(y-.48)/.22").replace("density*.90", "density*.52")

STAGE_VERT = """#version 330
in vec3 in_pos;in vec3 in_normal;in vec3 in_colour;
uniform mat4 mvp;out vec3 world;out vec3 normal;out vec3 colour;
void main(){world=in_pos;normal=in_normal;colour=in_colour;gl_Position=mvp*vec4(in_pos,1.);}
"""
STAGE_FRAG = """#version 330
in vec3 world;in vec3 normal;in vec3 colour;out vec4 frag;
uniform vec3 camera;uniform vec3 contacts[32];uniform int contact_count;
uniform float u_time;uniform float u_accent;uniform float close_shot;
uniform vec2 resolution;uniform float closing_shot;
void main(){
 float shade=.88;float groundlight=0.;
 for(int i=0;i<32;i++){if(i>=contact_count)break;
  float d=length(world.xy-contacts[i].xy);
  shade*=1.-.31*exp(-d*d/0.038)*step(abs(world.z-contacts[i].z),.10);
  groundlight+=.024*exp(-d*d/.38);
 }
 float r=length(world.xy-vec2(.8,2.));
 float veins=pow(.5+.5*sin(r*5.8+sin(world.x*.6+world.y*.32)*.6),20.);
 float horizon=pow(max(dot(normalize(camera-world),vec3(0,0,1)),0.),.5);
 float key=.64+.36*max(dot(normalize(normal),normalize(vec3(-.3,-.5,1.))),0.);
 vec3 col=colour*(.78+.22*horizon)*shade*key;
 col+=vec3(.055,.022,.035)*veins*.16;
 float bright=max(colour.r,max(colour.g,colour.b));
 col*=1.-(.50+close_shot*.26)*smoothstep(1.8,3.3,world.y)*smoothstep(.12,.35,bright);
 float quiet_left=1.-smoothstep(.265,.34,gl_FragCoord.x/resolution.x);
 col*=1.-closing_shot*.88*quiet_left*smoothstep(.12,.35,bright);
 col+=vec3(.55,.27,.06)*groundlight;
 col+=vec3(.010,.006,.003)*u_accent;
 float fog=1.-exp(-max(length(camera-world)-9.,0.)*.018);
 col=mix(col,vec3(.12,.055,.13),fog);
 frag=vec4(col,1.);
}
"""

HUMAN_VERT = """#version 330
in vec3 in_pos;in vec3 in_normal;in vec3 in_colour;
in float in_size;in float in_alpha;in float in_seed;
uniform mat4 mvp;uniform vec3 camera;uniform float focal_pixels;
uniform float pixel_scale;uniform float u_time;uniform bool reflection;
out vec3 colour;out float energy;out float sparkle;
void main(){
 vec3 p=in_pos;vec3 n=in_normal;
 float reflect_gain=1.;
 if(reflection){p.z=-p.z-.018;n.z=-n.z;reflect_gain=.075*exp(-in_pos.z*1.2);}
 vec4 clip=mvp*vec4(p,1.);gl_Position=clip;
 float actual=max(.04,in_size*focal_pixels/max(clip.w,.1));
 float diameter=clamp(actual,1.05*pixel_scale,9.*pixel_scale);
 gl_PointSize=diameter;
 float conserving=min(1.,actual*actual/(diameter*diameter));
 vec3 view=normalize(camera-p);
 float facing=dot(normalize(n),view);
 float rim=pow(1.-abs(facing),1.5);
 float key=max(dot(normalize(n),normalize(vec3(-.5,-.7,.9))),0.);
 float twinkle=.90+.10*sin(u_time*1.15+in_seed*83.);
 float front=smoothstep(-.45,.15,facing);
 colour=in_colour*(.58+.88*rim+.32*key);
 float fog=exp(-max(length(camera-p)-9.,0.)*.022);
 energy=in_alpha*conserving*twinkle*front*fog*reflect_gain*3.8;
 sparkle=step(.9988,in_seed);
}
"""
HUMAN_FRAG = """#version 330
in vec3 colour;in float energy;in float sparkle;out vec4 frag;
void main(){vec2 q=gl_PointCoord*2.-1.;float r=dot(q,q);if(r>1.)discard;
 float core=exp(-r*3.5);
 float glint=exp(-abs(q.x)*25.-abs(q.y)*3.)+exp(-abs(q.y)*25.-abs(q.x)*3.);
 frag=vec4(colour*energy*(core+sparkle*glint*.18),1.);
}
"""

ACCUM = """#version 330
in vec2 uv;out vec4 frag;uniform sampler2D image;uniform float weight;
void main(){frag=vec4(texture(image,uv).rgb*weight,1.);}
"""
FINISH = """#version 330
in vec2 uv;out vec4 frag;uniform sampler2D scene;uniform sampler2D bloom;
uniform sampler2D opening;uniform sampler2D signature;uniform sampler2D greeting;uniform sampler2D closing;
uniform vec4 type_weights;
vec3 aces(vec3 x){return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.);}
vec3 display(vec3 x){return mix(x*12.92,1.055*pow(max(x,vec3(0.)),vec3(1./2.4))-.055,step(vec3(.0031308),x));}
vec3 over(vec3 c,vec4 type,float w){return mix(c,type.rgb,type.a*w);}
void main(){vec3 c=texture(scene,uv).rgb+texture(bloom,uv).rgb*.38;
 c=display(aces(c*.93));
 c=over(c,texture(opening,uv),type_weights.x);
 c=over(c,texture(signature,uv),type_weights.y);
 c=over(c,texture(greeting,uv),type_weights.z);
 c=over(c,texture(closing,uv),type_weights.w);
 frag=vec4(c,1.);}
"""


def projection(aspect, fov, offset=0.0):
    f=1/math.tan(math.radians(fov)/2)
    near,far=.08,160.
    return np.array([[f/aspect,0,-offset,0],[0,f,0,0],
        [0,0,-(far+near)/(far-near),-2*far*near/(far-near)],
        [0,0,-1,0]],dtype="f4")


def source_hashes():
    paths=[*Path(__file__).parent.glob("*.py"),
           *ROOT.joinpath("tools/promo_design_example").glob("*.py"),
           *ROOT.joinpath("pipeline/motion").glob("*.py"),
           *ROOT.joinpath("engine/p3d").glob("*.py"),
           *ROOT.joinpath("assets/p3d").glob("*.npz"),
           *ROOT.joinpath("fonts").glob("*.ttf"),ROOT/"pyproject.toml",ROOT/"uv.lock"]
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def runtime_identity():
    context=moderngl.create_standalone_context(backend="egl")
    gl={key:context.info[key] for key in ("GL_RENDERER","GL_VERSION","GL_VENDOR")}
    context.release()
    return {"python":platform.python_version(),"platform":platform.platform(),
        "numpy":np.__version__,"moderngl":importlib.metadata.version("moderngl"),
        "pillow":importlib.metadata.version("Pillow"),
        "ffmpeg":subprocess.check_output(["ffmpeg","-version"],text=True).splitlines()[0],
        "software_gl":os.environ["LIBGL_ALWAYS_SOFTWARE"],
        "mesa_threads":os.environ["LP_NUM_THREADS"],"gl":gl}


class PeopleRenderer:
    def __init__(self,width=1920,height=1080,samples=2):
        self.width,self.height,self.samples=width,height,samples
        self.ctx=c=moderngl.create_standalone_context(backend="egl")
        self.renderer_name=c.info["GL_RENDERER"]
        self.people=PeopleScene()
        self.quad=c.buffer(np.array([[-1,-1],[1,-1],[-1,1],[1,1]],"f4").tobytes())
        self.sky,self.v_sky=self.fullscreen(PEOPLE_SKY)
        self.blur,self.v_blur=self.fullscreen(BLUR)
        self.accum,self.v_accum=self.fullscreen(ACCUM)
        self.finish,self.v_finish=self.fullscreen(FINISH)
        self.scene_tex=c.texture((width,height),4,dtype="f2")
        self.scene_fbo=c.framebuffer([self.scene_tex],c.depth_renderbuffer((width,height)))
        self.accum_tex=c.texture((width,height),4,dtype="f2")
        self.accum_fbo=c.framebuffer([self.accum_tex])
        self.out_tex=c.texture((width,height),4,dtype="f1")
        self.out_fbo=c.framebuffer([self.out_tex])
        self.small=(max(1,width//3),max(1,height//3))
        self.blur_tex=[c.texture(self.small,4,dtype="f2") for _ in range(2)]
        self.blur_fbo=[c.framebuffer([a]) for a in self.blur_tex]
        self.type_tex=[]
        for kind in ("opening","signature","greeting","closing"):
            im=build_overlay(width,height,kind).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.type_tex.append(c.texture((width,height),4,im.tobytes()))
        self.stage=c.program(vertex_shader=STAGE_VERT,fragment_shader=STAGE_FRAG)
        stage_buffer=c.buffer(static_mesh().astype("f4").tobytes())
        self.v_stage=c.vertex_array(self.stage,[(stage_buffer,"3f 3f 3f","in_pos","in_normal","in_colour")])
        self.human=c.program(vertex_shader=HUMAN_VERT,fragment_shader=HUMAN_FRAG)
        self.human_buffer=c.buffer(reserve=600000*12*4,dynamic=True)
        self.v_human=c.vertex_array(self.human,[(self.human_buffer,"3f 3f 3f 1f 1f 1f", "in_pos","in_normal","in_colour","in_size","in_alpha","in_seed")])
        self.points=c.program(vertex_shader=POINT_VERT,fragment_shader=POINT_FRAG)
        rng=np.random.default_rng(20261120)
        xyz=star_points(1600)*2.1
        colors=np.tile([.54,.33,.22],(len(xyz),1))*rng.uniform(.25,1.1,(len(xyz),1))
        star=np.c_[xyz,colors,rng.uniform(1.2,3.1,(len(xyz),1))].astype("f4")
        self.star_buffer=c.buffer(star.tobytes())
        self.v_stars=c.vertex_array(self.points,[(self.star_buffer,"3f 3f 1f","in_pos","in_colour","in_size")])
        self.dynamic_buffer=c.buffer(reserve=30000*7*4,dynamic=True)
        self.v_dynamic=c.vertex_array(self.points,[(self.dynamic_buffer,"3f 3f 1f","in_pos","in_colour","in_size")])
        self.ribbon=c.program(vertex_shader=RIBBON_VERT,fragment_shader=RIBBON_FRAG)
        self.ribbon_buffer=c.buffer(reserve=2048*2*8*4,dynamic=True)
        self.v_ribbon=c.vertex_array(self.ribbon,[(self.ribbon_buffer,"3f 3f 2f","in_pos","in_next","in_uv")])
        self.tracks=[
            CameraTrack([0,5,10.2],[(1.6,-5.9,1.85),(1.4,-5.6,1.78),(1.1,-5.5,1.75)],[(-2,0,1.0)],easing="smootherstep"),
            CameraTrack([10.2,14.8,1168/60],[(5.0,-3.8,2.55),(4.45,-3.0,2.35),(3.9,-3.3,2.5)],[(2.5,3.1,1.1)],easing="smootherstep"),
            CameraTrack([1168/60,24.5,30],[(5.5,-7.5,4.1),(6.6,-9.0,5.2),(7.5,-10.8,6.1)],[(.8,2.3,1.15)],easing="smootherstep"),
        ]
        self.accum["image"].value=0
        self.blur["image"].value=0
        for i,name in enumerate(("scene","bloom","opening","signature","greeting","closing")):
            self.finish[name].value=i

    def fullscreen(self,fragment):
        program=self.ctx.program(vertex_shader=VERT,fragment_shader=fragment)
        return program,self.ctx.vertex_array(program,[(self.quad,"2f","in_pos")])

    def camera(self,t,shot):
        sample=self.tracks[shot].sample(t)
        fov=(32.,43.,44.)[shot]
        offset=(.28,0.,.17)[shot]
        p=projection(self.width/self.height,fov,offset)
        return sample,p@look_at(sample.position,sample.target),fov

    def scene(self,t,shot):
        c=self.ctx
        camera,mvp,fov=self.camera(t,shot)
        mat=mvp.T.astype("f4").tobytes()
        accent=.28*math.exp(-((t-12.51)/.6)**2)+.35*math.exp(-((t-28.11)/.7)**2)
        self.scene_fbo.use();c.viewport=(0,0,self.width,self.height)
        self.scene_fbo.depth_mask=True;self.scene_fbo.clear(0,0,0,1,depth=1.)
        c.disable(moderngl.DEPTH_TEST|moderngl.BLEND|moderngl.CULL_FACE)
        self.sky["u_time"].value=t;self.sky["u_accent"].value=accent
        self.v_sky.render(moderngl.TRIANGLE_STRIP)
        c.enable(moderngl.PROGRAM_POINT_SIZE|moderngl.BLEND)
        c.blend_func=(moderngl.ONE,moderngl.ONE)
        self.points["mvp"].write(mat);self.points["pixel_scale"].value=self.height/1080
        self.v_stars.render(moderngl.POINTS)
        c.disable(moderngl.BLEND);c.enable(moderngl.DEPTH_TEST)
        self.stage["mvp"].write(mat);self.stage["camera"].value=camera.position
        anchors=self.people.anchors(t)
        contacts=np.zeros((32,3),"f4")
        values=np.asarray(anchors.get("contacts",[]),dtype="f4").reshape(-1,3)
        if shot==0:values=values[:4]
        if len(values)%2==0:values=values.reshape(-1,2,3).mean(axis=1)
        count=min(len(values),32);contacts[:count]=values[:count]
        self.stage["contacts"].write(contacts.tobytes());self.stage["contact_count"].value=count
        if "u_time" in self.stage:self.stage["u_time"].value=t
        self.stage["u_accent"].value=accent
        self.stage["close_shot"].value=1. if shot==0 else 0.
        self.stage["resolution"].value=(self.width,self.height)
        self.stage["closing_shot"].value=smooth((t-22.)/1.) if shot==2 else 0.
        self.v_stage.render()
        # The first camera's performance set is the foreground pair. Ensemble
        # performers enter with the second editorial shot, without edge crops.
        if shot==0:
            people=np.concatenate([self.people._body_array(self.people.bodies[name],t,ground_correct=True)
                                   for name in ("pair_a","pair_b")])
        else:
            people=self.people.sample(t)
        if len(people)*48>self.human_buffer.size:raise RuntimeError("Human point buffer exceeded")
        self.human_buffer.write(people.tobytes())
        self.human["mvp"].write(mat);self.human["camera"].value=camera.position
        self.human["focal_pixels"].value=self.height/(2*math.tan(math.radians(fov)/2))
        self.human["pixel_scale"].value=self.height/1080
        self.human["u_time"].value=t
        c.enable(moderngl.BLEND);c.blend_func=(moderngl.ONE,moderngl.ONE)
        self.scene_fbo.depth_mask=False
        c.disable(moderngl.DEPTH_TEST)
        self.human["reflection"].value=True
        self.v_human.render(moderngl.POINTS,vertices=len(people))
        c.enable(moderngl.DEPTH_TEST)
        self.human["reflection"].value=False
        self.v_human.render(moderngl.POINTS,vertices=len(people))
        self.ribbon["mvp"].write(mat);self.ribbon["resolution"].value=(self.width,self.height)
        self.ribbon["u_accent"].value=accent
        for path in ribbon_paths(t):
            xyz=np.asarray(path["positions"],"f4");n=len(xyz)
            following=np.vstack([xyz[1:],xyz[-1]+xyz[-1]-xyz[-2]])
            u=np.linspace(0,1,n,dtype="f4")
            vertices=np.stack([np.c_[xyz,following,u,np.full(n,-1)],np.c_[xyz,following,u,np.ones(n)]],axis=1).reshape(-1,8).astype("f4")
            self.ribbon_buffer.write(vertices.tobytes())
            self.ribbon["colour"].value=tuple(path["color"])
            self.ribbon["phase"].value=float(path["phase"])
            self.ribbon["thickness"].value=(2.0+path["width"]*50)*self.height/1080
            self.v_ribbon.render(moderngl.TRIANGLE_STRIP,vertices=len(vertices))
        points=environment_points(t)
        if len(points):
            self.dynamic_buffer.write(points.astype("f4").tobytes())
            self.v_dynamic.render(moderngl.POINTS,vertices=len(points))
        # The offered human gesture releases a soft light path toward the choir.
        if t>=6.0:
            hands=anchors.get("pair_palms",[])
            if len(hands):
                origin=np.asarray(hands[0],float)
                u=np.linspace(0,1,220)
                end=np.array([2.5,3.2,2.2])
                xyz=origin[None]*(1-u[:,None])+end[None]*u[:,None]
                xyz[:,2]+=1.0*np.sin(u*np.pi)
                xyz[:,0]+=.12*np.sin(u*9-t*.5)*np.sin(u*np.pi)
                travel=smooth((t-6.2)/7.)
                light=np.exp(-((u-travel)/.12)**2)*smooth((t-6.)/.8)*(1-smooth((t-15.)/2.))
                flow=np.c_[xyz,light[:,None]*np.array([.85,.45,.11]),1.1+2.5*light].astype("f4")
                self.dynamic_buffer.write(flow.tobytes());self.v_dynamic.render(moderngl.POINTS,vertices=len(flow))
        self.scene_fbo.depth_mask=True
        c.disable(moderngl.DEPTH_TEST|moderngl.BLEND)
        self.accum_fbo.use();c.viewport=(0,0,self.width,self.height);self.scene_tex.use(0)
        c.enable(moderngl.BLEND);c.blend_func=(moderngl.ONE,moderngl.ONE)
        self.accum["weight"].value=1/self.samples
        self.v_accum.render(moderngl.TRIANGLE_STRIP)
        c.disable(moderngl.BLEND)

    def frame(self,index):
        c=self.ctx;t=index/FPS
        shot=0 if index<CUTS[0] else 1 if index<CUTS[1] else 2
        lo=(0,CUTS[0]/FPS,CUTS[1]/FPS)[shot]
        hi=(CUTS[0]/FPS,CUTS[1]/FPS,30.)[shot]
        self.accum_fbo.clear(0,0,0,0)
        for i in range(self.samples):
            dt=((i+.5)/self.samples-.5)*.5/FPS
            self.scene(min(hi-1e-7,max(lo,t+dt)),shot)
        self.accum_tex.use(0);self.blur_fbo[0].use()
        c.viewport=(0,0,*self.small)
        self.blur["extract"].value=True;self.blur["step_size"].value=(1.5/self.small[0],0)
        self.v_blur.render(moderngl.TRIANGLE_STRIP)
        for i in range(3):
            source,target=(0,1) if i%2==0 else (1,0)
            self.blur_tex[source].use(0);self.blur_fbo[target].use()
            c.viewport=(0,0,*self.small)
            self.blur["extract"].value=False
            self.blur["step_size"].value=(0,2/self.small[1]) if i%2==0 else (2/self.small[0],0)
            self.v_blur.render(moderngl.TRIANGLE_STRIP)
        self.out_fbo.use();c.viewport=(0,0,self.width,self.height)
        self.accum_tex.use(0);self.blur_tex[1].use(1)
        for i,tex in enumerate(self.type_tex):tex.use(i+2)
        opening=1-smooth((t-7.)/.8)
        closing=smooth((t-22.)/1.)
        greeting=smooth((t-7.25)/.25) if t<10.2 else 0.
        self.finish["type_weights"].value=(opening,(1-opening)*(1-closing),greeting,closing)
        self.v_finish.render(moderngl.TRIANGLE_STRIP)
        raw=self.out_fbo.read(components=3,alignment=1,dtype="f1")
        return np.frombuffer(raw,dtype=np.uint8).reshape(self.height,self.width,3)[::-1].copy()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--width",type=int,default=1920)
    ap.add_argument("--height",type=int,default=1080)
    ap.add_argument("--samples",type=int,default=2)
    ap.add_argument("--start",type=int,default=0)
    ap.add_argument("--end",type=int,default=FRAMES)
    ap.add_argument("--stills")
    ap.add_argument("--out",default="work/promo-people-example/preview.mp4")
    args=ap.parse_args()
    if sys.platform=="darwin":ap.error("This proposal renders on cloud CPUs only.")
    if not 0<=args.start<args.end<=FRAMES or args.samples<1:ap.error("Invalid frame range or shutter samples")
    if min(args.width,args.height)<32 or args.width%2 or args.height%2:ap.error("Use positive even dimensions")
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    inputs=source_hashes();runtime=runtime_identity()
    renderer=PeopleRenderer(args.width,args.height,args.samples)
    print(json.dumps({"renderer":renderer.renderer_name,"size":[args.width,args.height],"samples":args.samples}),flush=True)
    if args.stills:
        out.mkdir(parents=True,exist_ok=True)
        for seconds in map(float,args.stills.split(",")):
            index=min(FRAMES-1,max(0,round(seconds*FPS)));start=time.monotonic()
            Image.fromarray(renderer.frame(index)).save(out/f"frame-{index:04d}.png")
            print(json.dumps({"frame":index,"seconds":round(time.monotonic()-start,3)}),flush=True)
        return
    temporary=out.with_name(out.stem+".rendering.mp4")
    cmd=["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{args.width}x{args.height}","-framerate",str(FPS),"-i","pipe:0",
        "-vf","zscale=matrixin=gbr:transferin=iec61966-2-1:primariesin=bt709:rangein=full:matrix=bt709:transfer=bt709:primaries=bt709:range=limited,format=yuv420p",
        "-c:v","libx264","-preset","medium","-crf","15","-profile:v","high","-threads","2",
        "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-color_range","tv","-movflags","+faststart",str(temporary)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE);started=time.monotonic()
    try:
        for index in range(args.start,args.end):
            process.stdin.write(renderer.frame(index).tobytes())
            if (index-args.start)%30==0:print(json.dumps({"frame":index,"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
        process.stdin.close()
        if process.wait()!=0:raise RuntimeError("Video encoder failed")
    except BaseException:
        process.kill();process.wait();raise
    if source_hashes()!=inputs:raise RuntimeError("Source changed during rendering; completed output not replaced")
    meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-count_frames","-select_streams","v:0","-show_streams","-of","json",str(temporary)],text=True))["streams"][0]
    assert int(meta["nb_read_frames"])==args.end-args.start and meta["width"]==args.width and meta["height"]==args.height
    assert meta["r_frame_rate"]==meta["avg_frame_rate"]=="60/1"
    receipt={"start":args.start,"end":args.end,"frames":args.end-args.start,"fps":FPS,"width":args.width,"height":args.height,
        "temporal_samples":args.samples,"renderer":renderer.renderer_name,"runtime":runtime,"source_sha256":inputs,
        "sha256":hashlib.sha256(temporary.read_bytes()).hexdigest(),"seconds":time.monotonic()-started,
        "camera_diagnostics":[t.diagnostics(120) for t in renderer.tracks],"cuts":list(CUTS)}
    temporary.replace(out)
    receipt_temp=out.with_suffix(".json.tmp");receipt_temp.write_text(json.dumps(receipt,indent=2)+"\n");receipt_temp.replace(out.with_suffix(".json"))
    print(json.dumps({k:receipt[k] for k in ["start","end","frames","seconds","sha256"]}),flush=True)


if __name__=="__main__":main()
