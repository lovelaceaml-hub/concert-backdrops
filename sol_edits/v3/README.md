# Nine Colors, One Love: Grand Finale

GPT-6.1 Sol's independent 62 second concert film, from v6 commit
`b7895aef771f4dcdbb7a3383afeab235fd945b6e`, on `compare/sol61-cinema-v3`.

The owner's chosen visual reference is Film 10, Nine Colours. Its existing share
artifact from run `43734065813` was inspected directly. The new choreography is
independently authored for Sol's current cast and timing; no Film 10 song code or
competitor revision is imported into this edit.

One white light becomes nine colours. The ribbons carry a welcome, gratitude,
reconciliation, listening, prayer and practical kindness. A blue gateway opens,
yellow and green surround an embrace, and all nine spiral upward into one light
before illuminating the world and resolving into the campaign logo. The owner's
latest direction adds an aerial barrel roll, luminous phrases passing the camera
with actual water reflections, and a much stronger concert ending.

This blends Film 10's comet journey, reflections and exhilarating braid with the
new emotional direction: closer gold-figure acting, opaque flowing costumes,
soft garden and cathedral atmosphere, controlled light, eased cameras and a real
musical release. Detailed environment paintings support selected tender scenes;
the braid is actual three dimensional light and clouds around a moving camera.

All nine phrases retain their exact campaign wording. The approved logo, opening,
signature, official-style end card and current event details remain. The opening
reads from frame 0 for seven seconds; the complete end card reads for seven
seconds. Nine coloured trails frame the invitation and pulse on the final accent,
then release without obscuring the exact logo or invitation text.

## Music

The owner's newest creative freedom is used to choose one continuous 60 second
passage from original concert Song 11 rather than another seven-song compilation.
The first 55.638 seconds use the continuous recording. The new coda sustains its
recorded tonic into a crescendo, rearticulates the original concert chord at
60.418 seconds, then releases into the recording's reverberation. No synthesized
music, voiceover or ElevenLabs media is used.

Source: the owner's original `11 Almighty God Who Knows Future.mp3`, Drive file
`1tESu4rGGlTJwVpiMXiEA2UC0wA6r2Rf7`. Its exact hash is in `assets.json`.
Extract 203.026939 to 263.026939 seconds, prepend two seconds of silence, ease the
first 1.5 seconds of music in, and apply one fixed gain. Only the last 50
milliseconds of already quiet decoder noise is tapered. This creates the base
score used for the scene analysis. `build_power_score.py` then constructs the
new ending from the same recording, with 60 ms crossfades and pitch-preserving
Rubber Band time stretching. A low register filtered copy reinforces the final
chord. A peak guard rejects faulty stretch output; the final 25 ms taper only
removes the release's remaining decoder noise. The last full second is
deliberately audible, following the owner's newest request for a powerful end.

## Assets and isolation

All new code is under `sol_edits/`. The loader registers `songs.sol_v3` from this
directory, imports the untouched v6 scene and configures this process only. No
protected engine file, competitor branch or workflow is edited. Nothing is
merged and the paid GitHub Render workflow is never dispatched.

Four supporting environment paintings were created with ChatGPT's image tool.
Their directions are in `environment-prompts.md`; exact PNG hashes are in
`assets.json`. They are animated projections, not generated video clips. The
people, cloth, contact shadows, ribbons, sparks, cloud flight, camera and logo
animation are rendered locally. A final photographic gold grade uses masks from
the actual animated body and cloth geometry, preserving scenery and brand colours.

The exact local source archive is `work/sol3/Sol-V3-environment-sources.zip`.
Retain it for exact reconstruction; regenerating a prompt does not reproduce
identical pixels. Automatic approval review blocked a separate Drive upload of
this archive because the owner's Drive request covered finished videos. It stays
local; finished-video delivery is separate and authorized.

Never commit recordings, paintings, fonts, features, caches or rendered outputs.

## Local construction

Existing dependencies only: numpy, scipy, librosa, moderngl, pillow, fonttools,
brotli and soundfile. FFmpeg with the Rubber Band filter must be on PATH.
EGL uses llvmpipe.

From the repository root:

```bash
python sol_edits/v3/prepare.py \
  --recording /path/to/original-song11.mp3 \
  --environment-archive /path/to/Sol-V3-environment-sources.zip
```

Pack `@fontsource/cormorant-garamond@5.3.0`, `@fontsource/jost@5.3.0` and
`@fontsource/outfit@5.3.0` with `npm pack`. Extract each package into its own
subdirectory of `/tmp/fs`, then:

```bash
python tools/setup_fonts.py /tmp/fs fonts
python sol_edits/v3/build_music.py
ffmpeg -y -i work/sol3/sol-v3-score.wav -ac 1 -ar 22050 work/sol3/audio.wav
python engine/analyze.py work/sol3/audio.wav work/sol3/features.npz
source sol_edits/v3/env.sh
```

A timing preview samples fewer frames while retaining the final 60 fps shutter:

```bash
mkdir -p work/sol3/nine-colors
python sol_edits/v3/render.py --range 0 3720 --step 4 --scale 0.5 \
  --out work/sol3/nine-colors/preview-silent.mp4
```

The final master renders every frame at 1920 by 1080:

```bash
mkdir -p work/sol3/nine-colors
python sol_edits/v3/render_all.py > work/sol3/nine-colors/render-all.log 2>&1
```

This recomputes frame count from the song settings, requires 62 seconds at 60 fps,
renders five exclusive ranges, checks each decoded range, concatenates them,
grades all 3720 frames through locally rendered body masks, muxes the score, and
encodes a 1280 by 720 review at the same actual 60 fps. Both audio encodes use the
original WAV directly. MP4s use H.264, AAC and faststart for phones.

Those are intermediate base outputs. Finish the owner's new aerial and musical
direction with these commands, still from the repository root:

```bash
mkdir -p work/sol3/power-finale
python sol_edits/v3/build_power_score.py
python sol_edits/v3/render.py --range 2522 2693 \
  --out work/sol3/power-finale/flight-native-60.mp4
python sol_edits/v3/grade_people.py --range 2522 2693 \
  --input work/sol3/power-finale/flight-native-60.mp4 \
  --out work/sol3/power-finale/flight-graded-60.mp4
python sol_edits/v3/power_finish.py
python sol_edits/v3/make_delivery.py
```

The final master is
`work/sol3/power-finale/Sol-V3-Nine-Colors-Grand-Finale-1080p60.mp4`.
The phone review is
`work/sol3/power-finale/Sol-V3-Nine-Colors-Grand-Finale-review-720p60.mp4`.
The finish replaces exactly 171 flight frames, keeps every other base frame in
order, adds the moving coloured crown, and muxes the grand finale score. Its
two-pass 2800 kbps review preserves 60 fps and targets less than 25 MB. The
separate flight pass allows an existing completed base to be reused; a fresh
base from this revision already includes the new flight choreography.

The Drive connector rejects files over 100 MiB. `make_delivery.py` retains the
134 MB local master and creates a separate 11 Mbps 1080p60 download copy, with
the original master AAC stream copied without another audio encode. Its name is
`Sol-V3-Nine-Colors-Grand-Finale-1080p60-download.mp4` in the same output folder.

`--mux-only` on `render_all.py` validates and finishes already completed ranges;
it never dispatches cloud work.

## Validation

```bash
python sol_edits/v3/check_media.py \
  work/sol3/power-finale/Sol-V3-Nine-Colors-Grand-Finale-1080p60.mp4 \
  work/sol3/power-finale/Sol-V3-Nine-Colors-Grand-Finale-review-720p60.mp4
python sol_edits/v3/check_audio.py \
  --score work/sol3/power-finale/concert-grand-finale.wav --tail-seconds .02 \
  --video work/sol3/power-finale/Sol-V3-Nine-Colors-Grand-Finale-1080p60.mp4 \
  --out work/sol3/power-finale/audio-check.json
python sol_edits/v3/check_seams.py
python sol_edits/v3/inspect_motion.py \
  work/sol3/power-finale/Sol-V3-Nine-Colors-Grand-Finale-review-720p60.mp4 \
  --out work/sol3/power-finale/motion-check.json
```

Checks count decoded frames and timestamps. All 16 boundary-adjacent raw scene
frames are compared with an independent ordered sampling pass. The photographic
finish processes every frame continuously with input-length guards. Audio checks
measure the lead-in, final release and source-to-AAC alignment in six places.
The final release check uses 20 ms rather than the earlier quiet full second,
because the latest owner request explicitly calls for a loud ending. The passing
reflections are secondary phrase echoes after the nine fully readable acts;
the latest owner direction explicitly requests those reflections.
These checks do not judge beauty, acting or musical feeling.

See `VALIDATION.md` for the reviewed result, measured cost and remaining limits.
