# Beauty study verification

20 November 2026. **The thirty-second native 1080p60 master is complete and its final technical verification passed with no errors or review warnings.** The movie and native 4K still have been delivered for owner review.

## Final file

| Property | Verified value |
| --- | --- |
| Movie | `work/promo-beauty-rebuild/final/Song11-Beauty-Study-30s-1080p60.mp4` |
| SHA256 | `6e4533c4527dfb81c750f8ba907e86392f0c87dca638c3daac768ece8edae82a` |
| Size | 110,865,643 bytes |
| Picture | Native 1920 x 1080, 60 fps, 1,800 frames, 30.000000 seconds |
| Video encoding | H.264 High, 8-bit SDR, YUV 4:2:0, BT.709 metadata, limited range |
| Audio | AAC LC, 48 kHz stereo, approximately 320 kbit/s |
| Sound excerpt | Source audio 97.8 to 127.8 seconds, without retiming |
| Audio treatment | -0.5 dB gain; 0.12-second entry fade and 0.25-second exit fade |

The final movie digest and byte count agree with `final/delivery.json` and the independent audio audit. Picture source time is 97.7 to 127.7 seconds, with the original 0.1-second picture delay applied once. The excerpt ends during the next scene's entry.

## Picture and clock checks

[verify.py](verify.py) decoded all 1,800 video frames without errors. Presentation timestamps increase strictly from 0 to 29.983333 seconds. Maximum reported deviation from the 60 fps grid is 0.0000003334 seconds, consistent with decimal timestamp precision.

The complete 320 x 180 display-pixel scan found zero jump candidates, zero brightness-reversal candidates and no nearly unchanged stretches. Only the eight authored cuts were exempted from the local motion heuristic: frames `102, 354, 447, 642, 726, 1158, 1418, 1694`. These form nine shots.

Native 1080p evidence was decoded at 32 selected frames, including both sides of every authored cut, shot interiors and brightness peaks. The original engine's filmic curve and display treatment are preserved. Encoding and RGB comparison use the matching BT.709 matrix and range conversion without another transfer-function conversion. Two HDR scene-motion samples do not make the encoded file HDR or 10-bit.

Local evidence under `work/promo-beauty-rebuild/`:

- `final/qa/qa-independent.json`: final-file technical pass, empty errors and review-warnings arrays.
- `final/qa/contact-sheet-independent.jpg` and `final/qa/native-6e4533c4527d/`: decoded final-master evidence.
- `final/qa/seams/seam-review-data.json` and `seam-contact.jpg`: native render-boundary strips and measurements.

These display-pixel heuristics support review; they do not establish natural anatomy, choreography, readable lettering or artistic quality.

## Render joins and recovery

Five canonical chunks were preserved with matching movie hashes and identical source/runtime/render receipts. The remaining range, frames 900 to 1200, was recovered as two 150-frame jobs. The strict join helper checked both child digests, contiguous ranges, H.264 configuration, decoded frame counts and presentation timestamps before publishing part-03.

Separate native strips cover boundaries at frames `300, 600, 900, 1050, 1200, 1500`. Recovery boundary 1050 was checked as an ordinary within-shot join, with no authored-cut exemption. Adjacent display-luma differences were 0.00908 before, 0.00903 across and 0.00654 after that join.

The boundary evidence was decoded from the first assembled movie, SHA256 `07c97660aa9e9f9604ace2ccbb5e3448607f29b8bc77b09c63d78d261a494805`. The audio-only correction preserved its compressed picture packets exactly. The before/after picture-stream SHA256 is `133dc0028980193953659a921c89c762554ebde009775b5584140bf573e78151`, establishing that this picture evidence also applies to the final movie.

## Audio alignment and headroom

The original recording was verified as SHA256 `70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004`. The prepared score remains `fa488e4805cdc43b1f0f38915d67044ef92a9e659a59ac916d4b75b4cbb6d29b`.

Initial full QA found six decoded AAC samples above full scale, with a peak of +0.098427 dBFS. The pre-encode PCM already reached full scale at those positions. An audio-only pass reduced the source excerpt by 0.5 dB before AAC encoding and copied the video stream. The original recording and prepared score were preserved.

The final decoded sample peak is **-0.2444528 dBFS**, with **zero full-scale exceedances**. The earlier movie, delivery receipt and QA remain archived in `audit/`. This is a decoded sample-peak measurement, not an inter-sample true-peak certification.

The independent final alignment audit compared prepared-score samples 4,694,400 to 6,134,400, end excluded, with the final AAC. The expected -0.5 dB gain was included in amplitude comparisons.

| Local interval | Source-audio interval | Best lag | Normalized correlation |
| --- | --- | --- | --- |
| 2 to 6 s | 99.8 to 103.8 s | 0 samples | 0.9997871 |
| 13 to 17 s | 110.8 to 114.8 s | 0 samples | 0.9998495 |
| 24 to 28 s | 121.8 to 125.8 s | 0 samples | 0.9999614 |

Across the continuous local interval 2 to 28 seconds, zero-lag correlations are 0.9998438 left and 0.9998069 right. The sampled lag shows no drift across 22 seconds.

AAC's first packet carries PTS -1024 and `skip_samples=1024`. FFmpeg handles this automatically, with no manual leading shift. The logical stream contains exactly 1,440,000 samples per channel. Its 768 extra decoder-padding samples lie beyond the declared 30-second end and were excluded from comparison.

This establishes correct technical excerpt alignment with no detected retiming. Musical and creative synchronization require separate judgment. Evidence: `audit/audio-alignment-final.json`, `audit/audio-peaks-before-gain.json` and `audit/audio-headroom-postpass.json`.

## Frozen picture source and asset provenance

All delivered pictures were rendered from [commit a7d68836c4fdc7156bbc9b839380cd65180ca2bb](https://github.com/lovelaceaml-hub/concert-backdrops/commit/a7d68836c4fdc7156bbc9b839380cd65180ca2bb). That snapshot uses the [pinned engine d928ff9](https://github.com/lovelaceaml-hub/concert-backdrops/commit/d928ff9eafe02ac3150f0c646bdcc497fe5a7278) and [reference people f43f451](https://github.com/lovelaceaml-hub/concert-backdrops/commit/f43f4514e4bc42dc25166e90160d98219f5a0db4). Its source receipts contain **333 entries**.

That historical manifest omitted the two body NPZ files and the brand land PNG. A separate checkpoint verified them against tracked blobs in their pinned commits. Completion checks confirmed identical SHA256 values and unchanged mtimes; their original mtimes preceded the render start.

| Asset | Confirmed SHA256 |
| --- | --- |
| `work/nine_colours_minor/render1/assets/p3d/body_v1.npz` | `b676d6b1f524f8d482a73c4c6d87d36fa415af19ff8e125a7789016b84edf468` |
| `work/nine_colours_revision3/claude-final/assets/p3d/body_v1.npz` | `0a72159f84b7008dcb135c79f82ae3b05df5f7361197e99ab9ca4af148c91189` |
| `assets/p3d/brand/land_2048.png` | `7a0e70fd74d1cd4940037c6c96c9f9617910f458ac49d1dccb678297771ca7dc` |

Evidence: `audit/asset-provenance.json` and `audit/asset-provenance-final.json`. These independent checks do not retroactively add files to the original manifest.

## Integrity follow-up and fresh-cache validation

After the initial movie and full QA, [render.py](render.py) gained required-file checks and hashes for all three assets. Future manifests contain **336 entries**. Future crowd caches use a namespace derived from a versioned schema and both body digests, in addition to the original prototype keys.

Mutable derived-cache files are not source inputs, and old caches are not copied into the new namespace. `P3D_BODY_ASSET` overrides, including empty values, are rejected before scene loading. [build.py](build.py) now defaults to the verified -0.5 dB audio headroom treatment for future builds.

A new cache namespace built 13 fresh crowd prototypes and rendered native frames 45 and 501 in **285.30667 seconds**. The source manifest remained frozen through that check. Both PNGs are **byte-identical** to their pre-guard native references, with zero RGB error. Comparison to the encoded movie gives the expected lossy differences:

| Native frame | Scene | New cache versus original PNG | Native versus encoded RGB MAE | PSNR |
| --- | --- | --- | ---: | ---: |
| 45 | Conductor | Identical bytes, zero RGB error | 1.764625 / 255 | 39.9648 dB |
| 501 | Stage | Identical bytes, zero RGB error | 2.376679 / 255 | 36.9065 dB |

Frame 45 PNG SHA256: `e5084a0d5981972feed79cd4e83eeef9dd759a41886d4dd5597c488cb27bbc8a`.

Frame 501 PNG SHA256: `4ae30785b176fab7c13611f951b64538307e469adda8e84f204cd626c2cc40ed`.

Small identity checks also passed: mapping order leaves the namespace unchanged; changing either body digest changes it; missing or invalid digests are rejected; and an empty body override is rejected before loading.

Evidence: `final/qa/native-after-cache-guard/receipt.json` and `comparison.json`. This is a targeted two-frame compatibility check, not a new rendering of the full movie. The historical picture source remains a7d688.

## Native 4K evidence

A separate conductor still at frame 45 was rendered natively at **3840 x 2160**, with two scene-motion samples. Its SHA256 is `76ccd2c942db1228969b0f020f577a4c14304c0afa298857576a4a825d2c10bd`.

`native-4k/frame-0045.json` records the native dimensions and confirms that it was not upscaled. The delivered movie is 1080p60; no full 4K movie was rendered in this round.

## Elapsed time

The cloud CPU render round through first assembly took **5,441.1196 seconds, or 90.69 minutes**, including recovery. The **27.8247 seconds** in the builder's completion receipt measures the final invocation that reused completed chunks and assembled them. It is not the full rendering time.

Later audio correction, final QA and fresh-cache validation are separate work. These figures describe this CPU environment and scene, not a guaranteed rendering speed elsewhere.

## Reference and review limits

The available approved promo's decoded reference frames and the [full Song 11 production account at commit 34f8352](https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/project-docs/backdrops/s11-full2/HOW-IT-WAS-MADE.md) informed this study. The completed Song 11 master was behind a sign-in page and was not inspected. Its account records multiple source versions and later unrendered changes, so this reconstructs the accessible authored passage without claiming an exact copy of that master.

Both music-analysis maps were regenerated from the verified mixed recording. The original authored absolute cues remain authoritative. Native 60 fps output samples the original performance system more frequently; the existing 15 fps interpolated crowd performances remain part of that system.

Selected native stills and motion strips were inspected. No real-time playback, complete artistic review or owner approval is claimed by these checks. The delivered movie is available for the owner to judge its movement, composition and emotional effect.
