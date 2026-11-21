# Independent native model prototypes

These are original procedural models for the existing p3d language of points, lines and light. They are **prototypes awaiting owner review**. Their existence does not establish a new approved song design. They do not change the approved promo, the Song 11 beauty source, or the Consideration study.

The current appearance pack is **v2**, with a narrower dove torso, smaller head, distinct neck and beak, reduced inner feather light and a three-quarter proof camera. Constructor API IDs remain at revision 1. The original **rig baseline v1** is separately preserved with its own source map, source archive and movie hash. Do not attach that older movie to the modified current sources. See [VERIFICATION.md](VERIFICATION.md) for both identities.

The immediate additions are an articulated dove for Song 09, a layered rose for Song 02 and a wheat clump for Song 06. Each can be reused elsewhere when the song's human story calls for it. The six-second silent flight scene is a model and motion proof, not a finished concert backdrop.

## Public constructors

```python
from tools.concert_addons import Dove, Rose, Wheat, build_model

dove = Dove(
    at=(-1.1, 0.9, 0.25),
    land_at=(1.35, 1.02, -1.2),
    launch=0.8,
    land=4.9,
    scale=1.4,
    seed=9,
)
rose = Rose(at=(0, 0, 0), height=0.9, radius=0.15, variant="blush", bloom_at=0.9)
wheat = Wheat(at=(0, 0, 0), count=11, height=1.0, radius=0.25, variant="ripe", seed=6)
another_rose = build_model("rose", variant="golden", seed=4)

scene.add("dove", dove)
scene.add("rose", rose)
scene.add("wheat", wheat)
```

All three implement `sample(absolute_seconds)` and return native p3d batch dictionaries. Units are metres, the Y axis points up, and the dove's local forward axis is positive Z. There is no per-frame state to advance. A frame at any song time can be rendered independently. Seeds choose persistent geometry or phase offsets and never introduce frame-by-frame random noise.

`anchors(t)` exposes named world-space contacts for integration and checks. Dove `at` and `land_at` identify the centre between its feet at the launch and landing perch. Rose `at` identifies its root. Wheat exposes every root and head. `geometry.LineSet` is a small native line-batch adapter for original supporting curves.

## What the motion actually does

**Dove.** A brief head turn and crouch prepare the launch. Two articulated wings have separate shoulder, elbow and wrist transforms, attached primary and secondary feather surfaces, a small wrist delay and a fan of tail feathers. The bird climbs along an authored cubic curve, reduces wing beating for a glide, extends its feet and tail during the approach, then folds the wings after contact. The feet stay fixed on the launch perch during preparation and on the destination perch during settling. Short quintic release and contact blends avoid a discontinuity at the two events.

The flight curve is authored motion, not aerodynamic simulation. The current default path and camera are a compact demonstration. Shoulder placement, feather anatomy and flight cadence need further owner review before a large close-up or flock is used in a song. At present, each bird follows one launch-to-landing event; a multi-event schedule needs a separate authored instance or future action controller.

**Rose.** Thirty-two independently arranged petal patches form four layers around the stem. Each patch has actual three-dimensional curvature, surface samples and a contour. The opening is a three-second quintic transition from the requested `bloom_at`. Leaves and flower head stay attached to the bent stem. Blush, crimson and golden are original palette variants; no specific rose cultivar is claimed.

**Wheat.** Every stem carries eight pairs of ellipsoid grains and individual awns. The roots remain stationary while the stems bend in one traveling spatial wind field. Height, root placement and head orientation come from the fixed seed. Ripe and green variants share the same structural geometry. There is no claim of agricultural species accuracy or physical plant simulation.

## Repeat the native proof

Use the locked project Python environment on a cloud CPU. Prepare the pinned fonts through the normal project setup first. These commands do not dispatch a paid provider or use a Mac.

```bash
PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m tools.concert_addons.verify \
  --out work/concert-addons/art-v2/geometry-verification.json

PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m tools.concert_addons.render \
  --scene flight --stills 0,1.65,2.8,4.55,5.7 \
  --out work/concert-addons/art-v2/reproduced-stills

PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m tools.concert_addons.render \
  --scene rose --stills 0,4.5 --out work/concert-addons/art-v2/reproduced-stills

PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m tools.concert_addons.render \
  --scene wheat --stills 2.8 --out work/concert-addons/art-v2/reproduced-stills

PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m tools.concert_addons.render \
  --scene flight --range 0 360 --fps 60 --samples 2 \
  --out work/concert-addons/art-v2/dove-flight-v2-reproduced-6s-1080p60.mp4
```

The default image size is native 1920 by 1080. Two temporal samples are evaluated at subframe times inside the established renderer. The video encoder preserves its display curve, performs the BT.709 matrix and limited-range conversion, and explicitly sets primaries, transfer, matrix and range tags. Inspect the actual decoded result; tags alone do not verify appearance. A native 4K output is exposed by the width and height options but is not claimed as delivered by this prototype.

Use a fresh Python process for each scene and render configuration. The established renderer captures song settings when it imports its modules. The separate CLI commands above keep those configurations isolated; changing scene or output rate inside an already initialized interpreter is not a supported workflow.

All caches and previews live in ignored `work/concert-addons/`. Creating `work/concert-addons/STOP` stops a running movie before its next frame. This small proof CLI records source hashes and rejects a changed source at completion. It does not implement the production pipeline's per-frame recovery. Register the scene through that existing scheduler before a long render or distributed delivery.

Choose a new output directory after a source revision. Preserve earlier receipts and their exact media together. In particular, the root-level `dove-flight-6s-1080p60.mp4` is the historical rig baseline v1 and must not be overwritten with v2 pictures.

## Provenance and license scope

`models.py`, `geometry.py`, the supporting branch geometry and the proof composition were authored for this repository from mathematical primitives. No stock footage, photo tracing, AI-generated raster, downloaded mesh or external motion capture was used in these new models. No real church or other identifiable building is modeled here.

The pack reuses the repository's existing p3d engine and pinned fonts. Their existing dependency and font license records continue to apply. This pack contains no new third-party visual asset. It does not grant a separate public license for the private project code. See [catalog.json](catalog.json) for exact constructor and status metadata and [VERIFICATION.md](VERIFICATION.md) for the actual rendered evidence.
