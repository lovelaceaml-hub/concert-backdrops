# Validation of the opening and world revision

## Source and unchanged chapters

Reference: original Film 10 render 1, commit
`d928ff9eafe02ac3150f0c646bdcc497fe5a7278`, run 43726203825.
All 82 original engine Python files in the private snapshot match their Git
blob hashes. Shared or protected engine, song, acting, music and workflow files
were not edited. Changes are confined to `tools/nine_colours_minor/`.

With the additions disabled, original times 4, 6.5, 9, 13.5, 18, 23.5, 25.5,
30, 32, 41.5, 44 and 48.0 s match the original renderer's raw 1920x1080 RGB
frames exactly. All 12 SHA-256 comparisons pass, with zero changed pixels.
The opening, Respect and finale are intentionally different.

The initial 48.5 s test was inside the original finale burst's 1.1 s rise,
which begins at original 48.37 s. It correctly differed because that burst is
replaced to make the globe visible. This sample was replaced with independently
rendered 48.0 s frames from both renderers. The original failure report is
retained privately; the final checked-in test uses the corrected boundary.

With all additions enabled, final times 0, 6.3, 7.2, 8, 18, 40, 42, 45.9,
46.3, 54.5, 55.5, 56.8, 57.7, 58.5, 59 and 65.98 s were rendered in forward
and reverse order in fresh processes. All 16 raw-frame hashes match. The complete 12-moment fidelity and
16-moment order checks passed again after the opening camera adjustment.
Thirteen sampled final frames from 8 s onward also match the first pass
exactly, confirming that the correction is confined to the opening.

This is a scoped fidelity check, not a claim that the added art, replaced
passages or lossy encodes are pixel-identical to the original film.

## Soundtrack

The 66.000 s PCM source is exactly four seconds of silence followed by the
existing approved lead-in soundtrack decoded to stereo 48 kHz, 24-bit PCM.
The decoded samples after the delay match byte-for-byte. No arrangement,
tempo, gain or internal join changes were made. Original audio features remain
on the original clock, shifted with the film by six seconds.

The original final musical accent is retained. Encoded audio checks measure
clipping, the intended quiet lead-in, joins and the final release. Signal
measurements do not claim a human listening audition.

## Visual review and delivery

Opening, Respect, Earth/symbols, logo handover and closing-card stills were
inspected. Preview checks caught and corrected a title-protection issue, an
undefined shader power on negative coordinates, and missing alpha blending
on the decorative hearts before the final export. Replacing existing scene
entries was also corrected to preserve their draw order and render flags.

The first encoded opening review found the city line too close to the bright
light. The opening camera now places that light and the horizon lower, matching
the reference composition, and returns to the original path before Greeting.
The first render part was replaced before final assembly; the checked later
frames remain identical. Half-second frame sheets were inspected across all
eight sections, with additional closely spaced checks of the logo handover.
The new Respect scene grows from two streams into a nine-petal light form.
The finale clearly shows the Earth and expression symbols against the night sky,
then the heart logo and pastel card. The card remains readable through the last
frame, with moving background detail and drifting hearts.

Private source hashes, raw-frame hashes, media, caches and reports remain under
`work/nine_colours_revision2/` and `out/nine_colours_revision2/`. No generated
media is committed. The previous delivered version remains available unchanged.

## Final encoded delivery

Both final exports pass `tools/nine_colours_minor/verify.py`: 3960 frames,
native 60 fps, 66.000 s video and audio, zero consecutive duplicate frames,
and maximum timestamp step error of 0.667 microseconds. Render-part join
differences are within 1.39 times their surrounding median. The original
fast vortex approach remains at 54 to 55.5 s; the motion scan identifies it
as the busiest passage. This revision does not claim to remove that chosen
Film 10 camera motion.

| Metric | 1080p60 master | 720p60 phone |
|---|---:|---:|
| File bytes | 95423428 | 21833340 |
| Audio sample peak, dBFS | -2.682 | -2.317 |
| Integrated loudness, LUFS | -13.0 | -13.0 |
| True peak, dBTP | -2.7 | -2.3 |
| Final 10 ms peak, dBFS | -92.949 | -92.080 |
| Final accent RMS, dBFS | -13.670 | -13.759 |

The first 5.9 s remain silent. No clipping, frozen frame run or black ending
was introduced. Background and heart motion continue beneath the steady
closing text.

[Phone copy](https://drive.google.com/file/d/1FZgfE34WaqerISwK93ZfrjeiOQf3Kh44/view)
and [1080p master](https://drive.google.com/file/d/1bNeVf4r7cUpwWKdWCbZWviJWbDBSWvU2/view)
are saved in the existing Videos folder. The previous delivery is preserved.

The phone copy was downloaded back from Drive. Its SHA-256 matches the
local final export exactly; that verified download is attached in chat.
