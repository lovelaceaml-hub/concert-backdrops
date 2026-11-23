# Repeatable video production

This checkout adds a reusable production workflow around the existing Python renderer, Blender, Three.js, Remotion, and Video Shotcraft. It preserves the approved films and their source scenes. The sample projects are engineering demonstrations, not new versions of the concert films.

Cloud GPU provisioning is intentionally absent. The default workers use the CPU. No GPU account, API key, billing configuration, automatic publishing, or Mac render is required or started by setup. Render quality still depends on the models, animation, lighting, and shot design supplied to these tools.

Read [the verification record](VIDEO-PIPELINE-VALIDATION.md) before relying on a renderer in a new workspace. Installation, compilation, a real rendered frame, and a finished movie are different verification stages.

The [native 4K and animation extension](4K-AND-MOTION.md) adds the current default
project template, high-bit-depth export profiles and reusable motion tools. See
[its verification record](4K-MOTION-VALIDATION.md) for the newer checks.

## Engine quality options

These are optional improvements to the current engine, not replacements for the
approved films. `Renderer(quality=QualityOptions(...))` selects them for any song.
With no quality argument, grain stays on, all light scales stay at 1.0, focus and
aperture stay authored, and temporal samples and shutter inherit the song's P3D
settings (normally one sample and the camera's shutter). Cut safety stays off.
No new motion helper runs automatically.

| Option | What it changes |
| --- | --- |
| `grain=False` | Removes added delivery grain, without changing the shared shader globally |
| `bloom_scale`, `sun_scale`, `rays_scale`, `sun_glow_scale` | Separate multipliers for bloom, sun, rays and halo |
| `grade_when` | Time predicate selecting which shots get the light treatment and aperture cap |
| `subject_focus` | Subject's world point, or time function returning a point; return `None` for other shots |
| `subject_aperture`, `aperture_cap` | Subject lens opening and maximum opening on other graded shots, in metres |
| `temporal_samples`, `shutter`, `cut_safe`, `cuts` | Moving-point samples, shutter fraction and extra cut times in source seconds |

The single `clarity` preset uses the Song 11 study's values: grain off, sun and
rays at 0.65, halo and bloom at 0.75, subject aperture 0.012 m, other graded shots
capped at 0.008 m, two temporal samples and a 0.35-frame cut-safe shutter. The
camera path is unchanged. Supply the subject point and stage-shot selector for
your song; the engine cannot infer them. Without a selector, light grading
applies throughout; without a subject point, authored focus stays in place.
Subject shots use 0.012 m rather than the non-subject aperture cap.

```python
from quality import QualityOptions
from render import Renderer

quality = QualityOptions.clarity(
    subject_focus=lambda t: hero_chest(t) if is_subject_shot(t) else None,
    grade_when=is_stage_shot,
    cuts=authored_cuts,
)
renderer = Renderer(1920, 1080, quality=quality)
```

Use those imports in the existing engine-loading environment. Every setting can
also be chosen individually through `QualityOptions`. Temporal sampling and
subject focus apply to P3D scenes. Bloom applies to all scenes; sun/ray/halo
scales apply where those world settings exist. Cut safety includes the camera
rig's hard and whip cuts plus `cuts`, disabling temporal and analytic blur on
frames whose shutter reaches across a cut. Draft point counts are unchanged;
use the existing final, non-draft mode for a quality proof.

For motion, `Motions.blend_gesture` solves the complete gesture at full weight
before blending, avoiding the partial arm solve that caused the 34.4 cm snap.
`Motions.pin_feet` solves explicit ankle positions and foot orientations after
upper-body acting, without a later ground lift or automatic contact shift.
`Motions.breathe_before_contacts` adds breathing before a caller's final hand
and foot solver; use `Actor(auto_breathe=False)` to avoid a second breathing
pass (the default is `True`). Install these before sampling or baking a body.
`p3d.attachments.final_hand_frame` attaches props to the final solved palm;
offsets are metres and grip roll/tilt are radians.

The frozen per-film tools are deliberately unchanged. Their source pins,
rounding, anatomy constraints, shader patches and cache fingerprints remain
authoritative for reproduction. New callers can use the shared options and
helpers instead of patches; do not apply both treatments. Focused non-rendering
checks cover the new paths. Cloud pixel comparison is still required before
claiming an existing film's byte-identical reproduction with a new caller.

## Reproducing approved films

Approved films pin exact hashes of the engine files that produced them, so
improving the shared engine on `main` never silently changes an approved film.
If you run a frozen film directly on a newer engine, it stops and points you to
the exact commit it is frozen to.

Use `reproduce` to render an approved film from its original commit in an
isolated worktree:

```bash
./scripts/video reproduce concert-kit-consideration-v2 --quality review
./scripts/video reproduce <project-id> --quality final --commit <sha>
```

The command looks up the project's recorded `picture_source_commit` in
`project-docs/production-system/catalogs/deliveries.json` (or uses `--commit`
when provided), creates a Git worktree at
`work/reproduce/<project-id>-<shortsha>` (reusing it if already present), runs
that commit's own `./scripts/video produce <project-id> --quality <quality>`
inside it, and prints the output folder path.

Limits to keep in mind:

- The recorded Git commit must be available in your local Git history (fetch it
  first if using a shallow clone).
- Private recordings and prepared inputs still need to be present inside the
  reproduction worktree before rendering, just as in a normal production run.
- For `approved-light-s11`, `pipeline/references/song11-beauty-v1.json` records
  `source_commit` `23c9307608291a99702d687933c8d2092d1fd01d`, which predates the
  `projects/approved-light-s11` manifest. To reproduce it through
  `./scripts/video produce`, pass
  `--commit 673f68785c36b57d55d05129ee5549efe6352c60`, which includes both the
  project manifest and the exact frozen engine files.

## 1. What is installed

| Part | Role | Project location |
| --- | --- | --- |
| Existing Python p3d engine | Preserve and reuse procedural worlds, particles, music response and existing scene code | `engine/`, with adapter in `pipeline/legacy.py` |
| Blender 5.2.4 LTS | Model and animate detailed 3D assets; render via background Python | `.tools/blender-5.2.4-linux-x64`, `scenes/blender/` |
| Three.js, React Three Fiber, React Postprocessing | Interactive scene preview and frame-driven light, particle and camera animation | `apps/scene-preview/` |
| Remotion 4.0.484 | Frame-accurate assembly with optional captions and typography | `apps/editor/` |
| FFmpeg and FFprobe | Browser-independent encoding, audio muxing and media inspection | Host executables, called by `pipeline/media.py` |
| MCP for Blender 2.3.1 | Optional assistant-controlled editing of a live Blender GUI session | `integrations/blender/`, project MCP configuration |
| Video Shotcraft | Pinned reference skill and Workbench for reusable motion patterns | `.tools/video-shotcraft`, project skill links |
| Python `video` CLI | Validate, analyze, render, reuse frames, assemble, check and archive projects | `pipeline/` and `scripts/video` |

JavaScript versions are in `package-lock.json`; Python versions are in `uv.lock`. MCP has its own hash-checked dependency lock. Blender's archive URL and SHA256 are in `infra/toolchain.lock.json`. Shotcraft uses the exact commit in `integrations/versions.json`. All Remotion packages match the pinned Workbench version.

The software dependency locks do not make different GPUs, graphics drivers or operating systems pixel-identical. Record the environment for each delivery. Keep rendering a frozen round on matched software and hardware.

## 2. Recreate the environment

Use a Linux x64 cloud workspace with Python 3.11, 3.12 or 3.13; Node 22.12 through 24; npm; Git; uv; FFmpeg and FFprobe. The current verified workspace uses Python 3.12.14, Node 24.22.3, npm 11.19.1 and uv 0.13.9. A regular browser worker also needs Chromium's usual Linux libraries and permission to create local process sockets. The bundled Blender installer and CPU Docker recipe target x86_64, not ARM.

From the repository root:

```bash
python3 scripts/bootstrap.py
./scripts/video doctor
./scripts/video doctor --probe-browser
python3 scripts/install-integrations.py --check
```

Bootstrap synchronizes the Python environment, installs locked Node packages, verifies/downloads the official Blender archive, installs the pinned Playwright headless shell, prepares the real font files, installs project integrations, and builds both applications. It starts no preview server, long render, cloud job or publication.

If an approved compatible browser is already installed, select it explicitly:

```bash
CHROMIUM_PATH=/usr/bin/chromium python3 scripts/bootstrap.py
CHROMIUM_PATH=/usr/bin/chromium ./scripts/video doctor --probe-browser
```

An installed browser may still fail to launch in a restricted sandbox. The second command tests an actual launch and WebGL2 context. Do not treat a dependency report as a rendering test. `CHROMIUM_PATH` selects a browser; it does not remove any sandbox restriction.

`--skip-browser-install` skips a network download, not the runtime requirement for Three.js or Remotion rendering. `--skip-integrations` omits MCP and Shotcraft. `--skip-blender` means an existing Blender must be available through `BLENDER_BIN` or PATH if Blender rendering or add-on installation is needed. Offline integration installation requires a populated package cache and the pinned checkout already present.

The optional CPU Docker recipe is `infra/docker/Dockerfile.cpu`:

```bash
docker build -f infra/docker/Dockerfile.cpu -t concert-video-cpu .
```

It is a supplied recipe, not a verified image from this task. No Docker daemon is available in the setup workspace. Before production use, build and test it on an approved CPU host and record the resulting image digest. Its base-image tag and distribution packages are not immutable pins. It contains no GPU provider configuration.

### Native p3d worker only

The current concert studies can run without installing Blender or a browser.
On a Debian or Ubuntu Linux x64 worker, the software OpenGL path needs these
distribution libraries in addition to the host tools listed above:

```bash
apt-get update
apt-get install -y --no-install-recommends libegl1 libgl1 libgl1-mesa-dri libgomp1
python3 scripts/bootstrap.py --p3d-only --reference-fonts
./scripts/video doctor --project concert-kit-consideration-v2
```

Use the host's normal administrator mechanism for package installation. The
package list is drawn from the supplied CPU container recipe; distribution
package versions are not locked. The p3d-only bootstrap recreates the locked
Python environment, installs locked Node packages used for font sources, and
reconstructs the exact reference fonts when `--reference-fonts` is selected.
See [REFERENCE-FONTS.md](REFERENCE-FONTS.md) for the checked 74-font recipe and
normal deterministic conversion mode. Node and npm are needed for that setup step even though the
native renderer itself does not use a browser. Git, uv, FFmpeg and FFprobe must
already be available.

The doctor checks dependencies; it does not create an EGL context or prove that
a frame can render. After restoring the private audio input, run one selected
frame through the commands in [PIPELINE-INTEGRATION.md](PIPELINE-INTEGRATION.md)
and inspect the result. Do not rerun font setup during a frozen render round.

The manual GitHub workflow `Video pipeline checks (manual CPU only)` validates the core workflow. Its optional render test uses runner minutes and must be started deliberately. It was not dispatched during setup. It does not run on pushes and it does not replace the existing concert Render workflow.

## 3. The shared project contract

Each project has `projects/<project-id>/project.json`. It identifies the recording, frame rate, style reference, manually reviewed timing and shots. Each shot names a renderer, a source scene, a start frame, an exclusive end frame, parameters and any additional asset dependencies.

Included examples cover different paths:

| Project | Contents | Purpose |
| --- | --- | --- |
| `cpu-demo` | Two seconds of the original Blender pavilion at 30 fps, silent | Small complete workflow proof without Chromium |
| `pipeline-demo` | Two seconds of Three.js followed by two seconds of Blender at 30 fps, silent | Mixed-renderer integration check on a browser-capable worker |
| `legacy-p3d` | Two seconds of an existing p3d technical scene and the existing short test recording | Compatibility check without editing the approved engine |
| `motion-study` | Ten seconds of a procedural conductor and camera track at 60 fps | Native 4K presets, baked motion blur and reusable rig foundation |

The original short examples use 320 x 180 drafts to keep verification inexpensive. New cinematic projects default to 960 x 540 drafts, 1920 x 1080 reviews, and 3840 x 2160 final images with 16-bit Blender PNG sources. Quality presets change dimensions and sample counts, never the project frame rate. Select 60 fps when creating a film intended for 60 fps delivery, and keep that timing throughout its reviews.

```bash
./scripts/video new "Next Concert Film" --fps 60 --seconds 10
./scripts/video validate next-concert-film
```

The default new-project template starts with the Blender camera and character study. Replace its scene and shot table with the intended production design. Use `video new TITLE --template browser` to start with the registered Three.js example and its original 1080p settings. Adding a new browser scene requires registering its component and path as described in [apps/README.md](../apps/README.md).

Frame intervals are half-open. A 60-frame shot starting at frame 120 covers frames 120 through 179, and the next shot starts at 180. Timelines must be contiguous, with no gaps or overlaps. Renderers evaluate the requested absolute frame and a fixed random seed. They do not depend on playback speed or wall-clock time.

Source paths stay inside the repository checkout. Keep private songs and assets in ignored paths within that checkout when rendering, then point the manifest at those paths. Do not add full songs, lyrics, finished videos or frames to Git. The existing approved short test clips are the repository's documented exception.

List additional models, textures, font assets or data files in `dependencies` at project or shot level. The cache hashes these files. Changes outside its declared inputs cannot be detected reliably.

## 4. The repeatable production round

### Establish the look and timing

Keep a small set of approved full-size reference frames for each section. Decide the composition, visible architectural detail, material finish, palette, camera intent and highlight level before rendering the whole film. `styles/zion-cinematic.json` records guidance; it is not a promise that every field automatically changes every renderer's shader.

For music, set `audio.source` to the existing recording and use:

```bash
./scripts/video analyze next-concert-film
```

This writes onset suggestions under `work/pipeline/<project>/audio-analysis.json`. It does not overwrite approved timing. Listen to important hits, correct their integer frame positions, and store the confirmed events in the project's timing file. This analyzer does not separate choir, timpani, strings or other instruments into stems. Existing approved feature data can be passed to a p3d shot with `params.features`. A p3d shot's `params.source_time_seconds` declares its source scene clock; set it explicitly when adapting later sections or an audio offset so its existing choreography and feature data stay aligned with the recording.

### Inspect full-size key frames

```bash
./scripts/video storyboard cpu-demo --quality review --render
```

This renders the first, middle and last frame of each shot at review resolution and writes a review page. For a particular moment:

```bash
./scripts/video render cpu-demo --quality review --frames 0,29,59
```

Review text and the exact approved emblem at full size. The example pavilion contains no official logo and is not a church reconstruction. Do not infer approval of a real building from this generic model.

### Check motion, then freeze the round

```bash
./scripts/video preview cpu-demo --quality draft
```

With no frame or shot filter, `preview` renders the full short project, assembles it, and runs technical QA. With a filter it produces selected frames and a review page, not a pretend complete master.

Review an actual short sequence for motion, shimmer, letter readability, camera acceleration and musical timing. Still frames cannot verify animation quality. Freeze the scene, style, timing and dependency versions before parallel builders continue. Assign a single owner to shared lighting and color settings.

### Render and finish

```bash
./scripts/video render next-concert-film --quality final
./scripts/video finalize next-concert-film --quality final
```

`finalize` assembles existing verified frames; it does not silently start a new full render. A missing, changed or stale frame stops assembly with a repair instruction. Matching frame receipts are reused on subsequent render commands.

To render one shot or a range:

```bash
./scripts/video render next-concert-film --quality draft --shot opening
./scripts/video render next-concert-film --quality draft --frames 0:60
```

One coordinator owns a project/quality output directory at a time. This prevents two builders from overwriting the same products. Optional `production.render_workers` sets the maximum renderer subprocesses per shot, from 1 to 32; the default remains 1. `production.threads` controls threads inside each process. Start conservatively and measure peak memory at the intended resolution before increasing workers. A 4K run needs a separate memory check.

Each chunk gets a unique job file, log, frame staging directory and audio feature directory under `shots/<shot>/workers/<invocation>/`. Frame ownership is disjoint. Only the coordinator validates PNG dimensions, bit depth and checksum, promotes completed frames into the canonical `frames` directory, and writes the receipt. Changing worker count does not change image identity. A failed worker stops further dispatch; already launched workers finish or reach their timeout, and their valid completed frames remain reusable. A `STOP` marker also stops dispatch; registered p3d workers check it between frames. Other backends can finish their current bounded chunk. A changed source fingerprint prevents promotion of that chunk. Keep sources frozen throughout the round.

The project lock and private staging protect a resumed run from an old worker that survived a killed coordinator. Unreceipted staging frames are never reused. This is bounded parallel rendering on one CPU host; distributed farm dispatch is not implemented.

FFmpeg is the default finishing path and needs no browser. It combines rendered clips and the supplied audio without silently adding or re-timing titles. If the project includes separate captions, use the Remotion path on a verified browser worker:

```bash
./scripts/video finalize next-concert-film --quality final --editor remotion
```

FFmpeg finishing rejects separate captions instead of discarding them. Words already rendered by the existing engine remain part of its frames. Remotion uses actual font files and composites captions above the images. The source audio must be long enough for the timeline; the pipeline rejects an accidental short recording.

### Review and archive

```bash
./scripts/video qa next-concert-film --quality final
./scripts/video review next-concert-film --quality final
./scripts/video archive next-concert-film --quality final --destination /approved/storage
```

QA checks dimensions, frame count, fps, duration, audio presence, checksums and source provenance. It samples brightness and scans consecutive decoded frames for suspected frozen intervals or unexpected large changes. Those warnings guide visual review. They do not establish musical intent, anatomy, correct lettering or artistic approval.

The normal delivery is an SDR H.264 MP4 with Rec.709 metadata. The examples use display-referred PNG frames, not a linear EXR or HDR grading pipeline. Blender uses AgX; the Three.js demo has its own view transform. Compare their reference images deliberately before mixing them in one film.

After a person has actually watched the delivery, record that review with `video approve`, supplying `--reviewer`, `--note` and `--confirm-viewed`. Setup does not record human approval. Archives include matching approval only, plus the master, manifest, timing, style, QA, dependency locks, render receipts and SHA256 checksums. Archive copies to the specified local or mounted storage; it does not upload or publish anything.

## 5. Interactive tools

On a browser-capable cloud desktop:

```bash
npm run preview
npm run editor
node scripts/launch-workbench.mjs
```

The preview app has a frame scrubber, frame steps, bloom control and three camera choices. It reports the actual graphics renderer. The CPU capture path explicitly uses software WebGL. Neither Three.js nor Playwright creates a GPU on a CPU-only machine.

Shotcraft's Workbench imports the example editor manifest. Its visual edits must be exported and deliberately incorporated into the source timeline; they do not automatically rewrite every pipeline project. See [the integration guide](../integrations/README.md) for the exact workflow and media restrictions.

For live assistant editing in Blender, use the project MCP configuration and start `python3 integrations/blender/launch_blender.py` on a cloud desktop. The upstream add-on requires Blender's GUI event loop. Background Blender rendering is independent of that connection and already works in the current workspace. The current session cannot host the GUI bridge because local Unix sockets are restricted.

These project files configure supported Claude Code and Codex clients when opened at the repository root. They do not install a new callable MCP tool into an already-running ChatGPT conversation. No global client settings or Mac applications are modified.

## 6. Troubleshooting and boundaries

| Symptom | Action |
| --- | --- |
| Browser installed but launch blocked | Run `video doctor --probe-browser`, inspect its error, and use an approved cloud CPU environment with normal browser IPC. The Blender/FFmpeg path remains available. |
| Playwright download denied | Preserve the error. Use an explicitly approved installed browser or a workspace whose policy permits the official download. Do not change network policy or use a bypass. |
| MCP tools listed but Blender unreachable | Start the isolated Blender GUI on a desktop-capable worker and run `python3 integrations/blender/smoke.py --live`. Installing the server is not a live connection. |
| Missing legacy font or Python package | Rerun bootstrap or use `scripts/video`, which retains the locked `legacy` dependencies. |
| Stale frame receipt | Rerun `video render` for the relevant project and quality. Do not edit checksums manually. |
| A change invalidates more frames than expected | Shared pipeline code is intentionally part of every cache fingerprint. Finish common changes before the frozen render round. |
| Need a real GPU later | Add the selected worker/provider and device policy in a separate implementation step. Current adapters deliberately select CPU/software rendering; no provider is hidden behind an environment variable. |

Better character rigs, detailed church models, choreography and revised shot design are production work performed with this foundation. The setup includes motion guidance and deterministic examples, not a completed library of realistic people or 226 upgraded buildings. Keep the existing approved master as the comparison reference.

Limit: a recorded commit's worktree starts without the ignored `work/` folder, so
private inputs such as full song recordings must be restored there first (for
example with `tools/drive_sync.py get` in a cloud job). Reproduction has not yet
been run end to end for every approved film.

## Reusable scenes for any song (November 22, 2026)

The `p3d-kit` route (frame recovery, worker chunks, temporal samples, QA) now
accepts any scene module that declares `FPS` and `DURATION` (or `DURATION = None`
to let the project's shots set the length), plus `make_renderer()` and `frame()`.
Optional `configure(params)` receives the shot's `params`. The approved films stay
locked to their registrations and still refuse params, so they reproduce exactly.

`scenes/p3d/song_scene.py` renders any `engine/songs/` file through that route.
Example shot params: `{"song": "s11_finale", "audio": "audio/promo/s11.mp3",
"start_seconds": 30, "bloom_scale": 0.7, "grain": false}`. See
`projects/song-scene-demo/project.json`. Work at 1080p; the final show video is
3840x2160 at 60 fps only after the video is approved.

## Music sync

The `tools/music_sync/` package measures real beats, downbeats, instrument hits, sung-word timing, and rehearsal tempo changes so concert backdrops follow the actual performance. The existing `pipeline/audio.py` stays untouched for earlier films. Heavy separation and transcription run on GitHub Actions CPU runners, never on the Mac.

### Commands

Run through `python -m tools.music_sync <command>` (on a cloud runner with `tools/music_sync/requirements.txt` installed):

- `analyze <audio> --out <dir>`: separates the song into `vocals`, `drums`, `bass`, and `other` stems with Demucs (`htdemucs` on CPU), tracks beats and downbeats with `beat_this` (falling back to `librosa` if unavailable and recording which tracker ran), measures per-stem hits and energy, and finds section boundaries from chroma and MFCC self-similarity. Writes `sync.json` with `"manually_verified": false`. Stems stay in `work/` and are never committed to Git.
- `lyrics <audio> --out <dir> [--language en]`: times every sung word with `faster-whisper` (CPU, `int8`, `small` by default or `medium` via `--model medium`), automatically using `<dir>/stems/vocals.wav` when present. Writes `words.json` (`word`, `start`, `end`, `confidence`). Because lyrics are copyrighted, `words.json` is ignored by Git and must go only to the private Google Drive folder.
- `match <studio_audio> <live_audio> --out <dir>`: aligns a rehearsal or live recording to the studio track with chroma features and dynamic time warping (`librosa`), writing `tempo_map.json` with monotonic `(studio_seconds, live_seconds)` anchors, overall offset, overall stretch, and a confidence score. Python code can call `retime(times, tempo_map)`, `retime_cues(cues, tempo_map)`, and `retime_phrases(phrases, tempo_map)` to shift studio cues and phrases to the rehearsal timing.
- `cues <sync.json> --out <dir>`: turns detected section starts into `cues.py` (a `CUES` list ready for `engine/live.py`) and `cues.csv` (`name`, `start_seconds`, `start_timecode_60fps` for show software such as QLab, ProPresenter, or Resolume). Pass `--tempo-map <tempo_map.json>` to export live-retimed cues.

### Running in the cloud and where results land

Start the GitHub Actions workflow **Music sync (cloud CPU)** (`.github/workflows/music-sync.yml`) manually from GitHub Actions or with `gh workflow run`. Pushing to any `claude/music-sync*` branch also starts it automatically, running every step (including sung-word timing) on the proof song "05 God Bless You! (sung guide, for lyric timing).mp3" and saving the results to Drive. Manual examples:

```bash
gh workflow run music-sync.yml -f song="05 God Bless You! (sung guide, for lyric timing).mp3" -f steps=all
gh workflow run music-sync.yml -f song="03 Studio.mp3" -f live="03 Rehearsal.mp3" -f steps=match
```

The cloud job pulls the song from the root of the Google Drive folder **Concert Backdrops - Songs**, runs the selected steps, and uploads the results to **Concert Backdrops - Songs / Status / Sync / \<song name without extension\>**. Non-lyric timing files (`sync.json`, `tempo_map.json`, `cues.csv`, and `cues.py`) are also attached to the workflow run as a downloadable artifact for 14 days. Raw WAV stems and `words.json` are never uploaded as workflow artifacts or committed to Git.

Every output is a starting suggestion (`"manually_verified": false`), not locked show timing. Anthony or a reviewer must listen against the music and confirm important beats, sung words, live retiming, and cue points before finalizing a concert backdrop.
