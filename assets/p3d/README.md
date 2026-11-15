# The human form for the particle bodies

`body_v1.npz` is what engine/p3d/body.py turns into people made of points. It is small (under 1 MB), it is
committed so that renders never download anything, and it holds two things from public packages:

| What | From | Licence |
|---|---|---|
| The body: the MakeHuman "hm08" base mesh, its default skeleton and skinning weights, and the shape targets for a woman, a man and a child | The PyPI wheel `anny` 0.6.2, folder `anny/data/mpfb2/` (the MPFB2 asset pack of the MakeHuman community) | CC0 1.0 Universal (public domain dedication). Stated in `anny/data/mpfb2/LICENSE.md`; the mesh file says "explicitly released as CC0 in september 2020" (copyright holders at that time: Data Collection AB, Joel Palmius, Jonas Hauquier); the weights file says `"license": "CC0"` (Copyright (C) 2025 NAVER Corp.) |
| Motion clips: walk, run, jump, spin, two dances | The PyPI source distribution `pybullet` 3.2.7, folder `examples/pybullet/gym/pybullet_data/data/motions/` (files `humanoid3d_*.txt`) | zlib licence (the Bullet Physics SDK's LICENSE.txt: "The files in this repository are licensed under the zlib license"). The clips are the DeepMimic reference motions (Peng, Abbeel, Levine, van de Panne 2018; the DeepMimic repository is MIT licensed). Stored here in altered form (as float32 arrays), which this notice marks plainly as the zlib licence asks |

Nothing else from those packages is used or stored.

## What was changed

`tools/build_p3d_body.py` is the exact record. In short: the three shapes are made by adding the MakeHuman
targets to the base mesh; the pockets inside the head (the mouth and the eye sockets) are removed and closed
and the face is smoothed until no facial feature is left (a mannequin: a profile keeps only its outline);
helper geometry is dropped; the bones of the face and the toes are folded into the head and the feet; units
become metres with the soles on y = 0.

## Rebuilding

    python tools/build_p3d_body.py

downloads the two packages from PyPI into a temporary folder and writes `assets/p3d/body_v1.npz` again
(needs numpy only).
