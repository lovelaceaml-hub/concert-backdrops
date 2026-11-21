# People animation example verification

This is an isolated thirty-second proposal requested on November 20, 2026.
It does not revise the approved film, and no creative approval is recorded.

## Delivered movie

The completed file is
`Mothers-Love-People-Animation-30s-1080p60.mp4`.

| Measurement | Actual result |
| --- | --- |
| Dimensions | 1920 by 1080, native rendering |
| Duration | 30.000 seconds for both video and audio |
| Decoded frames and rate | 1,800 at exactly 60/1 fps |
| Picture | H.264 High, 8-bit YUV 4:2:0, limited-range Rec.709 SDR |
| Audio | 48 kHz stereo AAC |
| File size | 54,789,838 bytes (52.25 MiB) |
| Maximum frame timestamp error | 3.33333336e-07 seconds |
| Full temporal scan | 1,800 decoded frames |
| Flicker / shimmer candidates | 0 / 0 |
| Technical errors / review warnings | 0 / 0 |
| Decoded audio peak | -2.657 dBFS |
| Clipped audio samples | 0 |
| Final 250 ms audio RMS | -48.984 dBFS |
| Native frame 900 mean RGB error | 1.292 out of 255 |
| Native frame 900 PSNR | 37.180 dB |

The movie SHA256 is
`571d538e58ce89de34de1bcd66f1953d8c7f984e134743fce1ecaa2a80983862`.

All presentation timestamps increase regularly from 0 to 29.983333 seconds.
The temporal scanner excludes five-frame windows around each intentional cut
(frames 610 through 614 and 1166 through 1170). Its longest nearly still
interval was 0.817 seconds. These are pixel heuristics, not a proof of
natural acting. The exact native frame comparison inverts the explicit
Rec.709 conversion; its 95th-percentile absolute RGB error is 5 out of 255.
The exported H.264 picture is intentionally lossy, so it is not byte-identical
to the source PNG.

The music is seconds 30 through 60 of the original medley, with a 0.35-second
entry fade and its natural ending. The source SHA256 remains
`e8731d3a15fc2dc47cf6abf1d37aa42381e2297ae2efd39f22db998fa3200f82`.
The nominal audio has 1,440,000 samples per channel; decoding AAC also produces
768 samples of codec padding. Both presented streams are exactly 30 seconds.

The final render and assembly took 886.46 seconds with four cloud CPU
workers after the cloth caches were prepared. Renderer: Mesa llvmpipe, two
scene samples per output frame. No full 4K movie was rendered for this example.

Independent evidence was written to the ignored working directory as
`final/delivery.json`, `final/qa/qa-independent.json`, the decoded twelve-frame
contact sheet and native frame 900. Both the contact sheet and native frame
were inspected. No gross encoding color or brightness damage, missing people,
text/head collisions or unintended crops were observed in those samples.

## Human performance checks

The final wide shot contains eleven performers: two principal actors,
a conductor and eight choir placements. Six distinct physical
performances feed those placements. The complete scene contains 149,002 human
particles, with finite coordinates at the sampled gesture times.

The final performance cache fingerprint is
`bd7a942ee2b9d8814d6b4bf6da684c8d773b19b1f2aa18584682bb238f00761f`.
Cloth is simulated at a fixed 120 Hz and stored at 30 Hz for interpolated
sampling. Matching source and dependency fingerprints are required to load it.
No cache identity exception or cache migration was used.

With all six final caches loaded, sampling 8.125 seconds, then 1.1 seconds,
then 8.125 seconds again produced byte-identical particle arrays. The complete
native renderer also produced an identical frame 900 before and after frames
0, 36, 1440 and 1799. Its raw RGB SHA256 was
`9144d47b22d5abf003e8e458d1ef5e9edd45d3656a5d554eeea392f6701683fa`.
These checks cover out-of-order physical sampling and framebuffer reuse.

After rendering, the independent verifier required an explicit planar RGB
intermediate (`gbrp16le`) before its packed RGB PNG conversion. This corrects
FFmpeg format negotiation in the checker. Only `verify.py` changed after the
movie was rendered; all geometry, animation, camera, shader, typography, asset
and dependency hashes still match the movie's recorded inputs. The movie
itself was not re-encoded for this verifier correction. The published verifier
includes the correction so its documented command is repeatable.

The existing walk initially allowed the principal actors' soles to dip up to
17.043 mm and 13.806 mm below the stage. A presentation correction now moves
each complete actor and its matching anchors together during the approach.
It leaves horizontal foot planting unchanged and tapers away by 2.5 seconds.
The checked corrected sole heights are at or above the floor within 1.2e-10 m
of numerical tolerance. Sampled standing horizontal ankle drift after the
approach is zero. Sampled walking strong-contact drift was at most 1.40 mm
and 1.90 mm per 25 ms for the two actors. These are sampled checks, not a
claim of continuous collision proof.

The conductor's sampled palm targets are reached within 8.67 mm. A first wide
choir gesture came too close to neighboring arms. The final chest-height,
palms-up gesture has at least 178.8 mm between adjacent arm axes across the
checked poses from 21 to 27 seconds. Arm-axis clearance is a pose screening
measurement, not a full cloth-surface collision test.

## Visual review

Native stills were inspected through all three shots. Review led to a closer
first camera, a raised greeting caption, a softer background cloud band,
quieter reflections and less bright stage trim behind the people and closing
address. The first shot contains only the two principal performers so cropped
background bodies do not intrude at the edge.

The conductor's bent-arm silhouette, all choir heads and full bodies remain
in frame in the inspected ensemble compositions. The colored canopy stays
behind and above the group. Some of its arcs extend beyond the top edge as
intentional environmental framing. The final decoded contact sheet and native
keyframe are inspected separately from these source stills.

## Scope and limits

The delivered format is recorded above, separately from the renderer's optional
3840 by 2160 setting. This example uses original code-rendered geometry and
the project's existing human and music assets. There are no generated images,
stock footage, video upscaling or synthesized intermediate video frames.
The performance demonstrates body and hand movement; detailed facial acting
and mouth synchronization are outside this example.

No paid render service, cloud GPU provider, Mac render or GitHub Render
workflow was used. Protected engine files, approved film and original music
remain unchanged. Automated metrics do not establish natural acting or
creative approval, and no real-time playback review is claimed.
