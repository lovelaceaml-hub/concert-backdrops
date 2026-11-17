"""Soft contact shadows and quietly falling three dimensional flower petals."""
import numpy as np
import moderngl

SHADOW_VS='''#version 330
in vec2 xy;out vec2 q;
uniform mat4 vp;uniform vec3 center;
void main(){q=xy;gl_Position=vp*vec4(center+vec3(xy.x*.36,.005,xy.y*.25),1);}
'''
SHADOW_FS='''#version 330
in vec2 q;out vec4 frag;uniform float gain;
void main(){float a=.30*gain*exp(-3.5*dot(q,q));frag=vec4(vec3(.06,.045,.025)*a,a);}
'''

class Atmosphere:
    def __init__(self,ctx):
        self.ctx=ctx
        self.prog=ctx.program(vertex_shader=SHADOW_VS,fragment_shader=SHADOW_FS)
        buf=ctx.buffer(np.array([[-2,-2],[2,-2],[-2,2],[2,2]],'f4').tobytes())
        self.vao=ctx.vertex_array(self.prog,[(buf,'2f','xy')])
        r=np.random.default_rng(781)
        self.base=np.stack([r.uniform(-6,6,64),r.uniform(.4,5,64),r.uniform(-8,2,64)],1)
        self.phase=r.uniform(0,2*np.pi,64);self.size=r.uniform(.018,.045,64)
        th=np.linspace(0,2*np.pi,12,endpoint=False)
        self.rim=np.stack([np.cos(th),np.sin(th),.2*np.sin(th)**2],1)
        self.tris=np.stack([np.zeros(12,int),np.arange(1,13),np.roll(np.arange(1,13),-1)],1)
    def shadows(self,bodies,t,cam):
        self.prog['vp'].write((cam.proj()@cam.view()).T.astype('f4').tobytes())
        for body in bodies:
            self.prog['center'].value=tuple(body.where(t,'ground'))
            self.prog['gain'].value=float(body.gain(t))
            self.vao.render(moderngl.TRIANGLE_STRIP)
    def petals(self,t,origin):
        center=self.base+origin
        center[:,0]+=.15*np.sin(.35*t+self.phase)
        center[:,1]=origin[1]+.4+(self.base[:,1]-.085*t)%5
        center[:,2]+=.12*np.cos(.3*t+self.phase)
        theta=.3*t+self.phase
        vertices=[];normals=[]
        for j,c in enumerate(center):
            p=np.concatenate([np.zeros((1,3)),self.rim],0)*self.size[j]
            p[:,1]*=1.65
            x=p[:,0].copy();z=p[:,2].copy()
            p[:,0]=x*np.cos(theta[j])+z*np.sin(theta[j]);p[:,2]=-x*np.sin(theta[j])+z*np.cos(theta[j])
            vertices.append(p+c);normals.append(np.tile([np.sin(theta[j]),0,np.cos(theta[j])],(13,1)))
        return np.concatenate(vertices),np.concatenate(normals),np.concatenate([self.tris+13*j for j in range(len(center))])
