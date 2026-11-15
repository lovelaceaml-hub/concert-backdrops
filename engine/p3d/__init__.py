"""The true 3D layer of the engine: a camera in space, point sprites with depth of field, a world with a
mirror lake. Switched on by the song key P3D; songs without it never load this package.

How a song uses it: engine/UPGRADE-HOWTO.md, section V. The API for point sets: engine/p3d/api.py.
"""
from .api import (KINDS, CameraState, Frame, Mask, Parented, PointSet, Scene, StandIn, Trail, at, hash01,  # noqa: F401
                  lin, normalize, ribbon, show)
