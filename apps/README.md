# Browser scenes and finishing

Run these commands from the repository root after `npm ci`:

```bash
npm run preview
npm run editor
npm run typecheck
npm run build
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

The pavilion supports `shot.params.camera` values `orbit`, `push-in`, or `locked`, plus `shot.params.bloom` as a boolean. Its camera, ribbon motion, water rings, and particles are functions of the requested frame and seed. The studio controls preview these same parameters. Use the capture script to obtain the exact configured pixel dimensions.

To add a scene, add its explicit path to the capture registry and select its component in the app. There is no dynamic execution of a path provided by a manifest. Add new scene files to the shot dependency list for cache invalidation.

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

Direct final rendering on macOS is disabled unless `--allow-local-render` is passed. The Python orchestration layer also controls host rendering policy.

## Shotcraft Workbench

The `src/workbench.ts` export follows the upstream Workbench format and shares `src/timeline.ts` with the default Remotion composition. It is a two-shot editing study, not an import of the approved concert. The skill and Workbench source are installed by the repository bootstrap into the ignored vendor directory. Start Workbench explicitly with the documented project launcher; dependency installation alone does not start a server.

All Remotion packages are pinned to the Workbench-compatible `4.0.484`. Do not independently update one Remotion package. Imported production clip timelines are rendered via the JSON interface above; the example Workbench shot table is not overwritten by those jobs.
