# Thirty-second people animation example

An isolated proposal requested on November 20, 2026, after the ten-second Earth
design example. This demonstrates actual human performance in the approved
promo's warm gold people-of-light style. It is not a revision of the approved
66-second film or a record of creative approval.

## The scene

The first shot follows two men approaching and settling, exchanging small bows,
and responding with a relaxed hand gesture and a hand near the heart. The next
shot shows a conductor facing a small choir. The final shot cranes back as the
choir opens its hands and colored light forms a canopy behind the group.

The final wide shot contains eleven people: the two principal actors,
one conductor and eight choir members. The choir uses three independently posed
human prototypes, with different placement, orientation, scale and brightness.
The foreground shot isolates the pair so cropped background bodies do not
intrude at the edge of the picture.

The edit cuts at frames 612 and 1168, approximately 10.2 and 19.467 seconds, near
the existing score's breath and finale entry. Camera movement is eased within
each shot. The final composition continues to move gently without fading black.

## Human assets and movement

The example reuses the project's actual MakeHuman human forms, articulated
skeleton, fingers, clothed body sampler and CMU walk data from
`assets/p3d/body_v1.npz`. It does not use primitive capsule stand-ins. The
existing engine implements planted-foot walking, gesture anticipation and
settling, breathing, head motion and cloth simulation. Its protected files are
read without modification.

New choreography is confined to `people.py`. The conductor's world-space hand
targets create an asymmetric gesture with wrist lag. Choir hand targets remain
inside each singer's space. The sample demonstrates whole-body and hand motion;
it does not add detailed facial acting or mouth synchronization.

The figure and motion provenance is documented in `assets/p3d/README.md`.
Acknowledgement retained from that record: The data used in this project was
obtained from mocap.cs.cmu.edu. The database was created with funding from
NSF EIA-0196217.

## Visual and audio construction

- Fine warm particles form the people and the folds of their clothing. There
  are no realistic faces, metallic figures, generated images or stock footage.
- A violet terrace establishes foot contact above rose and gold clouds. The
  canopy stays behind and above the group; it does not cross their faces.
- Opening and closing information use existing fonts and the exact campaign
  logo. The greeting caption has separate headroom. Text is composited after
  glow, and all type is drawn at the delivery size.
- Music is seconds 30 through 60 of the original medley. A 0.35-second entry
  fade softens the excerpt's start; its natural final release is retained.
  The source audio is never modified. No music is generated.

## Reproduce on a cloud CPU

From the repository root after the locked bootstrap:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
uv run --frozen --extra legacy python tools/promo_people_example/build.py \
  --workers 3 --width 1920 --height 1080 \
  --directory work/promo-people-example/final
```

Use a new output directory for a new review round. The same native renderer
accepts `--width 3840 --height 2160`; the completed export measurements in
`VERIFICATION.md` distinguish delivered movies from still checks.

Six small cloth systems are baked through 31 seconds before rendering, stored
only under ignored `work/`, and checked against source, asset and dependency
fingerprints. Each worker reads matching snapshots so later chunks do not have
to rerun the complete simulation. A missing or mismatched cache is regenerated.
The cache contains data arrays, not pickled executable objects.

The movie has 1,800 native frames at 60 fps. Two real scene evaluations per frame
are accumulated in linear light across a half-frame shutter; samples are clamped
inside their shot so an editorial cut does not blend two cameras. The viewing
copy is H.264 High, 8-bit Rec.709 SDR with stereo AAC. There is no video upscaling
or AI frame interpolation. This example does not claim HDR or 10-bit delivery.

The builder renders six independent 300-frame parts. Source, locked dependency,
Python/package, FFmpeg and software GL identities are checked for cache reuse.
Completed outputs replace temporary siblings only after encoder and stream
validation succeeds. The part checksum guard prevents a mismatched receipt
from being reused if a process stops between movie and receipt replacement.

The recipe rejects Darwin execution. It configures no cloud GPU provider,
starts no paid workflow, and never renders on the owner's Mac.

## Review and verification

To inspect selected native frames:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
uv run --frozen --extra legacy python tools/promo_people_example/render.py \
  --stills 0,3.8,7,8.8,12.5,15,24,29.983 \
  --out work/promo-people-example/stills
```

The separate delivery verifier decodes every frame and timestamp, checks the
audio, scans temporal differences around declared cuts, and compares an actual
decoded native frame with its exact source PNG:

```bash
uv run --frozen --extra legacy python tools/promo_people_example/verify.py \
  --movie work/promo-people-example/final/Mothers-Love-People-Animation-30s-1080p60.mp4 \
  --reference work/promo-people-example/stills/frame-0900.png \
  --frame 900 --output work/promo-people-example/final/qa
```

Frame strips and native stills must also be reviewed for anatomy, readable
gestures, text clearance and composition. Numerical continuity checks do not
prove natural acting or creative approval. `VERIFICATION.md` records the actual
checks performed on the delivered file.
