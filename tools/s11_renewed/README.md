# Almighty God Who Knows the Future: full recreation

This is the requested full Song 11 music video: 260 seconds of its existing
recording followed by the established 15 second closing hold. The original
story, musical meaning, church models, emblem and on-screen wording come from
`tools/s11_full2`. The new treatment has its own source and output identity.

## The owner's direction

On November 22, 2026, Anthony rejected the separate fan study because its
body-fitting surfaces exposed anatomical details. He clarified the intended
deliverable: recreate his recent **Almighty God Knows the Future** video more
beautifully, with better animation and detail, while retaining his concert
style. That correction governs this revision and future reuse.

- People are modest, artistic forms of light. Clothing has a designed, generous
  silhouette. No nipples, breast outlines, buttock clefts or exposed cheeks.
- Detail belongs in costumes, architecture, water, musical gestures and light.
- The Song 11 hero is the conductor, with the blue choir and orchestra and gold
  instruments/songbooks. The visual journey remains heavenly city, Earth,
  Mount Zion, gathering nations and the Church of God.
- Heavenly Mother is represented only by light in this song.
- Light has peaks and rests. Preserve color, readable subjects and dark space.
- A technically valid render is ready for review; creative approval must come
  from the owner for that exact delivered film.

## What this revision changes

`cinematography.py` authors new selected camera paths and steadier travel.
`performance.py` controls the conductor, final-pose prop contact and modest
costume geometry. `scene.py` composes those cameras with the existing phrases,
adds fine moving waterways and separates architectural, atmospheric and
musical light. `render.py` makes the complete native movie in restartable
chunks and assembles the verified recording once.

The baseline files remain intact. The frozen approved thirty-second study
remains a reference with its own identity. This full recreation is a new work.

## Required inputs

- Linux cloud environment with Python 3.12, FFmpeg/libx264 and software EGL/Mesa.
- The project history, including engine commit
  `d928ff9eafe02ac3150f0c646bdcc497fe5a7278` and people/words commit
  `f43f4514e4bc42dc25166e90160d98219f5a0db4`.
- The existing body assets, Earth map, exact emblem and reference fonts, restored
  by the repository's preparation/bootstrap tools.
- The original recording at `work/song-inputs/s11-original.mp3`. Its SHA256 is
  `70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004`.
  Its Drive identity is `108zDtdB4X189DOwsZn-K9p548nERubLG`.

Use the checked-in runtime requirements and the actual delivery environment
receipt when reproducing this revision. `scripts/bootstrap.py --p3d-only
--reference-fonts` restores the project's standard environment and fonts;
the renewed runtime record identifies the versions used for this movie.

No new stock assets, image-generation service, motion subscription or paid
render service is required by this implementation.

## Prepare and render

From the repository root with the virtual environment activated:

```bash
python -m tools.s11_renewed.prepare --audio work/song-inputs/s11-original.mp3
PYTHONHASHSEED=0 LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=2 \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 \
python -m tools.s11_renewed.render \
  --width 1920 --height 1080 --samples 2 --workers 3 --chunk-frames 900 \
  --out work/s11_renewed/Almighty_God_Knows_the_Future_Renewed_1080p60.mp4
```

The source clock stays unchanged. Preparation trims at 260 seconds, fades the
last 0.05 seconds, then adds 15 seconds of silence. The renderer applies the
existing 0.1 second picture delay once. It renders 16,500 real frames at 60 fps;
it does not interpolate a lower frame-rate movie or upscale a smaller render.

For a composition pass, `--stills 12,28,58,99,118,140,167,205,240,260` uses
absolute song seconds. `--baseline` is an explicit comparison with the earlier
beauty treatment. Movie `--start` and `--end` use absolute frame indices.

Each completed chunk records source, runtime, dimensions, sample count, exact
frame range and checksum. Rerunning the same command reuses only matching
completed chunks. Changing picture source, settings, runtime or analysis
invalidates the old chunks. Do not edit rendering source during a final run.

## Review before delivery

Inspect the entire story, every cut and join, close conductor gestures, clothing
from front/side/rear, blue ensemble figures, prop contact, text entrances and
the dark ending. Decode the complete assembled file and confirm video frame
count, audio length, original audio timing and the closing hold. Record what
was actually inspected and any remaining limitations in the delivery evidence.

The music features are measured band/onset estimates from the recording.
They are not isolated instrument stems. The conducting is deliberately
authored animation, not a newly captured human performance.
