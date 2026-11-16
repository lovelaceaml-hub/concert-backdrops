"""Smooth, opaque, long-sleeved costume shells on the shared animated rig."""
import copy
import numpy as np
from scipy.sparse import coo_matrix


def fabric_rig(rig):
    clothed=copy.copy(rig)
    tri=rig.tris
    a=np.concatenate([tri[:,0],tri[:,1],tri[:,2],tri[:,1],tri[:,2],tri[:,0]])
    b=np.concatenate([tri[:,1],tri[:,2],tri[:,0],tri[:,0],tri[:,1],tri[:,2]])
    adj=coo_matrix((np.ones(len(a)),(a,b)),shape=(len(rig.verts0),len(rig.verts0))).tocsr()
    degree=np.maximum(np.asarray(adj.sum(axis=1)),1)
    region=rig.bone_region[rig.vert_bone]
    mask=np.isin(region,[2,3,4,6,7,8])
    points=rig.verts0.copy()
    # Remove anatomical surface detail under the fabric while retaining fit.
    for _ in range(24):
        average=(adj@points)/degree
        points[mask]=points[mask]*.65+average[mask]*.35
    normal=rig._vertex_normals(points)
    points[mask]+=normal[mask]*.018
    clothed.verts0=points
    clothed.normals0=rig._vertex_normals(points)
    return clothed
