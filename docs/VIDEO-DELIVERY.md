# Native 4K60 and 10-bit SDR exports

The renderer supplies the detail and the motion. The finishing pipeline preserves the chosen frame clock, validates the source precision, and creates a specific delivery format. The same rendered PNG sequence can produce a compact viewing file and an editing master without rendering the 3D scene twice.

## Choose the output

| Profile | File | Video | Audio | Purpose |
| --- | --- | --- | --- | --- |
| `h264` | `master.mp4` | H.264 High, 8-bit 4:2:0, CRF 16 | AAC, 256 kb/s, 48 kHz | Compatible review and playback |
| `hevc10` | `master-10bit.mp4` | HEVC Main 10, 10-bit 4:2:0, CRF 18, `hvc1` | AAC, 256 kb/s, 48 kHz | Compact 10-bit delivery for a compatible player |
| `prores422hq` | `master-prores422hq.mov` | ProRes 422 HQ, 10-bit 4:2:2 | 24-bit PCM, 48 kHz | Editing intermediate and larger finishing master |

All three are Rec.709 SDR. A 10-bit container is not HDR and does not restore precision lost in an 8-bit source. The high-bit profiles require **actual 16-bit PNGs for every source frame**. The assembler reads each PNG's IHDR, then checks the encoded stream with ffprobe. Setting a manifest flag without changing the renderer is insufficient.

The high-bit path currently uses Blender's display-referred RGB16 output. The existing browser compositor and p3d outputs remain 8-bit paths. Use `h264` for their outputs until they have a real higher-precision frame path. The Remotion editor explicitly rejects a high-bit profile, and FFmpeg explicitly rejects requested captions it cannot composite. Put titles into the Blender scene when using the direct 16-bit finishing path.

## Project settings

Start a new timeline at 60 fps and render the final scene at 3840 by 2160. Increasing output dimensions after rendering a smaller source is an upscale; changing only the playback rate changes the duration. The project clock is fixed across every quality preset, shot, timing event and export.

```yaml
video:
  width: 3840
  height: 2160
  fps: 60
quality:
  draft:
    width: 960
    height: 540
    samples: 8
    image_bit_depth: 8
  review:
    width: 1920
    height: 1080
    samples: 24
    image_bit_depth: 16
  final:
    width: 3840
    height: 2160
    samples: 64
    image_bit_depth: 16
delivery:
  profile: hevc10
  source_transfer: srgb
  color_space: rec709
  profiles_by_quality:
    draft: h264
    review: h264
    final: hevc10
```

Profile precedence is: explicit `--profile`, then `profiles_by_quality`, then `delivery.profile` for final. Other qualities default to H.264. Samples are starting values to judge with native-size stills; they are not a quality guarantee.

## Repeatable sequence

Run these commands in the configured cloud checkout. They do not configure a GPU provider, dispatch a paid render, or opt in to Mac rendering. `concert-study` below is a project id created with `video new`.

```bash
./scripts/video validate concert-study
./scripts/video motion-qa concert-study
./scripts/video benchmark concert-study --qualities review 4k-check
./scripts/video preview concert-study --quality draft
./scripts/video review concert-study --quality draft
```

Inspect the native-size benchmark frames and the actual moving preview. Approve composition, figure poses, camera speed, title legibility, bloom and timing before spending time on the full final frame sequence. After those decisions, render and encode the chosen project:

```bash
./scripts/video render concert-study --quality final
./scripts/video finalize concert-study --quality final --profile prores422hq
./scripts/video review concert-study --quality final
./scripts/video archive concert-study --quality final --destination /existing/private/archive
./scripts/video finalize concert-study --quality final --profile hevc10
./scripts/video review concert-study --quality final
./scripts/video archive concert-study --quality final --destination /existing/private/archive
```

Both encodes read the same RGB16 frames. The ProRes profile creates ProRes shot intermediates; the HEVC profile encodes directly from the PNGs and concatenates matching HEVC clips without another video encode. A compatibility copy is available with `--profile h264`.

`master.json`, `qa.json` and `review.html` describe the **most recently assembled profile**. Archive each profile after its own QA if you need both with complete evidence. Older movie files can coexist, but they are not the active master. The review page links the active filename. ProRes and HEVC may need an external compatible player instead of in-browser playback.

Creative approval is separate from technical QA. The `approve` command records an actual completed human review; it must never be filled automatically merely because encoding checks passed. A new assembly clears approval for the previous master.

## Color and precision

The declared source is display-referred sRGB PNG, including Blender's AgX display output. FFmpeg converts the transfer, color matrix and range with `zscale`, dithers to the target precision, and writes BT.709 primaries, transfer and matrix metadata. The target uses the BT.1886 gamma-2.4 display convention in [zimg's transfer implementation](https://github.com/sekrit-twc/zimg/blob/master/src/zimg/colorspace/gamma.cpp). This is a display-to-display conversion, not the scene-referred Rec.709 camera curve or a metadata relabel. Keep the renderer's view transform consistent with the declared source; a linear EXR sequence requires a different finishing path. A known-gray regression checks the actual converted pixel value as well as metadata.

The installed FFmpeg must expose `libx264`, `libx265` or `prores_ks` for the selected profile and the `zscale` filter. Missing capabilities cause an actionable error. No hardware encoder is selected. ProRes MOV commonly omits a separate range flag when inspected by ffprobe; the encoder receives explicitly converted limited-range YUV, while QA requires the primaries, transfer and matrix and records the implicit range limitation.

## What QA checks

Technical validation checks one video stream, native dimensions, exact decoded frame count, average and nominal frame rates, start time, duration, codec/profile, pixel format, color metadata and the active filename. It checks the expected audio stream, codec, sample rate, start and duration. Source checksums, render receipts, source bit depth and project identity bind the result to its inputs. New master receipts also record SHA-256 hashes of finishing code and dependency locks, including the editor and shared code for Remotion. Changed finishing inputs fail QA; earlier receipts without this field remain readable. A master that fails delivery validation does not replace the preceding master, receipt or approval.

The decoded movie also receives a 160 by 90 temporal scan:

- Large consecutive frame changes away from declared cuts or flashes.
- Global brightness reversals across three consecutive frames, to find possible flicker.
- Local pixel reversals, to find possible shimmer even when overall brightness is steady.
- First and second temporal differences summarized in half-second windows.
- Nearly frozen intervals longer than 1.5 seconds.

These are review warnings. Moving edges, sparkles and deliberate musical effects can trigger them. They do not prove natural body movement or measure physical camera acceleration or jerk. The separate `motion-qa` command inspects the actual camera trajectory. Neither system replaces watching the exported movie at its native frame rate.

Declare intentional flashes in the exact timing file so the scan can exclude their attack/release interval and a two-frame margin:

```yaml
events:
  - frame: 240
    kind: intentional_flash
    amplitude: 0.12
    attack_frames: 6
    release_frames: 18
```

Ordinary musical cues are not automatically exempt. The report records excluded intervals and candidate frames so a reviewer can see what was measured. There is no automatic deflicker filter that could erase an intended effect.

## Verification and references

The delivery tests generate tiny RGB16 PNGs, encode actual H.264, HEVC Main 10 and ProRes HQ files on the CPU, concatenate two shots, mux audio and run technical QA. Separate tiny decoded movies exercise alternating brightness, a smooth exposure ramp, a declared flash, local shimmer and a freeze. These tests establish the finishing path; they do not claim a full concert or a full native 4K animation has been rendered.

```bash
uv run --frozen --extra legacy python -m unittest discover -s tests/pipeline -p 'test_delivery*.py' -v
```

Implementation references: [FFmpeg codecs](https://ffmpeg.org/ffmpeg-codecs.html), [FFmpeg zscale](https://ffmpeg.org/ffmpeg-filters.html#zscale), and [FFprobe stream inspection](https://ffmpeg.org/ffprobe.html).
