# Nine Colours upgraded, Sol V4

The owner explicitly chose the original Film 10 concept and soundtrack. This
revision, completed on 2026-11-16, preserves that ride and medley while updating its models, acting,
campaign text and cards. PR #68 is a separate draft. No competitor branch or
protected file is edited, nothing is merged and no Render workflow is triggered.

## Source and musical identity

The source snapshot is 3d8dbc40e8a9cc7fe7b5f19f230f3fbd4af866f8, verified against
Actions run 43734065813. The actual original share video is 60 seconds at 30 fps.
The output adds two quiet seconds and renders each scene sample at 60 fps.

The repository medley SHA-256 is
`e8731d3a15fc2dc47cf6abf1d37aa42381e2297ae2efd39f22db998fa3200f82`.
The score uses the complete original 60 seconds with a fixed gain of
1.2366468897338798 and a 100 ms entrance ease. It introduces no internal song
edits, tempo changes or new joins. Original joins are intentionally retained,
following the owner's choice of this soundtrack.

Direct comparison of the new score with the original reference at 12 positions
from reference time 5 to 58.5 seconds measures zero lag after the two-second
offset, with correlations from 0.99618 to 0.99982. Source peak is 0.91000 and the
final 20 ms RMS is -92.39 dBFS. The original ending and final musical hit remain.
No ElevenLabs media, generated music or voiceover is used.

## Visual review and corrections

The actual reference video was inspected. The new opening, nine expressions,
reflected gate, dancer, hands, prayer, rising braid, morning and official card
were inspected in stills. A native 60 fps five-second dancer/loop/dive preview
was reviewed through dense 10 fps frame strips. The full-resolution final
12.4 seconds were inspected, including the final eight seconds and final frame.

The seven-second opening requires later first-word arrivals than the old film.
The first two comet pens and the blue gate's birth times were aligned to those
words, so each pen writes before leading the flight. The affected first two
native sections were restarted; their discarded CPU cost is recorded separately.
A near-lens ribbon triangle was found and corrected before production. Opaque
arm stumps were removed by limiting solid hand detail to palms and fingers;
the adjoining arms remain soft trails of light.

The opening reads fully from 0 to 7 seconds. All nine main phrases read for at
least 2.5 seconds; the decorative date motif now reads for 2.51 seconds. The
complete final card reads from 55 to 62 seconds. The exact campaign logo,
wording, Sunday December 6, 4:30 PM, church name and Las Vegas address remain.
The original lake and coloured arch move behind the invitation; a small push
affects the complete picture rather than the scene alone.

## Final encoded checks

The native CRF 16 archive, 1080p download and 720p review each decode to 3720
frames at 60/1 fps, exactly 62.000 seconds. Every one of the 3719 presentation
timestamp intervals in each file is 1/60 second. Audio stream durations pass
the 50 ms sync tolerance. All 16 split-boundary raw samples match independent
ordered renders; no missing or duplicate range frames were found.

The delivered master and review each match the original reference audio at all
12 sampled positions, with zero lag after the two-second lead-in. The lowest
correlations are 0.99610 and 0.99357 respectively. Each also measures zero lag
against the source score at six positions. Decoded AAC sample peaks are 0.91396
and 0.92548, without clipping. The audible final second and quiet final release
retain the original medley's ending.

The encoded opening/gate sequence, apology/embrace, dancer/loop, hands, closing
eight seconds and final frame were visually inspected through dense motion
strips, alongside the nine-expression still review. The motion triage scan finds
no near-identical hold longer than 1.5 seconds. Its p95 grey-frame difference
and jitter are 25.93 and 42.61. These are diagnostics, not an artistic verdict.

## Local render cost and delivery

Native production used 109.85 CPU minutes and 38.42 measured wall minutes on
software llvmpipe with a 4 CPU quota. The two restarted opening sections account
for another 20.93 CPU minutes. Assembly, range validation, muxing and two-pass
delivery encodes used 13.25 CPU minutes and 5.82 wall minutes. The measured
production total is 144.02 CPU minutes and 44.24 wall minutes. Peak worker RSS
was about 1.87 GiB. Previews and inspection decodes are additional. No dollar
charge is inferred from CPU time; no paid GitHub Render workflow was run.

The native archive is 112726591 bytes and stays under `work/sol4/`. The Drive
connector's 100 MiB limit is handled by a separate 11 Mbps 1080p60 download,
88183660 bytes. The phone review is 23218355 bytes. Both uploaded files were
read back by ID, name, size and destination folder, and fetched as chat files.

- [1080p60 download in Drive](https://drive.google.com/file/d/1cBm_BXG0dZsLcIializBHDO4yj5MVY0T/view)
- [720p60 phone review in Drive](https://drive.google.com/file/d/1K_mMWnoch5hYzQjyLF0oUaKuKkVvjxEQ/view)

## Limits

The figures remain stylized gold characters. Surface volume, facial sampling,
cloth and gestures are improved; this is not detailed facial performance.
Captured body motion and cloth still derive from the engine's existing source
cadences, with interpolation and local pose smoothing. The original fast half
loop and rising corkscrew remain intentionally intense. Some ribbon bends and
fine star/particle grain remain part of the reference's visual language.

The main soundtrack is unchanged internally. Ear-based listening is unavailable
in this environment; identity, level and alignment checks cannot establish
listening approval. No claim to have listened to every join is made.
