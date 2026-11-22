

## Natural performance delivery and reusable workflow - PR 104

The owner's latest direction is to improve expressive whole-body movement, including dancing, while preserving the luminous character of the approved promo. The new isolated `concert-dance-study` is complete: eighteen seconds, 1,080 native 1920x1080 frames at 60 fps, two temporal samples, and the unchanged canonical Song 07 excerpt. The picture source is frozen at `0c42f4422a6b67464cb9cd84aac32008d45d4f4c`. Current code and integration record: https://github.com/lovelaceaml-hub/concert-backdrops/pull/104 .

Delivered files in Videos / Production Studies:

- [Natural-Dance-Duet-18s-1080p60.mp4](https://drive.google.com/file/d/1IImU7ohiNhI86WHtIPNB_3S0iFD2HgAH/view)
- [Natural-Dance-Duet-Native-4K.png](https://drive.google.com/file/d/1nB2MjshQhFJHe7c-KyjxcuWBBPGvFYyq/view)
- [Natural-Dance-Duet-Motion-Review.jpg](https://drive.google.com/file/d/1AmBWnRldfLNjbL9Vh31WzMEhAPby12Vm/view)

Both technical audits passed without errors or warnings. All frames decoded and their presentation timestamps match the exact 60 fps clock. All 197 frozen picture inputs remained unchanged. Three audio windows match the canonical score at zero-sample lag. Raw-byte readback verified all three Drive files. Read the delivery catalog for their exact hashes and saved backups.

The independent final-film visual review covered 89 targeted decoded samples, with the 62-sample earlier silent proof preserved separately. This was ordered-frame inspection, not real-time playback or audio listening. Slow initial preparation, prolonged raised-foot settling and a mostly held ending remain creative priorities. These studies do not inherit the owner's approval of the promo or Song 11 beauty reference.

Start a future chat with `project-docs/production-system/START-HERE.md`, `AI-HANDOFF.md`, `NATURAL-PERFORMANCE.md`, `MOTION-LIBRARY.md`, and `IMPROVEMENT-QUEUE.md` from current Git main. The motion catalog describes eight prepared clips from seven captures; new candidates are proposals, not acquired assets. Two differently staged figures currently reuse CMU 05_02 with a 0.6-second offset. Stored 30 Hz source poses are interpolated for 60 fps, and fingers are not captured performance.

Reproduce after restoring the exact private Song 07 source and pinned runtime/fonts:

```bash
./scripts/concert verify-audio s07
./scripts/concert prepare-study-audio
./scripts/video produce concert-dance-study --quality review
env PYTHONHASHSEED=0 .venv/bin/python tools/concert_review/dance.py
```

The 1080p project uses six single-thread cloud CPU workers, private per-chunk staging and one receipt coordinator. Keep picture inputs frozen for a round; the pipeline resumes only verified matching frames. The separate `concert-dance-study-4k` project configures native 3840x2160 at 60 fps with three workers. One native 4K still has rendered; the full 4K movie remains unrendered. No Mac rendering, paid service or external GPU provider was used.

The next creative pass should enrich or shorten preparation, make weight transfer through settlement more readable, author hand/head follow-through, and build complementary phrases from reviewed sources. Keep the existing 11-song queue and original approved engines intact.

The exact confirmed replacement `Concert-Production-System-Handoff-2026-11-20.zip` is already uploaded to Production System and raw-byte verified: file ID `1gp0x2dnj06eIPDuq6vSGpGtKn_bvKrML`, 350534 bytes, SHA256 `eb8bba933a37179fa970c84aecc67cbc0b493809d1e2b2e7863c3900b9606537`. All three prior Drive operations are complete. That ZIP remains an immutable historical snapshot; current Git source and these later instructions supply the new dance setup. Do not overwrite it or request the completed upload again.
