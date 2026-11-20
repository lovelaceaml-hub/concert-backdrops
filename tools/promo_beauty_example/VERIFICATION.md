# Beauty study verification

20 November 2026. **The full thirty-second movie is rendering.** This checkpoint records completed evidence without claiming a finished delivery or creative approval. The final media checks will replace this status after assembly.

## Completed evidence

- Read the full Song 11 production account at commit `34f835206dcb26cfa0bd7e321171d3d224e3aa7d` and inspected decoded reference frames from the available approved promo.
- Prepared the verified original recording with SHA256 `70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004`. Both analysis maps were regenerated with the project scripts because the archived copies were behind a sign-in page.
- Inspected native 1080p stills of the conductor, ensemble, city and procession entry. Kept the conductor focus correction and bounded stage-light adjustment.
- Rendered and inspected a native **3840 x 2160** conductor still, using two HDR temporal samples. SHA256: `76ccd2c942db1228969b0f020f577a4c14304c0afa298857576a4a825d2c10bd`. This is a still test; a full 4K movie has not been rendered.
- Inspected a 126-frame internal motion contact sheet covering the opening gesture and first cut. That pilot was correctly left outside delivery when its source-freeze gate detected source files changing during completion of the export tools.
- Exercised the actual video verifier on a two-second encoded fixture. It decoded 120 frames with a maximum timestamp error of approximately 0.000000333 seconds, and caught missing color tags before the encoder metadata was corrected.
- Read-only review of the final frozen renderer, builder and verifier found no delivery-blocking issue. The nine shots contain eight internal cuts at frames `102, 354, 447, 642, 726, 1158, 1418, 1694`.

## Active render

The movie target is native 1920 x 1080, 60 fps, 1,800 frames and thirty seconds, using the original performance and cameras. Picture source time is 97.7 to 127.7 seconds and audio time is 97.8 to 127.8 seconds. The existing 0.1-second picture delay is applied once. The contiguous excerpt ends during the next scene's entry.

A four-worker attempt lost one worker to SIGKILL as memory demand increased and produced no accepted chunks. The coordinator then restarted with two workers. After measuring steady memory use, a third independent worker began the final queue's landscape chunk from the identical frozen source and parameters. The coordinator will reuse it only if its complete receipt and movie digest match. All rendering is on the cloud CPU.

Still frames and a contact sheet do not establish complete musical synchronization, natural acting or the quality of the final encoded sequence. Full video decode, audio decode, timing checks, native evidence inspection and final checksums remain pending at this checkpoint.

## Provenance limits

The completed Song 11 master was behind a sign-in page and was not inspected. Its account records a mixture of source versions in the delivered film and later unrendered changes. This study reconstructs a selected passage from the accessible source, retaining its choreography and recording; it does not claim an exact copy of that completed master. The regenerated feature maps are estimates from the mixed recording, and the original authored absolute cues remain authoritative.

The source engine produces RGB8 after its existing filmic and display treatment. The movie target is 8-bit SDR H.264 with the matching BT.709 matrix and range conversion. Native 60 fps output does not replace the existing 15 fps interpolated crowd performances with newly authored poses.
