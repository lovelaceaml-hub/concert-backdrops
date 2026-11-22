# Consideration: a hand that opens the world

An original eighteen-second scene built with the established native p3d renderer. Two warm gold men share an act of help beside a mirror lake. The complete paired captured action is followed by an authored acknowledgement, a pink light traveling into the shore, opening flowers and a willow canopy reveal. The ending resolves in the scene rather than stopping during a new shot.

This is a bounded model and animation proof for the concert production system. It extends the model library in [MODEL-CATALOG.md](MODEL-CATALOG.md). [REVIEW-NOTES.md](REVIEW-NOTES.md) explains the artistic decisions; [VERIFICATION.md](VERIFICATION.md) records the actual model checks, native key frames, contact measurements and benchmark. It does not replace an approved promo or Song 11 and does not certify that every animation issue in the underlying engine has been fixed.

## Timeline

| Time | Designed picture |
| --- | --- |
| 0 to 3 seconds | Moving discovery of a seated person and an approaching helper in the luminous shore environment |
| 3 to 9.5 seconds | The complete paired capture: approach, offered hand, acceptance, shared effort, rise and release |
| 9.5 to 11.5 seconds | The figures settle into mutual acknowledgement; the recipient places a hand on his heart |
| 11.5 to 12 seconds | A pink light leaves the posed hand |
| 12 to 18 seconds | The camera rises and retreats while light reaches the shore and canopy, flowers open and the exact Consideration words appear |

The chosen source audio is original Song 07 from 137.5 to 155.5 seconds, without time stretch. The source timeline describes a hush followed by a build at 149 seconds, corresponding to the scene's 11.5-second world response. That cue is informed by the source timeline, not claimed as an ear-verified sample-accurate transient. The sound is prepared and attached separately, with source provenance recorded in the production package.

## Render

Use the repository's locked legacy Python environment and project fonts. Rendering is configured for cloud CPU execution. No Mac, external GPU service, stock footage or AI raster generation is needed. The repeatable production route is the registered `p3d-kit` adapter in [`projects/concert-kit-consideration/project.json`](../../projects/concert-kit-consideration/project.json); the direct commands below are useful for model development and bounded inspection.

This package preserves the original eighteen-second baseline. For the separate corrected camera and response study, use `concert-kit-consideration-v2` and read [the revision instructions](../concert_motion_revision/README.md). The original source and its recorded defects remain available for comparison.

```bash
PYTHONHASHSEED=0 uv run --frozen --extra legacy python tools/concert_kit/render.py --stills 0,6,11,16.5 --out work/concert-kit/review
PYTHONHASHSEED=0 uv run --frozen --extra legacy python tools/concert_kit/render.py --fps 60 --range 0 1080 --out work/concert-kit/final/consideration-picture.mp4
PYTHONHASHSEED=0 uv run --frozen --extra legacy python tools/concert_kit/atlas.py --out work/concert-kit/atlas
```

`--width` and `--height` allocate the native frame size. Defaults are 1920x1080. The renderer also accepts native 3840x2160. A format being supported does not mean a complete movie at that format has been rendered or reviewed. `--fps 30` renders 540 distinct frames; `--fps 60` renders 1080 distinct frames. `--samples 2` evaluates two HDR moments inside the shutter, with the shutter disabled at camera cuts to avoid blending unrelated views.

Set `CONCERT_KIT_FONTS` if project fonts are not at the default path. In a fresh checkout of current source, run `python3 scripts/bootstrap.py --p3d-only --reference-fonts` to reconstruct the exact reference files. See [REFERENCE-FONTS.md](../../docs/REFERENCE-FONTS.md). Font bytes enter source identity; default conversion produces different bytes. Do not run font setup during a frozen render.

## Integration API

Importing `tools.concert_kit.render` does not create a graphics context. Its public functions are `make_renderer(width, height, temporal_samples=2, fps=60)`, `frame(renderer, global_index, fps=60)`, and `source_hashes()`. Frames are packed RGB8. `COLOR_CONTRACT.name` is `legacy_display_gamma`: preserve the renderer's display curve, convert RGB to limited-range BT.709 with matrix and range only, and tag primaries, transfer and matrix as BT.709. Do not apply a second sRGB or gamma conversion.

All final encoded chunks carry a source manifest and a checksum. Source changes during a range leave the `.assembling.mp4` incomplete rather than promoting it to a finished chunk. A `STOP` file in the output directory halts between frames. Derived caches live below `work/concert-kit`; the body cache namespace incorporates the actual body and relevant source bytes. A `P3D_BODY_ASSET` override is rejected before scene loading.

## Review gates

Inspect full-size contact and ending frames before a long render. Then review a dense sequence through the grip, rise, release, standing settle and both camera cuts. Verify actual encoded pictures and exact frame timing. Judge the action without words first, then check hand visibility, silhouette, planted feet, garment behavior, prop support, light causality and a resolved ending. Resolution and frame count are technical properties; they do not establish beauty or natural acting.

The neutral picture-preview envelope is explicitly named in the source. It supplies the legacy renderer's required scalar fields and is not a fabricated audio analysis. Human action and world events are authored on the chosen phrase; future full-song work should use verified cue sheets and the actual recording.
