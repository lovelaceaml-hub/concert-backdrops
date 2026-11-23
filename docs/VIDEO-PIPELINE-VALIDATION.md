# Video pipeline setup verification

## Current verification: GitHub cloud runners, November 22, 2026

The supported tool demonstrations now run on a GitHub Actions cloud runner
(Ubuntu 24.04, CPU only). Exact PR #116 head
`285df02e51cc68073fe17c8a06ae0d7f54737df7` passed
[run 45125796332](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45125796332):
all eight original tool outcomes and all three jobs succeeded. The actual
outcome summary was checked because tool steps use `continue-on-error`.
Chat sandbox restrictions on browser sockets, Xvfb and Docker do not describe
these GitHub runner results. Workbench interactive browser playback/export was
not exercised in that run (it was proved later; see the table); Docker was built without a container execution proof. Short
technical demonstrations do not establish all-song quality or approved 4K
show output. The tool run used Python 3.12.16; the retained Song 11 film keeps
its separate Python 3.12.14 producing contract.

| Tool | Result on a GitHub runner | Proof |
| --- | --- | --- |
| Setup (`scripts/bootstrap.py`: Blender, browser, apps, integrations) | Works | Blender download cached between runs, retried if the site refuses a runner |
| Browser doctor | Works | No errors or warnings |
| Three.js scene capture (`npm run test:browser`) | Works | Real animated frames, out-of-order frame identity checked |
| Pipeline preview render (`pipeline-demo`) | Works | MP4 assembled and QA passed |
| Remotion assembly (`--editor remotion`) | Works | Silent projects no longer get an empty sound track |
| Blender background render (`cpu-demo`) | Works | MP4 assembled and QA passed |
| Blender MCP, live GUI under Xvfb | Works | Live call returned `PIPELINE_MCP_CONNECTED 5.2.4 LTS` |
| CPU Docker image (`infra/docker/Dockerfile.cpu`) | Builds | Separate job |
| Reusable song scene (`song-scene-demo`, p3d-kit with params) | Works | 4 seconds of Song 11 rendered at 1080p |
| Drive access (`tools/drive_sync.py check`) | Works | Read the folder and saved, then removed, a test file |
| Shotcraft Workbench playback and export (`node scripts/prove-workbench.mjs`) | Works on a GitHub runner ([run 45129900529](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45129900529)) and in a November 23 cloud session. | Page opened with no errors; playback advanced 00:00.00 to 00:04.00; export produced an H.264 1280x720 MP4 with 180 frames (checked with ffprobe). Shotcraft's own checker also rendered the SplitFlapFlip card to a 150-frame MP4. Cloud GitHub runner result pending. |
| Any-song draft (`./scripts/video song-draft <song>`) | Works in a November 23 cloud session (Song 5, 10 s, 1080p60 with sound, QA passed, using the repository's Song 5 promo recording). Cloud: Song 9 draft fetched from Drive by file id, result pending. | Run 45129900529 tried Song 5 and the Drive helper correctly refused: Song 5's chosen recording is a file shared from another account, outside the Songs folder. Songs 2, 5, 6 and 10 need copies in the folder before they can be fetched. |

The Workbench first failed to open on November 23 with a Vite error, `Failed to resolve import ../../shared/motion.mjs from proj/Composition.tsx`. The Workbench links the editor's source in as `workbench/proj` and resolves links by that path, so the relative import pointed outside the link. `apps/editor/src/shared` now links to `apps/shared`, and `Composition.tsx` imports `./shared/motion.mjs`. Earlier checks only confirmed an HTTP 200 response, which is why they missed it.

How to run it: push to any `claude/video-tools-*` branch, or dispatch
**Video tool proofs (cloud CPU)** by hand (`.github/workflows/tool-proofs.yml`).
Results are saved as the run's `tool-proofs` download, with one log per tool and
`proofs/summary.txt`. It runs no test suites.

Drive access for cloud jobs: `tools/drive_sync.py` lists, downloads (`get`) and
saves (`put`) inside the "Concert Backdrops - Songs" folder using the
`GOOGLE_DRIVE_OAUTH` Actions secret (Anthony's sign-in for the private "Concert
Video Renders" app in the Drive Backups Google Cloud project; revoke it at
myaccount.google.com, Security, Third-party connections). `GOOGLE_DRIVE_SA_KEY`
is a read-only fallback: Google gives service accounts no storage in a personal
Drive. Full song recordings stay in Drive; cloud jobs fetch them with `get`.

## Historical setup record

Historical setup verification is preserved below. The newer native 4K and motion
extension is recorded in [4K-MOTION-VALIDATION.md](4K-MOTION-VALIDATION.md).

Verified in the cloud workspace on November 19, 2026 (America/Los_Angeles). Work is on `setup/repeatable-video-pipeline`, based on `08b63fb3dd62ab0fdad7dcc5a86ca4bcf271f811`. It is an additive setup, not an update to an approved film.

## Outcome

The Blender and existing p3d adapters each rendered a complete two-second, 60-frame test. FFmpeg assembled both at exactly 30 fps and their technical QA passed. Three full-size Blender review frames were also rendered at 1920 x 1080. The browser applications and Shotcraft Workbench compile, but this cloud session cannot launch the browser or Blender GUI needed for their interactive runtime checks.

The cloud GPU provider is unconfigured. No Mac render, paid service, GitHub render workflow, automatic publication or creative approval was started or recorded.

## Installed environment

| Component | Observed version or pin |
| --- | --- |
| Platform | Linux x86_64, glibc 2.41 |
| Python | 3.12.14 |
| uv | 0.13.9 |
| Node / npm | 24.22.3 / 11.19.1 |
| Blender | Official 5.2.4 LTS Linux x64 build |
| FFmpeg / FFprobe | 7.1.5 |
| System Chromium | 156.0.8078.79, installed but unable to launch here |
| Three.js | 0.187.0 |
| React / React Three Fiber | 19.2.7 / 9.8.2 |
| React Postprocessing / postprocessing | 3.2.2 / 6.39.6 |
| Remotion | 4.0.484 across editor and Workbench |
| MCP for Blender | 2.3.1, isolated environment with dependency hashes |
| Video Shotcraft | 075b548c2405a07b77129eb448b0b504fc60dea3 |

The official Blender archive's SHA256 matched `2fd14c50987426897ba60237ee996edf2b4151f4b1a72a460ca20be58c1d2d86` before extraction. The environment recorder is `scripts/record-environment.py`.

## Completed checks

| Check | Evidence and result |
| --- | --- |
| Bootstrap replay | `CHROMIUM_PATH=/usr/bin/chromium python3 scripts/bootstrap.py --skip-browser-install` completed successfully. This selected the existing browser explicitly and did not establish browser runtime readiness. |
| Python contracts | 26 focused tests passed, including timing, path containment, cache repair, stale-frame rejection, caption protection, matching approval archives, and propagation of renderer failures. |
| JavaScript | Both apps passed TypeScript checks. Vite preview and Remotion production bundles built successfully. |
| Fonts | 74 pinned font files converted; the four legacy-required names are present. |
| Blender CPU movie | `video preview cpu-demo --quality draft`: 60 frames, 320 x 180, 30 fps, exactly 2 seconds, no audio by design, zero technical errors or QA warnings. |
| Legacy p3d movie | `video preview legacy-p3d --quality draft`: 60 frames, 320 x 180, 30 fps, exactly 2 seconds, one expected audio stream, zero technical errors or QA warnings. |
| Full-size review | `video storyboard cpu-demo --quality review --render` produced frames 0, 29 and 59 at 1920 x 1080 with 32 Cycles samples. Images were inspected. This is a key-frame review, not a complete 1080p movie. |
| Real cache reuse | A second `video render cpu-demo --quality draft` rendered zero frames and reused all 60. |
| Animation state | Sequential versus out-of-order frame visits produced exactly matching transforms, camera/light settings and material values across fresh scene builds: 90 objects, 16 materials, four comparisons. This does not imply identical Cycles pixels. |
| Archive | Local archive created; every file listed by its SHA256 manifest matched. No human approval was added. |
| MCP installation | Add-on enabled in an isolated Blender profile; all external asset/generation integrations off, telemetry off, localhost-only listener. |
| MCP stdio | Initialization and required-tool discovery passed; 10 tools advertised. Safe mode rejected a non-allowlisted import. |
| Shotcraft | Exact commit verified. Workbench TypeScript and Vite build passed. Linked project modules and main page returned HTTP 200. Foreground startup and shutdown passed. |

The existing `engine/`, approved scene definitions, audio sources, and original `.github/workflows/render.yml` were not modified.

## Reproducibility boundaries

The Blender image comparison deliberately requested frames out of order, including a repeated frame. The resulting PNG files were not byte-identical to the sequential run: Blender records render dates/times, and decoded images had very small differences. The largest observed RGB channel difference was 2 on a 0 to 255 scale; mean absolute differences were below 0.005. This is not evidence of pixel-exact rendering.

The separate scene-state check passed: four sequential versus out-of-order comparisons matched all tested animation values exactly across fresh scene builds. Within one scene build, complete snapshots including static geometry hashes also matched exactly. A sphere's mesh indices differed between fresh builds, but its 482 vertex positions and 512 oriented geometric faces were identical after canonical ordering; internal allocation IDs also differed. These are recorded separately from animation state in `work/pipeline/blender-order-check/scene-state-result.json`.

Animation uses absolute frames and seeded procedural geometry. Cache receipts validate the exact previously rendered files. Avoid claiming identical pixels across independent Cycles runs, denoisers, graphics drivers or hardware.

No full concert was migrated or rendered as part of this setup. No final 1080p60 or 4K60 film, realistic character rig library, detailed church library, or GPU performance improvement is claimed. The examples demonstrate tool integration and review discipline.

## Environment limits

### Browser capture and Remotion video rendering

The real browser probe reports `dependencies_ready: true`, browser `installed: true`, `runtime_validated: false`, and `status: blocked` when explicitly selecting system Chromium. Chromium fails to create its local process socket with `Operation not permitted`.

The official Playwright headless-shell download returned HTTP 403. An elevated browser-check attempt was automatically rejected because sandbox approvals are disabled in this workspace. The managed cloud browser also could not reach this execution workspace's localhost preview server. No network or sandbox protection was bypassed.

Consequently, actual Three.js PNG capture, repeated-frame pixel comparison in Chromium, Remotion MP4 rendering, and browser playback in Workbench remain unverified. Their source, dependencies, builds, diagnostics and launch commands are present. A normal approved cloud CPU workspace with browser IPC support can run the remaining checks; a GPU provider is not required for those checks.

### Live Blender MCP

The upstream add-on needs Blender's GUI event loop. A normal Xvfb startup failed with `Cannot establish any listening sockets` because local Unix sockets are restricted. The add-on is installed and MCP's stdio server works, but the live GUI bridge is unverified here. Background Blender rendering works independently.

### Container and GitHub workflow

The CPU Dockerfile was reviewed but not built because this workspace has no Docker daemon. The manual GitHub checks workflow was added but not dispatched. Its optional render uses runner minutes and is not configured to run on a push. The supplied container recipe still needs a successful build and a recorded image digest before production use.

## Remaining checks on a suitable cloud CPU host

```bash
python3 scripts/bootstrap.py
./scripts/video doctor --probe-browser
npm run test:browser
./scripts/video preview pipeline-demo --quality draft
./scripts/video finalize pipeline-demo --quality draft --editor remotion
python3 integrations/blender/smoke.py
```

For the optional live MCP check, first start the isolated Blender GUI on that cloud desktop, then run `python3 integrations/blender/smoke.py --live`. No GPU provider credentials are part of these commands.

## Where to inspect results

Outputs are ignored by Git under `work/pipeline/`. The principal evidence includes `cpu-demo/draft/qa.json`, `legacy-p3d/draft/qa.json`, the corresponding masters and contact sheets, the full-size `cpu-demo/review/` frames, `browser-doctor.json`, `contract-tests.log`, `environment.json`, and `blender-order-check/`.

The original silent CPU test master has SHA256 `6a50379ee65137f2247423c3db01533d44288408edea271d84718b752c55123a`. The legacy test master has SHA256 `feea2d6582d74eaa95845badd2c736ba03de4c1ef331176a3ca6de6b84ad4bc6`. They are technical evidence, not creatively approved deliveries.

For daily commands, see [VIDEO-PIPELINE.md](VIDEO-PIPELINE.md). Integration-specific checks are documented in [integrations/STATUS.md](../integrations/STATUS.md).
