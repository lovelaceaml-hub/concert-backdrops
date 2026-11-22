# Next performance upgrades

Research checked November 21, 2026. These are the next development choices after the original fan and silk study. They are not installed features, acquired datasets or approval of another final movie.

## 1. Author a complete phrase with visible weight transfer

The current study proves distinct roles and repeatable contact. Its main artistic limit is that the body remains mostly upright while the hands carry much of the choreography. The next useful proof is one complete six-second phrase: prepare on a supporting side, step and travel, sweep the fan, turn, arrive and recover. Pelvis height, torso counterbalance, knees, feet, head and hands need one coordinated intention.

The current rig can author this directly. If an editable external authoring stage is useful, Blender's NLA editor organizes reusable actions and blends tracks. Bake Action with Visual Keying records the evaluated transforms after constraints. That suggests an optional pipeline: author and refine a complete phrase, bake the final skeleton, export root and local rotations, then keep rendering with the existing luminous engine. This requires a real exporter and a tested coordinate/rest-pose contract; the documentation alone does not provide that integration.

Primary sources: [NLA introduction](https://docs.blender.org/manual/en/5.3/editors/nla/introduction.html), [Bake Action API](https://docs.blender.org/api/5.3/bpy.ops.nla.html).

## 2. Treat phrase transitions as contact transitions

Record the supporting foot, root position and velocity, facing, palm orientation and prop grip at both ends of every phrase. Select compatible entry/exit states before blending. Do not let a broad crossfade pull a planted ankle or held object away from its contact. Let the lead and answer use different complete phrases rather than only a time offset.

This is an implementation recommendation based on the current scene's limits. Stable ankles are a useful measured condition, but they do not certify natural balance or professional dance. Review the plain body before adding translucent garments, then review the finished style at actual speed where playback is available.

## 3. Bake body garments once, then improve the important collisions

The new fans already use immutable disk caches. Body garments still rebuild their history in each frame worker. A shared garment cache could remove that repeated CPU cost and fund better collision treatment in the hero shots. Bind caches to skeleton, full motion, garment topology, collision surfaces, software and solver settings, just as the fan cache binds to actual hand/capsule tracks.

Next, test a silk reversal against the costume and a longer settling interval. Blender's official cloth documentation explains that self-collision adds computation, while higher simulation quality reduces step size and can catch fast collisions. Simply increasing separation distance can make fabric appear to hover. These are useful design tradeoffs whether the next solver stays native or is authored/baked externally. Do not claim that adopting Blender automatically fixes intersections.

Primary source: [Cloth collisions](https://docs.blender.org/manual/en/5.3/physics/cloth/settings/collisions.html).

## 4. Evaluate richer motion annotations with explicit provenance

Google's AIST++ page publishes its annotations under CC BY 4.0. The format includes joint poses and root trajectories, exact 60 Hz annotation timing, a temporally smoothed 17-joint keypoint option and an exclusion list for poor reconstructions. These annotations are a candidate for a separately reviewed native-rig retargeting study. They have not been downloaded, inspected or integrated here.

An annotation-only candidate would need an exact source/license record, required attribution, a selected complete phrase, native-rig retargeting, contact cleanup and authored fingers/foot roll. Use the original concert recording. The original source videos/music have their own terms, linked separately by the dataset; the annotation license does not establish rights to reuse those media or external body-model assets. Do not apply an API code license to a dataset by assumption.

Primary sources: [AIST++ description and annotation license](https://google.github.io/aistplusplus_dataset/factsfigures.html), [formats, timing and filter list](https://google.github.io/aistplusplus_dataset/download.html), [linked original media terms](https://aistdancedb.ongaaccel.jp/terms_of_use/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Order of proof

1. One complete native-body phrase, six seconds, with clear support and recovery.
2. The same phrase with fan and actual garment response, including reversal and settlement.
3. A complementary second role, with compatible contact and space.
4. The luminous treatment and camera, preserving full-body legibility.
5. Native 1080p60 review, followed by a measured 4K passage.

Render the 4K pass separately from the six-worker 1080p pass on this approximately 10 GB host. The first concurrent 4K attempt was terminated with exit -9 while memory was heavily used; the log does not establish the kernel's reason. Record the successful sequential retry and its actual memory/time before increasing concurrency. No cloud GPU provider, paid service, Mac rendering or unattended background service is configured.
