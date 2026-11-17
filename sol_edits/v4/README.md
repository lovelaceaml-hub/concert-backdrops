# Nine Colours upgraded, Sol V4

The owner's newest request is to keep the original Nine Colours concept and its
song, essentially the same film with the model, animation, text and information
card improvements. This revision follows that direction directly.

## Original film and music

`original.py` is the repository's Film 10 source snapshot at
`3d8dbc40e8a9cc7fe7b5f19f230f3fbd4af866f8`, the exact commit of the original
share artifact from Actions run `43734065813`. The snapshot preserves provenance;
effective cast, effects, timing and card changes are in `film.py`. No competitor's
independent comparison revision is used. No protected repository file is edited.

The actual share video was inspected and its audio compared to the repository's
`audio/promo/concert-medley.mp3`. Correlation at six positions from 5 to 55 seconds
ranged from 0.99599 to 0.99974, confirming the same medley after share encoding.
This is the original eight-song medley with its original joins, order and final
hit, not Sol V3's Song 11 construction. The newer choice of the original Film 10
soundtrack supersedes the earlier seven-song comparison structure.

`build_music.py` decodes the full 60 second medley, applies one peak-safe fixed
gain and a 100 ms entrance ease, then prepends two quiet seconds. The resulting
duration is exactly 62 seconds. Internal song timing and the original recorded
ending are retained. The source medley already releases below -90 dBFS at the
end. No generated music, voiceover or ElevenLabs media is used.

## What is preserved and improved

The white seed, nine comet rivers, reflected blue gates, embrace, dancer, aerial
half loop, helping hands, gratitude, listening, prayer, upward corkscrew and
morning arch keep the original sequence and camera choreography. The updated
opening title and official-style end card use the exact campaign wording, logo,
fonts and current Las Vegas concert details. The opening reads fully for seven
seconds, and the complete final invitation reads from 55 to 62 seconds. A small
signature stays visible through the middle; the date burst remains a decorative
musical motif, now held for 2.51 seconds.

Warm gold figures gain actual shaded mesh volume under fine glitter, improved
costume shells, flowing cloth and denser facial/hand sampling. The apology and
embrace use two women with low hands and eased steps. The opening greeting uses
two men bowing. All touching casts are the same gender. The original dancer
remains; local pose smoothing and 60 Hz spline camera/ribbon anchors refine the
captured movement. Applause stays close to the chest. Prayer figures remain whole
and radiant. Old dissolve, disperse and falling-flake effects are not used.

The hand close-up retains arms made of light, with solid detail limited to palms
and fingers. It avoids opaque arm stumps. The late gate gains a secondary phrase
and its real water reflection after the main phrase's reading moment. This
follows the owner's explicit request for passing reflected words.

Fast cuts use short moving picture dissolves. Strong shader twinkle on figures,
words and ribbons is removed, while the original sky's stars remain.
Near-lens ribbon widths and alpha are bounded to prevent a large triangular
streak from filling the image. Native motion blur uses a 0.8/60 second shutter.
The original ending's sky and coloured arch remain alive behind the official
invitation, with a subtle complete-picture push to the final frame.

## Local reproduction

Use the existing repository dependencies: numpy, scipy, librosa, moderngl, pillow,
fonttools, brotli and soundfile, plus FFmpeg. No new heavy dependency or generated
painting archive is required. All scenery is rendered from repository code.

Install the three Fontsource packages with npm pack, extract each under `/tmp/fs`
and run `python tools/setup_fonts.py /tmp/fs fonts`. The known local font package
versions are 5.3.0 for Cormorant Garamond, Jost and Outfit.

From the repository root:

```bash
python sol_edits/v4/build_music.py
ffmpeg -y -i work/sol4/medley-scene-clock.wav -ac 1 -ar 22050 work/sol4/audio.wav
python engine/analyze.py work/sol4/audio.wav work/sol4/features.npz
source sol_edits/v4/env.sh
python sol_edits/v4/render_all.py > work/sol4/render-all.log 2>&1
```

Analysis follows the original unshifted scene clock. The render wrapper supplies
the two-second output lead-in. The total range is recomputed from the final song
settings and asserted as [0,3720) at 60 fps. Five exclusive native ranges are
rendered at 1920 by 1080 and concatenated after decoded-count checks.

Outputs under `work/sol4/`:

- `Sol-V4-Nine-Colours-Upgraded-render-master-1080p60.mp4`, native CRF 16 archive.
- `Sol-V4-Nine-Colours-Upgraded-1080p60.mp4`, 11 Mbps two-pass download copy below
  the Drive connector's 100 MiB upload limit.
- `Sol-V4-Nine-Colours-Upgraded-review-720p60.mp4`, 2800 kbps two-pass phone copy,
  targeting less than 25 MB. It preserves every 60 fps frame.

Use `--finish-only` to validate and finish completed ranges. It never starts a
workflow. Do not commit media, fonts, frames, caches or audio features.

## Validation

```bash
python sol_edits/v4/check_media.py \
  work/sol4/Sol-V4-Nine-Colours-Upgraded-1080p60.mp4 \
  work/sol4/Sol-V4-Nine-Colours-Upgraded-review-720p60.mp4
python sol_edits/v4/check_audio.py --tail-seconds .02 \
  --video work/sol4/Sol-V4-Nine-Colours-Upgraded-1080p60.mp4 \
  --out work/sol4/master-audio-check.json
python sol_edits/v4/check_seams.py
python sol_edits/v4/check_music_identity.py \
  --reference '/path/to/Film 10, Nine Colours (share).mp4' \
  --video work/sol4/Sol-V4-Nine-Colours-Upgraded-1080p60.mp4 \
  --out work/sol4/original-music-match.json
python sol_edits/v4/inspect_motion.py \
  work/sol4/Sol-V4-Nine-Colours-Upgraded-review-720p60.mp4 \
  --out work/sol4/motion-check.json
```

These checks verify decoded cadence, sound alignment and split boundaries. They
do not establish artistic quality or listening approval. Native motion previews,
acting, reflected text, final eight seconds and the final frame also need visual
review. Recorded findings and actual local render cost are in `VALIDATION.md`.
