# Song 11 beauty study

A thirty-second native render of the actual Song 11 world, with isolated lens and delivery improvements. This replaces the previous example's sparse presentation stage with the original production's conductor, orchestra, responsive light, Zion, reflections and cinematic cameras.

Read [DESIGN-REVIEW.md](DESIGN-REVIEW.md) for the artistic diagnosis. Read [VERIFICATION.md](VERIFICATION.md) for the delivered artifact, measured results and the precise scope of the visual review.

## What this example is

The picture uses source scene time **97.7 to 127.7 seconds**. The audio uses **97.8 to 127.8 seconds**, retaining the production's existing 0.1 second picture delay exactly once. Nine existing shot blocks are evaluated at fresh 60 fps output times. This is a contiguous quality excerpt, ending during the next scene's arrival. The performance and edit are reused from the actual production; they are not a newly choreographed short story.

| Example time | Existing scene |
| --- | --- |
| 0.00 to 1.70 | Hero conductor releases the braided streams |
| 1.70 to 5.90 | Light spreads across the people and terraces |
| 5.90 to 7.45 | Golden waterfall |
| 7.45 to 10.70 | Articulated orchestra and choir |
| 10.70 to 12.10 | Church of light |
| 12.10 to 19.30 | Rising light column, lanterns and city reveal |
| 19.30 to 23.63 | Quiet conductor phrase and falling light |
| 23.63 to 28.23 | Renewed string gestures and traveling ribbons |
| 28.23 to 30.00 | Beginning of the sky-light and procession scene |

Cuts are quantized to the first output frame at or after each authored cue. The machine-readable build plan records both the exact source cue and the resulting frame.

## Bounded changes

- Preserve the frozen approved renderer, scene models, existing choreography, music cues, camera paths, original typography, emblem and logo.
- Focus conductor shots on the performer's chest at 1.45 m with aperture 0.012. The original composition looks toward the ribbons and distant city; the new lens focus keeps the performer readable within that composition.
- In stage shots only, reduce sun intensity and rays to 0.65, sun glow and final bloom to 0.75, and cap aperture at 0.008. This reduces the warm veil around the blue performers and gold instruments while retaining the musical crest.
- Use two temporal samples of moving point sets in the existing linear HDR light pass, with the original 0.35-frame shutter. Set the shutter to zero on frames that would span a camera cut.
- Remove the final shader's tiny added grain. No global denoising or sharpening is applied.
- Keep every particle rather than enabling the renderer's draft reduction. Native dimensions are allocated directly; no finished video is enlarged and no intermediate frames are invented.

All variations happen in `render.py`'s isolated process. The approved renderer and Song 11 source files are unchanged.

## Repeatable execution

Use the repository's existing locked cloud bootstrap for system dependencies and fonts. The relevant font setup is `tools/setup_fonts.py node_modules/@fontsource fonts`, after the locked npm packages are installed. The example requires FFmpeg with libx264, the locked Python legacy dependencies, and the original private recording. It does not require a GPU provider, Blender bridge, browser capture, or a local Mac.

From the repository root:

```bash
uv sync --frozen --extra legacy
git fetch origin d928ff9eafe02ac3150f0c646bdcc497fe5a7278
git fetch origin f43f4514e4bc42dc25166e90160d98219f5a0db4
uv run --frozen --extra legacy python tools/promo_beauty_example/prepare.py --audio /absolute/path/to/original-song11.mp3
uv run --frozen --extra legacy python tools/promo_beauty_example/build.py --plan
```

Preparation verifies the original recording's SHA256 before restoring the two pinned engine packages and preparing the score. The audio and generated caches remain in ignored work directories. Do not commit a full song, rendered frames or movies.

Inspect actual native frames before freezing a render round:

```bash
PYTHONHASHSEED=0 uv run --frozen --extra legacy python tools/promo_beauty_example/render.py --stills 45,501,900,1236,1476,1740 --out work/promo-beauty-rebuild/review
```

Build the complete example with two workers. The first four-worker attempt on the approximately 9.7 GiB cloud machine lost a worker to SIGKILL as memory demand increased, so four workers are not a validated setting for this scene:

```bash
PYTHONHASHSEED=0 uv run --frozen --extra legacy python tools/promo_beauty_example/build.py --workers 2
```

The build creates six independently rendered chunks. It reuses a chunk only when the source hashes, runtime, dimensions, temporal samples, exact frame range and movie checksum match. A failed worker stops its siblings. Audio is trimmed without retiming, with a 0.12 second entry fade, 0.25 second exit fade and 0.5 dB of headroom before AAC encoding. `--audio-gain-db 0` preserves the original excerpt level. The original recording and prepared score remain unchanged. Assembly copies the encoded pictures and adds AAC audio.

Longer expected jobs run first, while assembly always uses chronological frame order. Workers check a `STOP` marker in the output directory before initialization and between frames. Stop the coordinator too if cancellation arrives during final audio or movie assembly. Remove that marker only when intentionally resuming the requested round.

Verify the delivered pixels rather than trusting the render settings:

```bash
uv run --frozen --extra legacy python tools/promo_beauty_example/verify.py --movie work/promo-beauty-rebuild/final/Song11-Beauty-Study-30s-1080p60.mp4 --output work/promo-beauty-rebuild/final/qa --reference work/promo-beauty-rebuild/review/frame-0045.png --frame 45
```

The verifier checks the native dimensions, frame count, timestamps, color tags and audio; decodes every frame; saves full-size evidence and a contact sheet; and measures clipping and cut-aware changes. Its motion and flicker measurements are review aids. They do not certify expressive acting or aesthetic approval.

### Static assets and derived caches

Future source manifests include both pinned `body_v1.npz` files and the land map at `assets/p3d/brand/land_2048.png`. Missing files stop rendering. Crowd prototypes use a fresh cache namespace derived from both body digests, in addition to the original prototype keys. Changing a body asset therefore cannot silently reuse prototypes made from different body bytes. The renderer rejects `P3D_BODY_ASSET` overrides before loading either engine.

The delivered movie's pictures were rendered from commit `a7d68836c4fdc7156bbc9b839380cd65180ca2bb`, before this integrity follow-up. The three asset files were independently checked against pinned Git blobs and remained unchanged through completion. The follow-up does not retroactively strengthen that historical manifest. Its native-frame comparison is recorded in [VERIFICATION.md](VERIFICATION.md).

## Native 4K

The same adapter accepts `--width 3840 --height 2160` for stills and builds. It initializes legacy text textures at 4K before creating the renderer, in addition to allocating the world buffers at 4K. One native 4K conductor frame has been rendered and inspected in this round. A complete 4K movie has not been produced by that still test.

```bash
PYTHONHASHSEED=0 uv run --frozen --extra legacy python tools/promo_beauty_example/render.py --width 3840 --height 2160 --stills 45 --out work/promo-beauty-rebuild/native-4k
```

More output pixels improve edges and point detail. They do not add geometry to a simplified building or create a better acting performance. Dense architecture, clouds and layered transparent light can remain expensive on a CPU.

## Color, motion and provenance limits

The scene renders through half-float HDR working buffers, then the original filmic and display treatment produces RGB8. The delivery deliberately preserves the original RGB-to-Rec.709 YUV matrix/range convention. It is an **8-bit SDR** H.264 file, not an HDR or true high-precision 10-bit master. The verifier uses the matching inverse matrix/range conversion when comparing decoded frames with native PNGs.

Camera, hero, world and particle state are sampled at native output times. Existing crowd prototypes are baked at 15 fps and interpolated. Sixty output frames per second therefore improve temporal presentation without replacing the source crowd acting. Cross-process probes matched exactly at one tested time and within one 8-bit level at another; bitwise identity for every possible frame history is not asserted.

The original recording checksum matches the production record. The archived analysis maps and completed Song 11 master were behind a sign-in page. This round regenerates the maps from the verified recording with the project scripts. Their hashes differ from the archived maps, and automatic tempo or instrument estimates are not treated as manual timing truth. Existing authored absolute cues remain authoritative.

The available approved promo was inspected visually. Song 11's account and scene code were read, and new frames were rendered from them. This example is a new source reconstruction with documented improvements, not a claim to reproduce the exact delivered master byte for byte.

## Source identities

- Production account: `34f835206dcb26cfa0bd7e321171d3d224e3aa7d`, PR #100.
- Frozen approved renderer: `d928ff9eafe02ac3150f0c646bdcc497fe5a7278`.
- Original people and words package: `f43f4514e4bc42dc25166e90160d98219f5a0db4`.
- Original recording SHA256: `70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004`.

Preparation and delivery JSON files retain the regenerated map hashes, actual adapter and scene file hashes, runtime versions, media checksums and output parameters. Creative approval remains the user's decision.
