# Song 11 full-run host cohort review

Reviewed 2026-11-23 UTC by an independent task agent. No picture, adapter, request, manifest, or receipt source was changed during this review.

## Finding

The mismatch is real, but the observed mismatch is confined to the GitHub host image label and kernel/platform string. It is not a difference in the recorded artistic source, animation source, shaders, assets, fonts, analysis maps, request, render settings, Python packages, Mesa package versions, FFmpeg version, or deterministic thread controls.

The existing `tools/s11_cloud/assemble.py` intentionally rejects different full fingerprints. Keep this default intact. A separate, explicitly named compatibility assembler under `tools/s11_delivery` can accept this *specific* completed run if it enumerates the two observed full fingerprints and retains every integrity/input/stream/coverage check. This should be described as reviewed compatible host cohorts, never as a single identical runtime or byte-reproducibility proof.

## Exact identities

Producing commit: `eec8d16519ea82309ef851975792e9dfc548da03`.

Run: `45108198761`; request: `s11-renewed-20261123-master`.

| Full fingerprint | Image version | Platform |
| --- | --- | --- |
| `2188eb82bbb9c539367a3424630dbcca818f313950751afc2c72e18c0f661d7c` | `20261116.133.1` | `Linux-7.0.0-1014-aws-x86_64-with-glibc2.39` |
| `c34e7f5bde42bb5fb5568817872b16521dcf3acfffe4ab9c2c95066a15ce8ce7` | `20261116.376.1` | `Linux-7.0.0-1017-azure-x86_64-with-glibc2.39` |

Removing only `fingerprint`, `runtime.github_image_version`, and `runtime.platform` yields the same canonical SHA256 contract digest for each observed cohort:

`87b19dea408188d88eef2bad616adb606ef84f1545b0259d555d8ec46509aef4`.

This digest is supporting comparison evidence, not a replacement for verifying each original full fingerprint. A third full fingerprint requires another explicit review, even if those two host fields account for it.

## Additional evidence from completed worker logs

Existing job logs were retrieved through the GitHub connector for part 0 (`137474297516`) and part 7 (`137474297616`). The extracts are saved in `project-docs/production-system/evidence/s11-host-cohort-renderer-logs.json`.

Both renderers report `llvmpipe (LLVM 20.1.2, 256 bits)`, native `[1920, 1080]`, and `samples: 2`.

Both jobs installed `libx264-164` version `2:0.164.3108+git31e19f9-1`, both recorded Mesa `25.2.8-0ubuntu0.24.04.5`, and both ran the libc-bin `2.39-0ubuntu8.12` trigger. Both use runner agent `2.338.2` and image provisioner `20261111.635`.

The exact manifest runtime captures all 33 Python package versions (including NumPy, ModernGL, glcontext, llvmlite, and Numba), Python 3.12.14, x86_64, software rendering, LP threads 2, single BLAS/OMP/Numba threads, fixed Python hash seed, FFmpeg's first version line, and OpenSSL's first version line.

## Limits and residual risk

The manifest does not record the CPU model/features, selected SIMD dispatch, every shared-library binary hash, GL_VENDOR/GL_VERSION, or the entire FFmpeg build configuration. GL_RENDERER is logged but not bound inside the encrypted artifact's identity. Therefore, the evidence does not establish bit-identical rendering across hosts. Different CPUs can in principle produce small floating-point/encoding differences even with matching package labels. A common-frame comparison would be needed for a strong numerical equivalence claim; it is unnecessary to claim or promise that for this visually reviewed movie delivery.

There is no observed evidence here of changed motion timing, missing geometry, changed scene data, or changed color settings. The matching software renderer and package versions make broad image differences less likely; this is an inference supported by the runtime evidence, not a demonstrated pixel-equality result.

## Required delivery acceptance

1. Authenticate every CMS envelope and inventory. Recompute every original full fingerprint before considering compatibility.
2. Require the exact frozen request and source/adapter mapping. Require identical complete runtime maps after excluding only the two reviewed host fields. Explicitly enumerate accepted full fingerprints and exact corresponding host metadata, not wildcard platform/image matching.
3. Validate each part's receipt against its own full fingerprint; preserve that fingerprint in the final manifest. Reject altered hashes, waveform-bearing chunks, incorrect stream formats, wrong part indices/ranges, gaps, overlaps, or duplicates.
4. Preserve all 40 original per-part identities in the delivery receipt. Record the compatibility decision, evidence paths, comparison digest, exact accepted cohorts, and limitation on byte reproducibility.
5. Review the actual encoded frames on both sides of every join; inspect dense short windows across each cross-cohort join for a brightness/geometry/motion discontinuity. Pay particular attention to joins within one camera shot, since scene cuts can conceal small host differences. This is real output acceptance and must be completed before final delivery status is marked passed.
6. Run the complete decode/timestamp/frame-count/audio verification on the assembled master. Keep final review honest about sampled visual review versus uninterrupted playback.

Future workflow improvement after this frozen run: bind GL renderer/library/CPU metadata and a small common reference-frame sentinel into each job's receipt, or render in a pinned container and still audit CPU/driver details. Do not modify the currently producing request merely to collect metadata already available from logs.

## Evidence status

This record permits the specifically scoped assembly path for subsequent QA. It does not approve the completed film, certify every join, or record owner creative approval. The initial blocker remains preserved as historical evidence of why this review was required.
