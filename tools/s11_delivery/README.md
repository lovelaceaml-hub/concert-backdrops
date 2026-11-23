# Song 11 delivery and reviewed host assembly

These tools assemble and check the complete **Almighty God Knows the Future** recreation. Assembly and automated checks do not constitute visual or owner creative approval.

## Exact scope of the reviewed host route

`assemble_reviewed.py` applies only to producing commit `eec8d16519ea82309ef851975792e9dfc548da03`, GitHub Actions run `45108198761`, and request `s11-renewed-20261123-master`: 40 parts, 16,500 native 1920×1080 frames at 60 fps, two temporal samples, and a 275-second result.

Two hosted runner images produced different complete runtime fingerprints. The recorded source, request, dependencies, renderer, and render controls match; only the recorded image version and platform string differ. The persisted [review](../../project-docs/production-system/evidence/s11-host-cohort-review.md) explains the evidence and its limits. The [policy](../../project-docs/production-system/evidence/s11-host-cohort-policy.json) enumerates the two exact accepted fingerprints and hashes its supporting evidence. It permits assembly for mandatory final QA; it does not claim byte-identical runtimes or completed visual acceptance.

The assembler loads its request, source manifest, and adapter hashes from the immutable producing commit, not current HEAD. The checkout must contain that Git commit. Original full fingerprints and per-part assignments remain in the assembled receipt. All 40 authenticated picture artifacts, the corresponding private recovery key, and the verified original prepared score are required locally. Do not commit the private key, original recording, prepared score, or decrypted picture artifacts.

## Assemble this reviewed request

Run from the repository root after all 40 encrypted artifacts have been collected. Use a new output name if an existing output or extraction directory is present; existing output is preserved.

```bash
.venv/bin/python -m tools.s11_delivery.assemble_reviewed \
  --encrypted work/s11_cloud/downloaded-master \
  --key work/s11_cloud/private/recipient-private.pem \
  --policy project-docs/production-system/evidence/s11-host-cohort-policy.json \
  --out work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60.mp4
```

This authenticates and checks the artifacts, preserves their original identities, copies the encoded pictures without another picture encode, and adds the verified local score once as AAC at 48 kHz. Its receipt explicitly leaves technical, cross-cohort join, and story/costume QA pending.

## Check the encoded master

```bash
.venv/bin/python tools/s11_delivery/verify.py \
  --video work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60.mp4 \
  --score work/s11_full2/score.wav \
  --out work/s11_cloud/master-encoded-check.json
```

The check covers the complete decode, dimensions, frame rate, color tags, frame count, presentation timestamps, audio correlation against the original prepared score, and silent ending. A successful receipt is technical evidence; it does not evaluate costume coverage or graceful movement.

## Prepare and perform visual review

```bash
.venv/bin/python tools/s11_delivery/story_review.py \
  --video work/s11_cloud/Almighty_God_Knows_the_Future_Renewed_1080p60.mp4 \
  --parts 40 \
  --out work/s11_cloud/master-story-review
```

Inspect the extracted sheets and selected native frames. Review before and after every render-part join, and dense short motion intervals across cross-cohort joins, especially joins within the same camera shot. Confirm the story, titles, costumes, compositions, representative performance motion, and ending. Extraction alone is not review. Record observed findings and resolve anomalies before marking final QA passed. Distinguish sampled visual inspection and complete technical decode from uninterrupted playback of the entire film.

The assembler's validation tests are:

```bash
.venv/bin/python -m unittest tools.s11_delivery.test_assemble_reviewed -v
```

## Future requests

Use the original strict `tools.s11_cloud.assemble` route by default. The reviewed route deliberately rejects every new request or unknown full fingerprint, including a new host whose normalized fields otherwise match. A future mismatch requires its own evidence and explicit compatibility review; do not broaden this policy merely to make an assembly pass. Keep the producing picture source separate from later delivery documentation or maintenance commits.
