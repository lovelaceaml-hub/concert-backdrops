"""Warm satin surfaces beneath the original golden particle people.

The original rig, acting and simulated cloth supply every vertex. This local
pass adds volume and gentle facial modelling without changing engine files.
"""
import types
import numpy as np
import moderngl

VERT='''#version 330
in vec3 in_pos;
in vec3 in_normal;
in float in_alpha;
uniform mat4 vp;
out vec3 world;
out vec3 normal;
out float body_alpha;
void main(){world=in_pos;normal=in_normal;body_alpha=in_alpha;gl_Position=vp*vec4(in_pos,1.0);}
'''
FRAG='''#version 330
in vec3 world;
in vec3 normal;
in float body_alpha;
uniform vec3 eye;
uniform vec3 tint;
uniform vec3 light_pos;
uniform float coverage;
out vec4 frag;
void main(){
 if(body_alpha<.003)discard;
 vec3 n=normalize(normal);if(!gl_FrontFacing)n=-n;
 vec3 v=normalize(eye-world);
 vec3 key=normalize(light_pos-world);
 float d=max(dot(n,key),0.0);
 float grain=fract(sin(dot(world,vec3(723.13,919.37,621.19)))*43758.54);
 float rim=pow(1.0-max(dot(n,v),0.0),2.5);
 float spec=pow(max(dot(n,normalize(key+v)),0.0),28.0);
 vec3 c=tint*(.24+.48*d)+vec3(1.0,.87,.65)*(.12*rim+.22*spec);
 frag=vec4(c*coverage*body_alpha,coverage*body_alpha);
}
'''


def grid_triangles(rows,cols,closed):
    a=np.arange((rows-1)*(cols if closed else cols-1))
    width=cols if closed else cols-1
    r=a//width;c=a%width;cn=(c+1)%cols
    v00=r*cols+c;v01=r*cols+cn;v10=(r+1)*cols+c;v11=(r+1)*cols+cn
    return np.stack([np.stack([v00,v10,v01],1),np.stack([v01,v10,v11],1)],1).reshape(-1,3)


def mesh_normals(points,tris):
    face=np.cross(points[tris[:,1]]-points[tris[:,0]],points[tris[:,2]]-points[tris[:,0]])
    normals=np.zeros_like(points)
    for k in range(3):np.add.at(normals,tris[:,k],face)
    return normals/np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-10)


class Surfaces:
    def __init__(self,renderer,film):
        self.R=renderer;self.layer=renderer.p3d;self.film=film;self.ctx=renderer.ctx
        self.prog=self.ctx.program(vertex_shader=VERT,fragment_shader=FRAG)
        self.depth=self.ctx.depth_renderbuffer((renderer.w,renderer.h))
        self.fbo=self.ctx.framebuffer(color_attachments=[self.layer.t_paint],depth_attachment=self.depth)
        self.buf=self.ctx.buffer(reserve=6*4*200000,dynamic=True)
        self.vao=self.ctx.vertex_array(self.prog,[(self.buf,'3f 3f 1f','in_pos','in_normal','in_alpha')])
        self.topology={}
        self.costumes={}
        

    def draw_mesh(self,vertices,normals,tris,body,t):
        fade=np.ones(len(vertices),np.float32)
        if body.part:
            region=body.rig.bone_region[body.rig.vert_bone]
            side=1 if body.part.endswith('.L') else -1
            hand=(region==5)&(body.rig.side[body.rig.vert_bone]==side)
            center=body.rig.verts0[hand].mean(axis=0)
            d=np.linalg.norm(body.rig.verts0-center,axis=1)
            u=np.clip((d-.15)/.23,0,1);fade=1-u*u*(3-2*u)
        packed=np.concatenate([body._w(vertices,t),body._wdir(normals,t),fade[:,None]],axis=1)[tris].astype('f4').reshape(-1,7)
        if packed.nbytes>self.buf.size:self.buf.orphan(packed.nbytes)
        self.buf.write(packed.tobytes())
        self.vao.render(moderngl.TRIANGLES,vertices=len(packed))

    def draw(self,t,P):
        active=[]
        for name,group in self.film.bodies().items():
            if name=='hands0':continue
            for body in group if isinstance(group,(list,tuple)) else [group]:
                if hasattr(body,'gain') and body.gain(t)>.002:active.append(body)
        if not active:return
        cam=self.layer.rig.state(t,16/9)
        self.fbo.use();self.fbo.clear(0,0,0,0,depth=1)
        self.ctx.disable(moderngl.BLEND)
        self.ctx.enable(moderngl.DEPTH_TEST|moderngl.BLEND)
        self.ctx.blend_func=(moderngl.ONE,moderngl.ONE_MINUS_SRC_ALPHA)
        self.prog['vp'].write((cam.proj()@cam.view()).T.astype('f4').tobytes())
        self.prog['eye'].value=tuple(cam.pos)
        key=self.film.O.HEADS[self.film.O._lead_of(t) or 0](t)
        self.prog['light_pos'].value=tuple(key+np.array([0,4,2]))
        for body in active:
            if np.linalg.norm(body.where(t,'heart')-cam.pos)>55:continue
            gain=float(body.gain(t));self.prog['coverage'].value=.92*gain
            self.prog['tint'].value=(.68,.46,.24)
            verts,norm=body._skinned(t);tris=body.rig.tris
            # Long dresses cover the lower body; retain the feet below the hem.
            if body.garment=='dress':
                y=body.rig.verts0[:,1];keep=(y[tris].min(axis=1)>.59*body.rig.height)|(y[tris].max(axis=1)<.055)
                tris=tris[keep]
            region=body.rig.bone_region[body.rig.vert_bone]
            if body.part:
                side=1 if body.part.endswith('.L') else -1
                # Palms and fingers gain volume; the arm remains a soft trail of light.
                allowed=(region==5)&(body.rig.side[body.rig.vert_bone]==side)
                tris=tris[allowed[tris].all(axis=1)]
            off=np.where(np.isin(region,[2,3,4,6,7,8]),.014,.002)
            clothed=np.isin(region[tris[:,0]],[2,3,4,6,7,8])
            self.draw_mesh(verts+norm*.002,norm,tris[~clothed],body,t)
            if id(body.rig) not in self.costumes:
                from sol_edits.v4.costumes import fabric_rig
                self.costumes[id(body.rig)]=fabric_rig(body.rig)
            cv,cn=self.costumes[id(body.rig)].skin(body.actor.frame(t)['M'],True)
            self.prog['tint'].value=(.82,.67,.45)
            self.draw_mesh(cv,cn,tris[clothed],body,t)
            for pc in body.cloth.pieces if body.cloth is not None else []:
                if pc.strands:continue
                key=(pc.rows,pc.cols,pc.closed)
                if key not in self.topology:self.topology[key]=grid_triangles(*key)
                tri=self.topology[key];points=body.cloth.piece(pc.name,t).reshape(-1,3)
                ns=mesh_normals(points,tri)
                self.prog['tint'].value=(.82,.67,.45)
                self.draw_mesh(points,ns,tri,body,t)
        self.layer._painted=True
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.R.f_L.use();self.ctx.blend_func=(moderngl.ONE,moderngl.ONE)


def install(renderer,film):
    surfaces=Surfaces(renderer,film)
    original=renderer.p3d.draw
    def draw(self,t,P):
        original(t,P)
        surfaces.draw(t,P)
    renderer.p3d.draw=types.MethodType(draw,renderer.p3d)
    renderer.sol_surfaces=surfaces
