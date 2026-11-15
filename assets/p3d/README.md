# The human form for the particle bodies

`body_v1.npz` is what engine/p3d/body.py turns into people made of points. It is small (under 1 MB), it is
committed so that renders never download anything, and it holds two things from public sources:

| What | From | Licence |
|---|---|---|
| The body: the MakeHuman "hm08" base mesh, its default skeleton and skinning weights, and the shape targets for a woman, a man and a child | The PyPI wheel `anny` 0.6.2, folder `anny/data/mpfb2/` (the MPFB2 asset pack of the MakeHuman community) | CC0 1.0 Universal (public domain dedication). Stated in `anny/data/mpfb2/LICENSE.md`; the mesh file says "explicitly released as CC0 in september 2020" (copyright holders at that time: Data Collection AB, Joel Palmius, Jonas Hauquier); the weights file says `"license": "CC0"` (Copyright (C) 2025 NAVER Corp.) |
| Motion clips: walk, run, jump, dance, twirl, get up, and a pair captured together (one pulls the other up from sitting) | The CMU Graphics Lab Motion Capture Database, mocap.cs.cmu.edu, in the BVH conversion by Bruce Hahne (cgspeed, 2010 release), mirrored at github.com/una-dinosauria/cmu-mocap. Files: 35_01 (walk), 35_17 (run), 13_11 (jump), 05_02 (dance and twirl), 22_01 and 23_01 (pull up, helped up), 140_08 (get up) | CMU: "This data is free for use in research and commercial projects worldwide." The BVH conversion adds no restrictions ("CMU places no restrictions on the use of the original dataset, and I (Bruce) place no additional restrictions on the use of this particular BVH conversion"). CMU asks for this acknowledgement: The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217. |

Nothing else is used or stored.

## The motion data decision

The first clips were the DeepMimic reference motions (from the pybullet source distribution, zlib). DeepMimic
made them from the CMU and the SFU motion capture databases without saying which clip came from which, and the
SFU terms could not be verified, so every one of them was dropped (walk, run, jump, spin, two dances) and
replaced with CMU data only. The old motion names still work in song files: "spin" plays "twirl", "dance_a"
and "dance_b" play "dance".

## What was changed

`tools/build_p3d_body.py` and `tools/build_p3d_motion.py` are the exact record. In short:

- Body: the three shapes are made by adding the MakeHuman targets to the base mesh; the pockets inside the head
  (the mouth and the eye sockets) are removed and closed and the face is smoothed until no facial feature is
  left (a mannequin: a profile keeps only its outline); helper geometry is dropped; the bones of the face and
  the toes are folded into the head and the feet; units become metres with the soles on y = 0.
- Motion: each capture is turned to face +z, retargeted onto the MakeHuman skeleton by matching bone
  directions from the capture's T-pose frame (twist kept), resampled to 30 frames per second, and stored as
  rotations of 25 bones (float16), the root's path and two foot contact curves. Cycles (walk, run) are cut
  where the pose repeats best, made seamless, and their two legs levelled (the captured legs differ by about
  2 cm). Planted feet are held in place at render time (engine/p3d/actor.py), also while a walker turns.

## Rebuilding

    python tools/build_p3d_body.py
    python tools/build_p3d_motion.py

The first downloads the anny wheel from PyPI; the second the BVH files from the mirror (or give `--bvh DIR`
with files already on disk). Both need numpy only.
