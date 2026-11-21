# Promo design example verification

Rendered November 20, 2026, on the cloud CPU with Mesa llvmpipe. This is an
isolated proposal based on the approved Film 10 Nine Colours Revision 3. No
creative approval is recorded.

## Complete 1080p delivery

| Check | Actual result |
|---|---|
| Picture | 1920 x 1080, 600 decoded frames, nominal and average 60/1 fps |
| Duration | Video and audio both 10.000000 seconds |
| Video format | H.264 High, yuv420p, limited-range Rec.709 SDR |
| Audio | AAC stereo, 48 kHz, original medley excerpt |
| Maximum frame timestamp error | 0.333 microseconds |
| Decoded audio peak | -2.643 dBFS; zero clipped samples |
| Final 250 ms audio RMS | -48.997 dBFS |
| Motion scan | All 600 frames decoded; no warnings or flicker/shimmer candidates |
| Native rendering and assembly wall time | 143.071 seconds with two concurrent CPU workers |
| File size | 6,633,692 bytes |

The final decoded AAC packet includes codec padding. The MP4 stream duration is
exactly ten seconds; audio-ending measurements use the intended ten-second
interval. No new music was generated, and the original source file's hash was
verified unchanged.

1080p movie SHA-256:

```text
910cfd1c776d6e81b168c4b22e724a4a99fe2877c5af953bafe7e9bf6ef866c7
```

## Visual and motion review

Native stills were inspected at the opening, 5.11 seconds, the final accent and
the end. A twelve-frame sheet from the actual delivered movie was also
inspected. The concert title and event details remained readable, the three
families of light gathered coherently, and the sampled frames showed no trails
crossing principal lettering or full-frame white-out.

An early transparent-ribbon depth-write artifact was found in the still review
and corrected before the completed render. Transparent elements now depth-test
against Earth without writing opaque rectangular coverage into the depth buffer.

Frame 307 was decoded and converted back to sRGB before comparison with its
exact native source PNG. Mean absolute RGB error was 1.213 levels out of 255;
PSNR was 39.375 dB. The 95th-percentile absolute channel error was four levels.
There was no gross encoding color shift.

The actual shared camera track was evaluated at 120 Hz: maximum speed 1.3524 m/s,
maximum acceleration 0.6580 m/s squared and maximum sampled jerk 0.6683 m/s
cubed. Endpoint easing is C2. This does not claim mathematically continuous jerk
or prove that every viewer will prefer the design.

The nine streams were sampled at 601 times. All positions were finite,
and the minimum distance from Earth's center was 2.03278 m, outside its 1.55 m
radius. Symbol geometry and frame-order independence were also checked.

No real-time playback claim is made for this cloud environment. The checks are
technical evidence and sampled visual review; artistic approval remains with
the owner.

## Native 4K delivery

The full ten-second native 4K movie completed and passed independent checks.
The delivered filename is `Mothers-Love-Promo-Design-Example-4K60.mp4`.

| Check | Actual result |
|---|---|
| Picture | 3840 x 2160, 600 decoded frames, nominal and average 60/1 fps |
| Duration | Video and audio both 10.000000 seconds |
| Video format | H.264 High, yuv420p, limited-range Rec.709 SDR |
| Audio | AAC stereo, 48 kHz; same verified original music excerpt |
| Maximum frame timestamp error | 0.333 microseconds |
| Decoded audio peak | -2.643 dBFS; zero clipped samples |
| Final 250 ms audio RMS | -48.997 dBFS |
| Motion scan | All 600 frames decoded; no warnings or flicker/shimmer candidates |
| Native rendering and assembly wall time | 570.131 seconds with two concurrent CPU workers |
| File size | 14,979,868 bytes |

Every frame was drawn at native 3840 x 2160 with two real scene evaluations per
frame. This was not an upscale or an interpolated frame-rate conversion.

The actual decoded native frame 307 was inspected and compared with its exact
source PNG after inversion of the Rec.709 conversion. Mean absolute RGB error
was 0.906 levels out of 255; PSNR was 42.237 dB. The 95th-percentile absolute
channel error was three levels. The native keyframe retained clear typography,
globe detail, cloud layers and separate colored light paths.

4K movie SHA-256:

```text
ed5b81a6c16b01cf4219e21a8506e0cdb8a2f182022fd5ea7baa030d3f358c49
```

## Evidence and preservation

Detailed private reports live under `work/promo-design-example/`:
`audio-analysis.json`, `final/delivery.json`, `final/qa-independent.json`,
`4k/delivery.json`, `4k/qa-independent.json`, and decoded contact sheets.
Render receipts record source, geographic-mask and font hashes. The isolated
builder's cache and output-replacement limits are documented in `README.md`.

Source audio SHA-256:

```text
e8731d3a15fc2dc47cf6abf1d37aa42381e2297ae2efd39f22db998fa3200f82
```

The approved movie, shared engine/acting/scene modules, source music and Render
workflow were not modified. No paid service, cloud GPU provider or Mac rendering
was used. Generated video, frames, private reports and caches are excluded from
Git.
