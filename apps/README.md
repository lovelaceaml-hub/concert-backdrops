# Browser scenes and finishing

Run these commands from the repository root after `npm ci`:

```bash
npm run preview
npm run editor
npm run typecheck
npm run build
npm run test:motion
npm run test:browser
```

Both development applications bind to the current machine. They do not connect to a cloud GPU or upload media. Preview is a procedural tool demonstration, separate from the approved film.

## Frame capture

`node apps/scene-preview/capture.mjs --job /absolute/job.json` starts a temporary Vite server and Chromium process, captures PNGs, and closes both. The job schema is shared with the Python pipeline:

```json
{
  "project_id": "example",
  "shot": {"id": "opening", "name": "Light study", "renderer": "threejs", "start_frame": 0, "end_frame_exclusive": 60, "scene": "apps/scene-preview/src/scenes/Heavenly.tsx", "params": {"bloom": true}},
  "video": {"width": 640, "height": 360, "fps": 30},
  "seed": 2026,
  "frames": [0, 30, 59],
  "out_dir": "/absolute/output"
}
```

Frame numbers are absolute on the project timeline. Each frame is evaluated independently from its number, frame rate, shot start and seed. `renderer.json` records Chromium and WebGL renderer identity and output hashes. The browser smoke test checks repeated frames for equality after rendering other frames out of order. Different drivers or hardware can change shading.

Chromium uses SwiftShader intentionally for this CPU workflow. Install the pinned Playwright-managed headless shell with `npx playwright install chromium --only-shell` once, or set `CHROMIUM_PATH` to an approved compatible browser. `node apps/browser-path.mjs` reports the resolved path. `node apps/probe-browser.mjs --launch` verifies an actual browser launch and WebGL2 context, reports JSON, and never downloads anything. Native GPU rendering is not silently substituted. Browser downloads and local IPC must be allowed by the current environment; installing npm packages does not itself verify these capabilities.

The pavilion supports `shot.params.camera` values `orbit`, `push-in`, `fly-through`, or `locked`, plus `shot.params.bloom` as a boolean. Its camera, ribbon motion, water rings, and particles are functions of the requested frame and seed. The studio controls preview these same parameters. Use the capture script to obtain the exact configured pixel dimensions.

To add a scene, add its explicit path to the capture registry and select its component in the app. There is no dynamic execution of a path provided by a manifest. Add new scene files to the shot dependency list for cache invalidation.

## Natural motion and authored musical phrasing

`apps/shared/motion.mjs` is the shared Three.js and Remotion motion library. It evaluates every pose directly from elapsed seconds or the absolute timeline frame. It has no accumulated spring state, frame delta, wall clock, or random calls during frame sampling. The Node tests exercise motion mathematics without needing Chromium or a GPU:

```bash
node --test apps/shared/motion.test.mjs
```

The browser study now uses a natural cubic camera spline, a quintic arrival/settle curve, slow secondary motion with independent seeded phases, and authored musical envelopes. Camera position, velocity and acceleration are continuous at internal spline joins. Whole-shot `smootherstep` also brings velocity and acceleration to zero at the outer endpoints. This is mathematical continuity, not a claim that every authored path has attractive speed, avoids objects, or gives good framing. Preview the actual scene and inspect dense frame strips before approval.

A custom camera track overrides the named preset:

```json
{
  "camera": "push-in",
  "camera_path": {
    "points": [[1.9, 5.2, 16], [1.85, 5.05, 14.9], [1.7, 4.85, 13.8], [1.55, 4.65, 12.7]],
    "targets": [[0, 2.2, -1.3]],
    "seconds": [0, 2, 4, 6],
    "easing": "smootherstep",
    "roll_degrees": [0, 0]
  },
  "motion_amount": 0.8,
  "music_amount": 0.12,
  "bloom": true
}
```

`points` are interpolated waypoints in Three.js metres with **Y up**. Blender uses **Z up**, so transfer coordinates explicitly. `targets` contains one fixed look target or one per point. `seconds` must be finite and strictly increasing. If omitted, the app spaces points uniformly over the shot duration. A track holds its first and last poses outside the provided interval. Natural splines may curve beyond their waypoint bounds, so leave clearance around geometry.

`linear` easing preserves the supplied knot times. `smootherstep` warps the whole interval once: it eases the complete move instead of stopping at every waypoint, and interior waypoint arrival times shift. It is not constant-speed or arc-length motion. The optional `pacing` field only accepts `waypoints`. A moving `linear` track needs matching neighboring-shot velocities if a continuous camera move spans a cut. `roll_degrees` is an optional browser-only start/end pair. Nearly vertical or coincident look targets are rejected to avoid a horizon flip.

`motion_amount` ranges from 0 to 2 and controls the study's gentle drift. `music_amount` ranges from 0 to 1 and controls small ribbon and water-ring responses. Musical cues do not change global exposure or bloom. The study's motion clock eases into and out of the shot, so the final frames settle instead of snapping into a freeze.

Music remains an authored timing file. Its event frame is the intended **peak**; the attack anticipates the peak, and the release settles after it:

```json
{
  "fps": 60,
  "events": [
    {"frame": 360, "kind": "phrase", "amplitude": 0.8, "attack_frames": 120, "release_frames": 180},
    {"frame": 540, "kind": "accent", "amplitude": 0.3, "attack_frames": 15, "release_frames": 72}
  ]
}
```

The pavilion responds to `phrase`, `accent`, and `swell`. An event with no attack/release values defaults to about 0.25 seconds of attack and 1.2 seconds of release, rounded to whole frames. Event envelopes have zero velocity and acceleration at their start, peak and end. Overlap is additive unless a cap is requested. The study uses a smooth cap of 1, with a quintic transition between half the cap and the cap; values in that transition are gently remapped. This prevents the derivative discontinuity of clipping the sum with a hard minimum. Exact timing must still be checked against the approved audio.

`apps/shared/shot-templates.mjs` exports three original reusable templates: `reveal`, `procession`, and `resolve`. `createShotTemplate(name, {start_frame, duration_frames, fps})` creates the scene/path parameters. `createPhraseEvents({start_frame, peak_frame, end_frame_exclusive, fps})` creates a phrase from three explicit editorial anchors. It does not detect beats, invent music, or alter an approved timeline. Both the preview demo and Remotion title movement consume the shared motion library.

## Finishing rendered clips

`node apps/editor/render.mjs --input /absolute/props.json --output /absolute/master.mp4` bundles a temporary Remotion application, validates each video with FFprobe, renders, then removes temporary copies. It accepts:

```json
{
  "title": "Concert study",
  "width": 1920,
  "height": 1080,
  "fps": 60,
  "durationInFrames": 600,
  "clips": [
    {"src": "/absolute/first.mp4", "start_frame": 0, "end_frame_exclusive": 300},
    {"src": "/absolute/second.mp4", "start_frame": 300, "end_frame_exclusive": 600}
  ],
  "audio_src": "/absolute/approved-soundtrack.wav",
  "show_title": false,
  "captions": [{"text": "A sample title", "start_frame": 0, "end_frame_exclusive": 240}]
}
```

The audio field is optional. The pipeline never generates a soundtrack. Clips must exactly match the output dimensions, frame rate and their assigned frame counts. Each source starts at its own frame zero. Clips are joined with clean cuts; no automatic transition changes shot timing. `show_title` defaults off so assembly preserves already approved titles. Text is composited above footage, never generated inside imagery. Every audio source must already include any intended offset, trim or fade.

The browser finisher uses lossless PNG captures, explicitly converts full-range sRGB pixels to limited-range Rec.709 with BT.1886 display gamma 2.4, and encodes software H.264 High with 8-bit `yuv420p`. This is display-referred output for rendered imagery; it does not apply a camera capture OETF. Audio, when present, is AAC at 48 kHz. The final stream-copy mux preserves the encoded video instead of applying color conversion a second time. `node --test apps/editor/delivery.test.mjs` checks a tiny real encode, metadata and the expected converted mid-gray value; it does not need Chromium. High-bit-depth intermediates and final delivery use the pipeline's frame-sequence encoder. A 4K canvas preserves native output dimensions, but changing this setting cannot add detail that is missing from source geometry or turn an 8-bit browser capture into a 16-bit source.

The display transform follows [zimg's Rec.709 transfer implementation](https://github.com/sekrit-twc/zimg/blob/master/src/zimg/colorspace/gamma.cpp), which selects BT.1886 for display-referred operation. The pinned Remotion launcher forces the sRGB browser profile; the Three.js capture launcher does so explicitly as well.

Direct final rendering on macOS is disabled unless `--allow-local-render` is passed. The Python orchestration layer also controls host rendering policy.

## Shotcraft Workbench

The `src/workbench.ts` export follows the upstream Workbench format and shares `src/timeline.ts` with the default Remotion composition. It is a two-shot editing study, not an import of the approved concert. The skill and Workbench source are installed by the repository bootstrap into the ignored vendor directory. Start Workbench explicitly with the documented project launcher; dependency installation alone does not start a server.

All Remotion packages are pinned to the Workbench-compatible `4.0.484`. Do not independently update one Remotion package. Imported production clip timelines are rendered via the JSON interface above; the example Workbench shot table is not overwritten by those jobs.
