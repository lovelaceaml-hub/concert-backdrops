# Validation of Film 10 with minor additions

## Fidelity and frame order

Reference: original Film 10 render 1, commit
`d928ff9eafe02ac3150f0c646bdcc497fe5a7278`, run 43726203825.

All 82 original engine Python files in the private snapshot match their Git
blob hashes. The camera, world, people, word effects and original shader code
are loaded from that snapshot. No shared or protected file was edited.

At original times 0, 0.5, 4, 6.5, 9, 13.5, 18, 23.5, 25.5, 30, 34, 38.5, 41.5,
44, 48.5 and 51 s, the original renderer and the new wrapper with additions
disabled produced identical raw 1920x1080 RGB frames at 60 fps. All 16 SHA-256
comparisons passed, with zero changed pixels. The original closing card is
intentionally replaced after original time 51.4 s.

With all additions enabled, final times 0, 2.5, 6, 11, 19, 27.5, 40.5, 50.5,
53, 54.5, 54.75, 55 and 61.98 s were rendered in forward and reverse order in
fresh processes. All 13 raw-frame hash comparisons passed.

This establishes fidelity to the original engine at the tested times. It does
not claim pixel identity for the added art, the replaced closing card, the
extra 60 fps samples, or a lossy encode compared with the old 720p30 share MP4.

## Soundtrack

The existing approved `concert-medley-leadin.mp3` is decoded without a new
arrangement, tempo change or gain adjustment. Its first 1.9 s are silent. The
stereo PCM source peaks at -2.624 dBFS, with zero full-scale samples. The last
10 ms peak at -93.177 dBFS. The original final musical accent remains, with
59.5 to 60.7 s averaging -13.638 dBFS RMS.

The existing original song joins and loud final accent are retained as part
of the owner's selected film. The final second is not forced below -45 dBFS;
the actual final release is checked separately. No human listening audition
is claimed by these signal measurements.

## Visual review

Full-size stills were inspected for the opening, signature, symbols, globe,
logo handover and closing card. A duplicate logo during the handover was found
and corrected before the full export. Dense review then found the logo rising
before the globe had fully disappeared. The added morph was shortened by 0.5 s
and both affected sections were rendered again. The final correction passed all
13 forward/reverse checks; eight sampled frames before 53 s remained identical
to the previous pass. The original bright bursts, fast camera
rolls, hoop crossings and word reflections are preserved as directed.

Private source hashes, raw-frame hashes and reports are under
`work/nine_colours_minor/`. Only source and this written record are committed.

The 15.5 s motion-scan alert was reproduced in the unmodified original engine:
its 160x90 grayscale frame difference is 29.954 levels, versus 30.030 in the
encoded master. This is the original comet passing close to the lens, not a
render-part discontinuity.

## Final encoded delivery

Both final files passed tools/nine_colours/verify.py after the corrected ending
was assembled. Each has 3720 frames, native 60 fps, 62.000 s video and audio,
zero consecutive identical frames, and no missing presentation timestamps.
Maximum timestamp step error is 0.667 microseconds. Dense 10 fps sheets were
reviewed across all eight sections, including the corrected finale and outro.

| Metric | 1080p60 master | 720p60 phone |
|---|---:|---:|
| File bytes | 102934999 | 21016563 |
| Audio sample peak, dBFS | -2.593 | -2.494 |
| Integrated loudness, LUFS | -13.0 | -13.0 |
| True peak, dBTP | -2.6 | -2.5 |
| Final 10 ms peak, dBFS | -93.05 | -93.257 |

The card is fully readable from 55 s through the last frame. Its background
continues moving: no frozen stretch or black ending was introduced.

[Phone copy](https://drive.google.com/file/d/1jsLihGhX6RgmXOkm4IT9te89AgD5nDlc/view)
and [1080p master](https://drive.google.com/file/d/1c7P_0moEF2jaEoIN4SxlvGKZMOUKiT3j/view)
are saved in the existing Videos folder. No media is committed.

The phone copy was downloaded back from Drive. Its SHA-256 exactly matches
the local final export; the same verified file is attached in chat.
