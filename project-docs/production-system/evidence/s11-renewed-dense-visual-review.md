# Incremental review of the actual encoded cloud pictures

Producing commit: `eec8d16519ea82309ef851975792e9dfc548da03`.
Request: `s11-renewed-20261123-master`, GitHub Actions run `45108198761`.

This is visual inspection of extracted encoded frames, not a claim of complete uninterrupted real-time playback, bit-identical hosted environments, or owner creative approval.

## First arrivals: parts 0, 5, 6, 7, 10

Inspected 15 story overview samples and a 12-consecutive-frame interval spanning part 6 to part 7, including both immediate boundary frames at native 1920×1080. Exact frame/time inventory is in `inventory.json`.

- Opening event/song typography is legible; the partially dissolved title at 5.867 seconds is a deliberate particle reveal rather than corrupt text.
- Church architecture, colored ribbon arcs, Earth points of light, and crown staging remain legible in the sampled compositions.
- Part 6 to 7 changes the recorded host image/kernel cohort at global frame 2887 (48.116667 seconds). No abrupt visible lighting, color, geometry, or camera change is apparent in frames 2881–2892 (48.016667–48.200000 seconds). The camera moves continuously around the Earth.
- The mean absolute 8-bit RGB change at the join is 1.969630 per channel, within the neighboring within-part range 1.360658–2.351574. The join's 99th-percentile difference is 29, against neighboring values 26–30. These measurements support continuity of this specific join; they do not establish equivalence of all frames on the two hosts.
- These sampled sections do not contain a close human figure, so this pass does not yet assess garments or conducting.

Evidence: `overview.jpg`, `join-06-07.jpg`, the two native boundary PNGs, `join-06-07-differences.json`.

## Second arrivals: parts 1, 2, 4, 11

Inspected 12 overview frames and three additional 12-frame cross-host joins: 0→1 at 6.866667 seconds, 4→5 at 34.366667 seconds, and 10→11 at 75.616667 seconds. The first and third joins show no abrupt framing/color discontinuity. The overview includes the choir at 79.05 seconds, inspected at native resolution: separate generously cut blue robes, faceless light figures and gold books read clearly, with no exposed body anatomy visible. The stage at 28.5 seconds retains blue players and identifiable gold instruments; bright instrument accents remain deliberate.

### Resolved concern: 4→5 brightness increase

The ground/star field brightens precisely at this join. It was initially held for investigation rather than automatically accepted. A wider 61-frame encoded timeline (33.866667–34.866667 seconds) and a separately rendered continuous local seven-frame reference (frames 2058–2064) resolve it as the authored musical light response:

- Prepared music map at source 34.25→34.266667 seconds: bass 0.31414→0.58078, kick 0.02051→0.77438, `fx_pulse` 0.107016→0.770061.
- `s11_music_fx.add` applies that pulse to the sea glitter, floating lights, dust and city lights.
- Local continuous-render mean RGB jump is [6.3087, 5.5410, 4.0443]; remote join jump is [6.2481, 5.4996, 4.0726]. The largest channel difference between these jumps is 0.061/255.
- Actual local reference pictures show the same exact-frame lower-field sparkle rise. This confirms authored timing/behavior, not pixel identity: the local and remote LLVM versions differ.

No seam-specific defect remains identified here. Evidence: `join-04-05-wider-timeline.json`, `join-04-05-local-comparison.json`, `join-04-05-local-comparison.jpg`; root's native reference PNGs reside in the adjacent `join-04-05-local-reference` directory.

## Third arrivals: parts 8 and 19

Inspected seven overview frames and four additional crown reading-interval frames. Native images at 131.0 and 136.5 seconds show the procession as covered, faceless light figures. They are viewed at a distance, so this pass supports only their visible modest silhouette rather than close garment construction or walking fluidity. Mother remains a source of light in these images, with no human representation apparent.

The two-line glory phrase is readable at 58.0 seconds. In the subsequent church shot, sampled native-time images at 58.6, 59.2, 59.8 and 60.0 seconds keep both lines readable; the crown's dim arcs pass behind the phrase but do not visually erase its letters. At 60.7 seconds the first line is deliberately dissolving/rising after its source reading interval ends at 60.0 seconds, matching `PHRASE_LIST` (source delay is 0.1 seconds). The hope phrase at 136.5 seconds is fully readable; its partial lettering at 134.6 seconds is its authored entrance before reading begins at source 135.19 seconds.

## Scope at pause

86 extracted encoded frames were visually inspected across parts 0, 1, 2, 4, 5, 6, 7, 8, 10, 11 and 19, including 48 consecutive-frame samples across four cross-host joins. Additional numerical evidence covers 61 frames around the questioned music pulse. The close conductor, dense motion, later 165.8-second phrase/terrace composition, all remaining joins, and final story sheets remain for subsequent review. No actual full-film playback or owner approval is asserted.

## Fourth arrivals: parts 12, 14 and 18

Inspected 76 additional actual encoded frames, with 24 consecutive frames at 98.000000–98.383333 seconds and another 24 at 124.000000–124.383333 seconds. Eight native crop frames from each motion interval were also inspected to resolve garment, hand, baton and foot details. The conductor's separate knee-length coat and trousers retain a generous silhouette. No exposed anatomy, abrupt within-shot arm pose, foot jump, or separated baton is visible in those two intervals. The right hand and baton turn together through the downward and rising gestures; the golden trace remains tied to the baton. The sampled head and shoulder motion remains consistent with the slow camera movement.

The stage phrase at 82.7–85.8 seconds stays readable over the orchestra. At 126.5–130.5 seconds the descending light and gathered figures preserve the intended light-only representation of Mother.

Cross-host join 11→12 at 82.5 seconds is visually continuous through 12 consecutive frames. Its mean absolute RGB change is 3.544/255, within the neighboring within-part range 2.558–4.310. Part 18→19 uses the same AWS fingerprint; its boundary remains included in the planned final all-join review.

Evidence is in `batch-04/`, including full/native frames, the dense motion sheets, native crop sheets, overview, join sheet, numeric join differences, and exact frame inventory. Cumulative inspected encoded-frame count at this stage: 162.

## Fifth arrivals: parts 15 and 16

Six additional story frames at 105.7, 107.8, 109.5, 111.4, 114.5 and 116.5 seconds were inspected; the 105.7-second stage image was also viewed at native resolution. The musicians' robe/trouser silhouettes and instruments remain discernible, the word “Devotion” is fully readable, and localized light accents do not obscure the phrase. The city/pillar return remains coherent through its three sampled views. Part 16 finishes before the next close conductor shot, so the close 117–123-second block remains pending arrival of part 17. Evidence is in `batch-05/`. Cumulative inspected encoded-frame count: 168.

## Sixth arrival: part 17, close conductor and former transition

Inspected 59 additional encoded frames, including 24 consecutive frames at 118.800000–119.183333 seconds, 18 consecutive frames spanning the authored 121.433333-second camera change, and 12 consecutive frames around cross-host join 16→17. Native 118.8 and 121.383333-second images resolve the front/oblique garment and baton contact.

The quiet conductor keeps a full, modest coat/trouser silhouette, with gold head/hands and no anatomical emphasis. The sampled quiet gesture and preparatory movement show no visible within-shot pose snap, foot displacement, or detached baton. The large viewpoint and lighting change at frame 7286 (121.433333 seconds) corresponds to the authored source cut at 121.32 seconds plus the picture delay. Frames before and after that cut maintain coherent figure poses within each shot; the brighter release is visible as an intentional cue.

Join 16→17 at 116.866667 seconds shows no abrupt host-seam color or geometry change. Its mean absolute RGB difference is 2.625/255, within neighboring values 2.247–3.394. Evidence is in `batch-06/` (overview, quiet-conductor, authored-camera-cut and join sheets, native images, exact inventory and numeric join differences).

Cumulative visually inspected encoded-frame count: 227. The 165.8-second phrase/terrace view and complete final story/join sheet review remain pending.

## Complete musical gesture sample: 117.1–123.1 seconds

Inspected 61 chronological native conductor crops sampled at 10 fps from the actual encoded part 17. The six sheets and exact global frame/source-time inventory are in `long-gesture-117-123/`.

The quiet interval uses small controlled baton loops and restrained upper-body shifts, with planted feet. The preparatory movement leads into the documented camera/light cue at 121.433333 seconds. After it, the right arm opens into a broader stroke, turns the baton and returns toward the torso by 123.1 seconds. No abrupt within-shot jump, detached baton, or foot slide was observed in the sampled sequence. The separate coat and trousers maintain a modest silhouette in both viewpoints. This longer view complements the consecutive-frame continuity checks; it is a chronological sample review, not real-time playback or a claim of motion capture realism.

## Later composition risk: 165.8-second joy phrase

Inspected 11 actual encoded frames from part 24 at 165.0, 165.2, 165.3, 165.5, 165.7, 165.8, 165.9, 166.1, 166.3, 166.5 and 166.7 seconds. All phrase crops were inspected at native pixel scale; 165.8 seconds was also inspected as a full native frame. “Joy of salvation!” remains readable throughout the inspected portion of its reading hold. After the authored camera change near 165.26 seconds, the terrace rings remain below the words. The church rooftop touches/slightly overlaps the lower edge of “sal,” so separation is not perfect, but no word becomes difficult to read. This is a recorded nonblocking composition observation. The earlier reading-hold portion before 165 seconds remains in part 23. Evidence and exact inventory: `phrase-165-167/`.

## Cross-host completion pass: newly available join 32→33

Inspected 12 consecutive encoded frames around global frame 13612 (226.866667 seconds), with both immediate boundary frames also viewed at native resolution. The bright blue foreground comet moves coherently to the right through the join and exits shortly afterward. Earth orientation, light paths, “Devotion” typography and background stars preserve continuous motion and color. No seam-specific defect was identified. The join mean absolute RGB change is 7.848/255, compared with neighboring within-part changes of 3.669–7.450/255; the large change corresponds to the prominent moving comet. Exact frame inventory, two cohort fingerprints, video hashes and the per-join verdict are preserved in `all-cross-host-joins/review-index.json`.

Join 34→35 at 240.616667 seconds: all 12 consecutive encoded frames were inspected. The choir/orchestra stage, church background, music trail and “Oh, the Church of God” title preserve continuous motion. The gold comet advances consistently upward-right without a seam-specific color or exposure change. Mean absolute RGB difference is 5.266/255, against neighboring values 4.489–4.996/255. Fingerprints and exact frame inventory are retained in the consolidated index.

Join 35→36 at 247.5 seconds: all 12 consecutive encoded frames were inspected. The moving choir view maintains aligned robe silhouettes, gold books and overhead pink trail. No abrupt figure, camera, color or exposure change appears at the join. The lower song signature fades progressively across later samples. Mean absolute RGB difference is 13.541/255, within neighboring values 12.445–17.938/255.

## Part 23 arrival: completing the phrase hold and two joins

Five additional native phrase crops at 163.4, 163.8, 164.2, 164.6 and 164.9 seconds complete the previously unavailable early portion of the “Joy of salvation!” reading hold. The words remain complete and legible in all five. Translucent facade lines overlap the lettering region but do not erase or disguise words. Together with the existing 11 samples, the targeted phrase composition review now spans 163.4–166.7 seconds. Exact inventory and evidence: `phrase-165-167/earlier-hold/`; the later rooftop-contact note remains in force.

Join 22→23 at 158.116667 seconds: all 12 consecutive encoded frames inspected. The city, Church of God phrase, sun, mountains and colored approach arcs preserve continuous position and exposure. Mean absolute RGB change is 2.298/255, within neighboring values 1.827–2.463/255.

Join 23→24 at 165.0 seconds: all 12 consecutive encoded frames inspected. The joy phrase and choir/orchestra view remain continuous as the camera moves past the church facade. Figure positions, blue robes, gold instruments and foreground sparkles stay coherent. Mean absolute RGB change is 2.445/255, within neighboring values 1.813–2.734/255. No unresolved seam-specific defect was identified at either boundary.

## Parts 21 and 29: three more cross-host boundaries

All 12 consecutive encoded frames at each boundary were inspected:

- 20→21 at 144.366667 seconds: continuous floating-city camera movement, central light and reflections, with foreground trails retaining stable placement and exposure. Mean absolute RGB change 3.254/255, within neighboring values 2.210–3.385/255.
- 21→22 at 151.25 seconds: “All kings worship You” finishes forming continuously; gold city and surrounding colored structures remain coherent. Mean absolute RGB change 1.948/255, within neighboring values 1.208–2.471/255.
- 29→30 at 206.25 seconds: elevated orchestra, mountain horizon, lower signature and colored trails remain continuous. The upper golden particles fade progressively on both sides rather than collapsing at the boundary. Mean absolute RGB change 4.448/255, within neighboring values 3.316–5.803/255.

No unresolved seam-specific defect was identified in these three intervals.

## Part 27 arrival: two more cross-host joins

All 12 consecutive encoded frames at each boundary were inspected. At 26→27 (185.616667 seconds), the “Wondrous” phrase continues forming and the choir/orchestra camera movement, foreground rings and lettering light remain coherent; mean absolute RGB change is 4.605/255 versus neighboring values 2.950–4.104/255. At 27→28 (192.5 seconds), the elevated city camera movement stays continuous, with central church, round light medallions, terraces and mountain horizon maintaining coherent placement; mean absolute RGB change is 11.335/255, within neighboring values 10.330–14.651/255. No unresolved seam-specific defect was identified.

## Final closure of the assigned dense cross-host and targeted review

All 40 authenticated parts are present. Comparing the actual per-part fingerprints identifies **20 cross-host boundaries** among the film’s 39 interior part boundaries. **All 20 are visually reviewed with 12 consecutive encoded frames each: 240 unique frames**, with native boundary views where a closer check was needed. The final part 31 has the same Azure fingerprint as both parts 30 and 32, so those two boundaries do not add cross-host cases. The receipt/index audit confirms exact consecutive frame ranges, timestamps, both video hashes, both full fingerprints, and all image files for every reviewed boundary. No unresolved seam-specific defect was identified. The 34.366667-second brightness concern is explicitly resolved as an authored musical pulse using immutable map data and a single-renderer neighboring reference.

The known 165.8-second phrase risk is now covered by **16 native phrase samples spanning 163.4–166.7 seconds**. All remain readable. Terrace lines stay below the words after the camera cut; the church roof touches/slightly overlaps the lower “sal” edge, recorded as a nonblocking composition observation. The **61-frame, 10 fps conductor gesture sample from 117.1–123.1 seconds** is also complete, in addition to earlier dense conductor checks. No within-shot lurch, detached baton, foot slide or exposed anatomy was observed in those sampled views.

This closes the assigned cross-host and targeted composition/motion review. It does not replace the separately assigned final broad story review, uninterrupted playback, or owner creative review. Machine-readable closure: `cross-host-review-closure.json`.

| Cross-host join | Boundary time (seconds) | Verdict |
|---|---:|---|
| 0→1 | 6.866667 | No unresolved seam-specific defect |
| 4→5 | 34.366667 | No unresolved seam-specific defect |
| 6→7 | 48.116667 | No unresolved seam-specific defect |
| 9→10 | 68.750000 | No unresolved seam-specific defect |
| 10→11 | 75.616667 | No unresolved seam-specific defect |
| 11→12 | 82.500000 | No unresolved seam-specific defect |
| 12→13 | 89.366667 | No unresolved seam-specific defect |
| 13→14 | 96.250000 | No unresolved seam-specific defect |
| 14→15 | 103.116667 | No unresolved seam-specific defect |
| 16→17 | 116.866667 | No unresolved seam-specific defect |
| 20→21 | 144.366667 | No unresolved seam-specific defect |
| 21→22 | 151.250000 | No unresolved seam-specific defect |
| 22→23 | 158.116667 | No unresolved seam-specific defect |
| 23→24 | 165.000000 | No unresolved seam-specific defect |
| 26→27 | 185.616667 | No unresolved seam-specific defect |
| 27→28 | 192.500000 | No unresolved seam-specific defect |
| 29→30 | 206.250000 | No unresolved seam-specific defect |
| 32→33 | 226.866667 | No unresolved seam-specific defect |
| 34→35 | 240.616667 | No unresolved seam-specific defect |
| 35→36 | 247.500000 | No unresolved seam-specific defect |
