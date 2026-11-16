# When Love Becomes Light

GPT-6.1 Sol's third independent concert treatment, from v6 commit
`b7895aef771f4dcdbb7a3383afeab235fd945b6e`. This responds to the owner's rejection
of Sol V2 and subsequent direction to pursue beauty and emotion freely. It is an
alternative for review, not a change to Claude's or Astra's films.

A warm light passes from person to person. A bow welcomes, an apology becomes an
embrace, listening opens a garden, prayer fills a vast cathedral, a helping hand
raises someone, and encouragement sends the light toward the world. The luminous
Earth resolves into the campaign logo and invitation.

The environments now have detailed ivory architecture, magnolia gardens,
reflective marble, cloud valleys and vast sunlit space. The locally animated
people have shaded gold surfaces, opaque smoothed long-sleeved costumes and
simulated cloth beneath their golden particle grain. A final photographic gold
grade uses masks from the actual animated body and cloth geometry, giving the
people more depth without recolouring the scenery, campaign words or logo. Camera orbits, dollies and
an ascending crane replace the baseline whips. An output-space phrase treatment
keeps the exact nine expressions readable without repeating large category pills.
The approved opening, logo and end-card typography and event information remain.

## Music

The latest creative freedom is used to choose one continuous 60 second passage
from the original full recording of concert Song 11, rather than another short
seven-song compilation. There are no internal song joins, tempo changes or pitch
shifts. The recording's final chord and recorded reverberation are retained.

Source: the owner's original `11 Almighty God Who Knows Future.mp3`, Drive file
`1tESu4rGGlTJwVpiMXiEA2UC0wA6r2Rf7`. The exact hash is in `assets.json`.
Extract 203.026939 to 263.026939 seconds, add two seconds of silence, ease the first
1.5 seconds of music in, and apply one fixed gain. Only the last 50 milliseconds of
already quiet decoder noise is tapered. The final cadence is around film time
55.6 seconds and the recording rings out to the end. No synthesized music,
voiceover or ElevenLabs footage is used.

## Assets and reproducibility

All new code is here. No protected engine files are edited. The loader registers
`songs.sol_v3` from this directory, imports the untouched v6 scene, and applies
configuration to this render process only. It never writes into `engine/`.

Four new environment paintings were created with ChatGPT's image tool. Their
production prompts are recorded in `environment-prompts.md`. The exact PNGs are
in the local delivery archive `work/sol3/Sol-V3-environment-sources.zip`; their SHA256
hashes are in `assets.json`. The paintings are animated projections, not generated
video clips. Original 3D cameras, people, cloth, shadows, petals, rain, light trails
and logo animation are rendered locally. Regenerating a prompt will not reproduce
identical pixels; retain the exact archive for exact reconstruction.

Drive upload of the separate source-art archive was blocked by automatic approval
review because the owner's Drive delivery request covered finished videos. The
archive remains local. Finished-video delivery is separate and authorized.

Never commit the source recording, paintings, fonts, features, caches or outputs.

## Local build

Use the existing Python dependencies: numpy, scipy, librosa, moderngl, pillow,
fonttools, brotli and soundfile. FFmpeg must be on PATH. Software EGL uses llvmpipe.

From the repository root, prepare the exact assets:

```bash
python sol_edits/v3/prepare.py \
  --recording /path/to/original-song11.mp3 \
  --environment-archive /path/to/Sol-V3-environment-sources.zip
```

Install the three existing font families using Fontsource 5.3.0. Pack
`@fontsource/cormorant-garamond@5.3.0`, `@fontsource/jost@5.3.0` and
`@fontsource/outfit@5.3.0` with `npm pack`, extract each package into a separate
subdirectory of `/tmp/fs`, then run:

```bash
python tools/setup_fonts.py /tmp/fs fonts
python sol_edits/v3/build_music.py
ffmpeg -y -i work/sol3/sol-v3-score.wav -ac 1 -ar 22050 work/sol3/audio.wav
python engine/analyze.py work/sol3/audio.wav work/sol3/features.npz
source sol_edits/v3/env.sh
```

Short previews retain the 60 fps shutter while sampling fewer frames:

```bash
python sol_edits/v3/render.py --range 0 3720 --step 4 --scale 0.6666667 \
  --out work/sol3/preview-silent.mp4
```

The final master uses every frame and the full 1920 by 1080 canvas:

```bash
python sol_edits/v3/render_all.py > work/sol3/render-all.log 2>&1
```

This recomputes frame count from the song settings, requires 62 seconds at 60 fps,
renders five exclusive ranges, concatenates them, grades every frame through
locally rendered body masks, muxes the original score, and
encodes a 1280 by 720 review at the same actual 60 fps. Audio comes directly from
the source WAV in both encodes. Both MP4s use H.264, AAC and faststart for phones.
Do not trigger GitHub's paid Render workflow.

## Checks

```bash
python sol_edits/v3/check_media.py work/sol3/Sol-V3-When-Love-Becomes-Light-1080p60.mp4 \
  work/sol3/Sol-V3-When-Love-Becomes-Light-review-720p60.mp4
python sol_edits/v3/check_audio.py \
  --video work/sol3/Sol-V3-When-Love-Becomes-Light-1080p60.mp4
python sol_edits/v3/check_seams.py
python sol_edits/v3/inspect_motion.py \
  work/sol3/Sol-V3-When-Love-Becomes-Light-review-720p60.mp4 \
  --out work/sol3/motion-check.json
```

Media checks count decoded frames and timestamps. The seam check compares all 16
boundary-adjacent raw scene frames against one independent ordered sampling pass.
The photographic finish then processes all 3720 frames in one continuous pass,
with an input-length guard and a decoded output frame-count check. Audio
checks measure the exact silence, final decay and source-to-AAC alignment in six
places. These checks do not judge beauty, natural acting or musical feeling.

See `VALIDATION.md` for the reviewed result, actual render cost and limitations.
