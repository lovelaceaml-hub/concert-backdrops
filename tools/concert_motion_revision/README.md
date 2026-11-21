# Consideration action revision

This isolated study revises two specific defects in the original eighteen-second Consideration working film: the people overlap in projection during the rise and release, and the recipient's returning hand makes an abrupt excursion beside the face. The comparison covers original scene time 3 to 18 seconds as 900 genuinely evaluated frames at native 1920x1080 and 60 fps, with two shutter samples. See `VERIFICATION.md` for the media that has actually completed and the remaining limitations.

## Boundaries

The implementation changes only a renderer instance's camera and the recipient actor instance's response. It preserves `engine/`, `tools/concert_kit/`, the registered project, the paired capture, the shared grip, the standing settlement, and the original eighteen-second movie inputs. The source check rejects any original kit identity other than `2fa9e0fce212be765d639fbb85acf8cdb755e5a92d995dae418fa66fbd7eae6e`.

This is a bounded action revision registered through the existing `p3d-kit` adapter, not a second scheduler or a complete concert-song scene. The fifteen-second excerpt includes the completed garden and the original closing expression, with the established corner logo. The original eighteen-second project remains separate and unchanged.

The native models, luminous people, cloth, original CMU performance, mirror water and vegetation come from the existing kit. The new contribution is the response interpolation and the camera coverage. No generated raster, stock footage, Mac rendering or cloud GPU provider is involved.

## Why the response changes

The original hand-on-heart gesture applies a fractional weight during a repeated arm-target solve. That is different from interpolating a complete rest pose toward a complete solved pose. The surrounding actor system also composes core and hand groups from differently timed gesture weights. The old rendered hand excursion survives disabling the living-wrist layer, so simply removing subtle finger motion would not address the observed defect.

`response.py` removes only the recipient's original hand-on-heart entry. It obtains the original neutral base pose, solves a copied endpoint at full weight, and quaternion-blends the complete poses with an explicit quintic envelope: enter from 9.4 to 10.2 seconds, hold through 11.5, return from 11.5 to 12.3. The original right-hand contact remains intact. Living hands remain enabled.

The world light still launches from the actual left palm sampled at scene time 11.5. Its subsequent path is deliberate world-space travel, not a light welded to the moving hand. Numerical continuity checks and native consecutive images are required before claiming the return is visually resolved.

## Reproduce

Use the existing pinned p3d environment and fonts. Keep the canonical eighteen-second prepared score at `work/concert-kit/consideration-score.wav`, SHA-256 `0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b`.

```bash
PYTHONHASHSEED=0 LP_NUM_THREADS=1 .venv/bin/python -m tools.concert_motion_revision.render \
  --stills 3,5.3,6.883333333333,6.9,7.5,10.7,11.533333333333,11.983333333333,12,12.3,17.5 \
  --out work/concert-motion-revision/native-probes

./scripts/video produce concert-kit-consideration-v2 --quality review --plan
./scripts/video produce concert-kit-consideration-v2 --quality review --frames 0,233,234,270,539,540,690,870,899
./scripts/video produce concert-kit-consideration-v2 --quality review

```

The final movie uses the existing registered production renderer, frame checkpoints, source fingerprints and finisher. Do not launch a parallel hand-written frame scheduler. The wrapper's `frame(renderer, output_index, fps=60)` maps output frames 0 through 899 exactly to original scene frames 180 through 1079. Output cuts at 3.9 and 9.0 seconds correspond to original times 6.9 and 12.0. The first contact camera is preserved until 6.9; the rise and response use a western view, then a wider view on the same side reveals the garden. Shutter sampling is kept within the correct shot.

All cache roots are redirected before the base renderer initializes. They live beneath `work/concert-motion-revision/cache/`, keyed by this revision's complete source identity. The required source manifest includes the original engine, kit, body asset, fonts and revision Python modules. A planning import does not initialize graphics.

## Audio and color

The proof crops the canonical score from 3 to 18 seconds, corresponding to original Song 07 recording time 140.5 to 155.5 seconds. It preserves playback speed and extracts exactly 720,000 stereo sample frames at 48 kHz. The registered project adds no extra fade; the canonical recording's existing ending fade is retained. The complete input and derived hashes are recorded by the production pipeline.

The established RGB8 display curve remains unchanged. Encoding applies BT.709 matrix and limited-range conversion only, with explicit primaries, transfer, matrix and range tags. It does not apply a second transfer function. Decoded review images invert only the matrix and range. Native 1080p60 does not imply HDR or a new native 60 Hz motion capture.

## Review and provenance

The verifier performs a complete decode, checks all 900 presentation timestamps, validates codec geometry and color tags, compares decoded audio with the prepared score, records peaks, and extracts actual encoded motion around the former defect. These establish technical delivery facts. Human action, silhouette clarity, contact and camera continuity still require visual review; owner approval remains separate.

Existing body, motion, fonts and campaign provenance remain in `tools/concert_kit/MODEL-CATALOG.md` and `assets/p3d/README.md`. Retain the motion acknowledgement: "The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217."
