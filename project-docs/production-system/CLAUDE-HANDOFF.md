# Claude handoff: the concert project

**Checkpoint: November 22, 2026, America/Los_Angeles (machine receipts use UTC).** The complete **Almighty God Knows the Future** recreation is rendered, technically checked, visually reviewed within the recorded sample scope, and saved. It is a **275-second, native 1080p60 design/review delivery**, with no unfinished render queue. The owner has **not approved this exact new film**. The final show target is **4K60 after design, timing and content approval**; this Song 11 delivery is not a rendered 4K show master.

The picture source is `eec8d16519ea82309ef851975792e9dfc548da03`. [PR #112](https://github.com/lovelaceaml-hub/concert-backdrops/pull/112) merged the completed recreation and delivery workflow at `93527bf5e2e43477073e361d22cfd6d4fa999da7`. Later documentation, transfer or maintenance commits do not change the producing picture identity. The November 22 owner directions, merged through [PR #113](https://github.com/lovelaceaml-hub/concert-backdrops/pull/113), are included in that integration checkpoint. The subsequent owner priorities in [PR #114](https://github.com/lovelaceaml-hub/concert-backdrops/pull/114) are retained from main `651e9487cd134e06b94f9627c22f008a8da02b54` and govern the next work.

[PR #116](https://github.com/lovelaceaml-hub/concert-backdrops/pull/116), merged at `3812463e1196f4c47b468e05060dbc1c8154ff75`, adds the working cloud tool-proof route, reusable song scene and Drive transfer helper. [Section 9](#9-actual-status-of-the-additional-tools) distinguishes the actual tested source/run, this local checkout's installation gaps and the remaining integration limits. These additions do not change the completed film's producing source or its approval status.

This is a continuation guide for the **whole existing concert system**, not a request to replace it or restart completed studies. Read the current conversation and [root AGENTS.md](../../AGENTS.md), then [STATE.json](STATE.json), [the delivery record](evidence/s11-renewed-final-delivery.json) and [final QA](evidence/s11-renewed-final-qa.json). The dated sections in older documents preserve history; they are not an automatically authorized work queue.

## Contents

- [1. Standing owner directions](#1-standing-owner-directions)
- [2. Creative purpose and current visual rules](#2-creative-purpose-and-current-visual-rules)
- [3. Project locations and recovery](#3-project-locations-and-recovery)
- [4. Completed Song 11: exact identity](#4-completed-song-11-exact-identity)
- [5. Source recordings and performance references](#5-source-recordings-and-performance-references)
- [6. Earlier work and approval boundaries](#6-earlier-work-and-approval-boundaries)
- [7. Where the implementation lives](#7-where-the-implementation-lives)
- [8. Bootstrap, resources and runtime pins](#8-bootstrap-resources-and-runtime-pins)
- [9. Actual status of the additional tools](#9-actual-status-of-the-additional-tools)
- [10. Repeatable production and delivery workflow](#10-repeatable-production-and-delivery-workflow)
- [11. What was actually reviewed](#11-what-was-actually-reviewed)
- [12. Future entry points](#12-future-entry-points)

## 1. Standing owner directions

[Root AGENTS.md](../../AGENTS.md) contains the latest standing directions for Claude, Codex, ChatGPT and Gemini. Its November 22 owner section takes priority over earlier navigation-only wording and dated project records.

1. **Improve the current system.** Keep the established engine, working scenes, source identities and render setup. The owner used ChatGPT to establish and improve this system, not to replace it with a separate ChatGPT system.
2. **Keep the additional tools and make them reusable.** Blender, the Three.js scene preview, Remotion, Video Shotcraft and Blender MCP remain part of the project. Preserve the successful cloud proofs and describe the remaining checks precisely; they should not be deleted or shelved.
3. **Do not create new phone versions or phone-only review files.** The existing 720p Song 11 file is a preserved historical viewing derivative. Its existence does not establish a current phone workflow.
4. **Develop at 1080p; render the final show at 3840×2160, 60 fps after approval.** Do not infer approval from a successful technical check, an earlier study's approval or a saved delivery.
5. **CPU rendering stays in the cloud. GPU work, if needed, uses Anthony's Mac.** The owner reports an Apple M1 Pro with a 16-core GPU and Metal 4. Before heavy local work, check the one-minute load and stop if it exceeds 50; run at `nice -n 19`. The generic renderer refuses macOS by default. Its explicit `--allow-local-render` option is only for authorized local GPU work; the flag does not itself select or configure Metal/GPU rendering. The Linux x64 installation is not proof of a working Mac GPU setup.
6. **Ask a short, recommended-choice clarification when the request is genuinely unclear or changes what the owner receives.** Routine recovery, inspection and implementation already authorized by the conversation can proceed.

The owner has already authorized continuing the priorities in this order: **(1)** get Blender, Three.js, Remotion, Video Shotcraft and Blender MCP working and reusable for any song; **(2)** incorporate proven quality improvements into the existing engine for every song; **(3)** organize one plain status page, stale pull requests and distributed cloud rendering. The current request is to complete this project handoff; those priorities guide Claude's continuation, with no need to ask again for routine authorized work.

For browser 3D, Remotion and live Blender failures caused by cloud sandbox restrictions, **try permitted cloud routes first**, such as a suitable GitHub Actions runner. Such restrictions are not proof of a missing GPU. Use the owner's Mac only if no cloud route works, and explain why. The separate Mac GPU and load/priority conditions still apply.

The GitHub Actions CPU route now has successful browser, Remotion and live Blender proofs. The older chat-sandbox socket restrictions remain local environment observations, not a current blanket cloud blocker.

The owner's correction about anatomical detail is a standing creative requirement. The rejected body-fitting fan direction must not reappear as the default because its code or an old queue remains in Git. [PR #111](https://github.com/lovelaceaml-hub/concert-backdrops/pull/111) is closed without merging. The completed Song 11 recreation uses separately shaped, generous garments.

## 2. Creative purpose and current visual rules

The concert's central message is **The Words of Mother's Love bring peace**. Its nine practices are greeting, gratitude, apology, inclusiveness, concession, respect, encouragement, consideration and compliment. The exact words, colors and established vocabulary belong to [the creative rules](CREATIVE-RULES.md), the catalogs and [the engine's word definitions](../../engine/p3d/words.py).

The visual language includes mirror water, mountains, a starry sky, architecture, light people and meaningful human interactions. A useful story pattern is: a person notices a need, chooses a kind action, another person responds, and the world responds. Each song should develop its own emotional world; an attractive effects loop alone does not express the concert's message.

**People must read as modest artistic figures of light.** Build independent clothing geometry with a generous silhouette. No visible nipples, breast outlines, buttock clefts or exposed cheeks. Making a body-shaped surface opaque or blue is insufficient. Apply the rule to every reused figure, including choir, orchestra, procession and distant figures, and review front, side and rear views. Put detail into costume design, musical gestures, architecture, water and light. Historical body assets and anatomy studies are source material, not automatically approved visible models.

Ordinary figures generally use warm gold. Song 11's choir and orchestra use blue, with gold books and instruments. Its male conductor leads a journey through the heavenly city, emerald Earth, Mount Zion, gathering nations and kings, and the Church of God. **Heavenly Mother is represented only by light in this song.** That song-specific rule is narrower than some older general suggestions about rear views or hands. Use the provided church architecture and exact emblem, not an invented replacement. Preserve the established logo/song/theme placement; event details belong on the ending card. Keep readable space around words and let musical light have peaks and rests.

The following world descriptions are navigation into the historical design plans, not claims that eleven upgraded full films have been delivered. Read the actual [song catalog](catalogs/songs.json) and each [song design](../designs/) before using one.

| Song | Established title | Design direction |
| --- | --- | --- |
| 01 | All You Stars of Zion | Starry night opening toward gold sunrise |
| 02 | The Rose | Winter opening into blush spring |
| 03 | I Reminisce About Your Love | Rain and lantern memory toward rose dawn |
| 04 | I'm Sorry, Please Forgive Me | Ice giving way to an apricot thaw |
| 05 | God Bless You! | A welcoming spring garden |
| 06 | Heavenly Mother Tells Us to Be Grains | Harvest and the field of grain |
| 07 | May No One Ever Feel Lonely | Twilight paths, lanterns and welcome |
| 08 | Out of Heaven, Favor From God | A royal festival night |
| 09 | Let's Save the World | A misty sea at dawn |
| 10 | Our Mother Saves the World | Quiet protective light before dawn |
| 11 | Almighty God Who Knows the Future | City, Earth, Zion and a world finale, ending in darkness |

The owner calls Song 11 **Almighty God Knows the Future**. The catalog/audio title includes **Who**. These refer to the same project, not two different songs. Its current rendering remains code-based; archived generated figure or plate assets are not default inputs to this recreation.

## 3. Project locations and recovery

| Location | Role |
| --- | --- |
| [GitHub repository](https://github.com/lovelaceaml-hub/concert-backdrops) | Public, versioned source, instructions, catalogs and evidence |
| [Main project documentation](https://github.com/lovelaceaml-hub/concert-backdrops/tree/main/project-docs) | Current documentation plus dated design and production history |
| [Concert Backdrops - Songs](https://drive.google.com/drive/folders/1xyNZn4ZA6bjPcvKjGfgSWQIs9aAp2PPd) | Shared Drive project home |
| [Production System](https://drive.google.com/drive/folders/1QDGGqqkJlbovBLCthX-QChqfD8zSmK8X) | Established shared handoff and documentation area |
| [Videos / Production Studies](https://drive.google.com/drive/folders/1hrk62bFIOHv2NwXvYl2bNSmp0cwBoXrr) | Earlier films, studies and media |
| [Claude handoff](https://drive.google.com/drive/folders/1lxcic8BcSzNgPtEY_Yg_2TBAbNam72dZ) | Current project handoff destination |
| [Claude handoff source and documentation](https://drive.google.com/drive/folders/1ARIxA-UsuIR0xEVeDIBMH-MMgoxnafHn) | Source/document snapshots and resource inventory |
| [Verified cloud-tools source checkpoint](https://drive.google.com/file/d/1NSXgPH0YSHKTEP9d2dGppXfnQNUSn919/view?usp=drivesdk) | **877 tracked entries** at `252e14145d535d8c8472c72144d85587967f3b2f`, including PR #116 and the archive transfer helper; actual source/resource restoration passed. |
| [Prior frozen source backup A](https://drive.google.com/file/d/1QrBbz-SxWWNEkGtC30BcTWuB9_N8MDd4/view?usp=drivesdk) | 861 tracked entries at `3ef80d97d2cc25d5201195bb8ced3646811200db`, before PR #116; modes and symbolic links preserved. Use the completion receipt for the latest refreshed source archive. |

Use the [Drive completion record](evidence/claude-drive-completion.json) for exact Drive file IDs, bytes, hashes and confirmed coverage. The [media inventory](catalogs/handoff-media.json) and [resource inventory](catalogs/handoff-resources.json) describe the intended originals and their provenance. Read each status: a folder's existence or a transfer plan does not prove that every intended upload is present. A source snapshot contains the tracked project at its recorded commit. A pinned-resource archive has its own inventory; it must not be described as a complete installed environment. GitHub is the history authority. A source snapshot archive or a linked partial clone is not an offline Git bundle.

### Final source after parallel owner updates

Use [FINAL-SOURCE-CHECKPOINT.md](FINAL-SOURCE-CHECKPOINT.md) and the final `FINAL-SOURCE-MANIFEST.json` / `FINAL-HANDOFF-RECEIPT.json` in the source folder for the exact final merged source. The 877-entry snapshot `252e1414` is a verified recovery checkpoint before the later PRs #117–#119. The final archive also includes the Claude cloud-session hook, opt-in shared engine quality/motion helpers, and original-source reproduction guards from those owner updates. The recorded short cloud tool proofs retain their exact tested source; they do not prove every later engine change or full-film reproduction.

### Verified handoff coverage

The reconciliation retains **40 media, reference and recovery originals**: the 29 later saved delivery artifacts, six canonical/current reference copies, two recovery artifacts and three separately identified earlier imports. All 40 have complete raw-byte verification either as a whole file or through exact, individually verified recovery parts. Twenty-two existing whole files were adopted after new full hash checks; seven large originals use verified byte parts. Six extra Cinematic movies copied before the older canonical folder was discovered remain as verified redundant copies in the recovery folder.

The two additional archives preserve **392 reproduction resource paths** and **467 visual-review evidence files**. Both were uploaded intact and fully read back. The separate **637 MB PR #116 tool-proof archive** is also retained intact in Drive. Its source ZIP hash and full Drive readback matched in [transfer run 45127784158](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45127784158); see [the retention proof](evidence/claude-cloud-proof-retention.json). This proof used the project’s authenticated cloud route because the archive exceeds the chat download limit. The existing project scan listed **62 folders and 542 metadata objects**, with four new active handoff/recovery subtrees intentionally excluded; it is a locator index, not a claim that every older object was downloaded. All 31 previously recorded Drive objects had matching sizes, and 29 had unchanged recorded modification times. Eleven reported historical full-film targets remain unresolved; a different complete-length Song 03 alternate was recovered and is separately identified.

| Need | Current destination |
| --- | --- |
| Full-HD Song 11 movie already present in Drive | [Direct MP4](https://drive.google.com/file/d/1Zgt8q8--0lro5_6_pavdsREi7bGrh8X8/view?usp=drivesdk) — title/size/parent checked; raw readback exceeds the connection limit |
| Verified exact Song 11 delivery/master recovery | [Song 11 recovery folder](https://drive.google.com/drive/folders/1Lcu1I78xzy65svx0-wCJq5wmD9OGFEqu) — all 19 parts plus manifest, helper and instructions |
| Earlier Cinematic Ten whole films/support | [Canonical Cinematic Ten folder](https://drive.google.com/drive/folders/1gxMbTORCUZNXAAa-Gg7_T8scfKXELMkf) |
| Exact Cinematic Ten package recovery | [Verified Cinematic Ten recovery](https://drive.google.com/drive/folders/1Hi6YobO_2dXIbod0-3BPoZXlSq22rRB6) |
| Advanced Dance whole films/support and maintenance | [Canonical Advanced Dance folder](https://drive.google.com/drive/folders/1CbjaFW1_zewZ4IWrzvM4GpsOFM_XEQTj) |
| Exact Advanced Dance package recovery | [Verified Advanced Dance recovery](https://drive.google.com/drive/folders/1e0j_89WwvQSlhmGqTQDnsBaRyxQwInh7) |
| Exact reproduction assets and prepared score | [Resource archive](https://drive.google.com/file/d/1zLhcmJRo_ZH4Kd4lO0MtyHEV2McLSWux/view?usp=drivesdk) |
| Preserved visual-review evidence | [Review archive](https://drive.google.com/file/d/18AqvLakHwJzmWrFQAfZXmyL9ksQ0_-P2/view?usp=drivesdk) |
| Exact cloud tool proof archive | [Cloud_Tool_Proofs_PR116_2026-11-22.zip](https://drive.google.com/file/d/1IW2BxB1qKPpz-4nrIfD3KSV7H9p6CmdB/view?usp=drivesdk) — 637,361,486 original bytes; full authenticated cloud Drive readback verified |
| All nine distinct reference imports/copies | [Reference Media](https://drive.google.com/drive/folders/1ihTYIdC8ssma9QZ1-OLXn3fRU6K6jaCZ) |
| Recovery cache and separate private render-key archive | [Private Recovery](https://drive.google.com/drive/folders/1aVv7mbC7Tam_GahdpgFGJMZpzvxPowQ-) |

Five additional large whole-file Drive copies have matching metadata only because the raw fetch route rejects files above 268,435,456 bytes. Their expected original hashes must not be represented as hashes proved from those objects. The independently uploaded and fully read-back parts are the verified content authority. Existing sharing was retained; receipt-level observations describe actual permissions without a blanket owner-only claim. No permission changes were made.

Use [the plain status page](PROJECT-STATUS.md), [the complete Drive locator index](catalogs/drive-project-index.json), and [the ready-to-paste Claude prompt](CLAUDE-START-PROMPT.txt). The original source backup A contains commit `3ef80d97d2cc25d5201195bb8ced3646811200db` and 861 tracked entries; it predates PR #116. Its actual extraction and restoration of all 392 resource paths passed. Follow the current [source archive receipt](evidence/claude-source-snapshot.json), [clean restoration proof](evidence/claude-source-clean-restore.json) and [completion record](evidence/claude-drive-completion.json) for the refreshed snapshot's exact identity and verification; do not infer that the older backup includes later cloud-tool changes. The initial handoff checkpoint merged through [PR #115](https://github.com/lovelaceaml-hub/concert-backdrops/pull/115); the current closeout preserves that merge and [PR #116](https://github.com/lovelaceaml-hub/concert-backdrops/pull/116). The [publication record](evidence/claude-publication.json) identifies the final uploaded documentation and source.


The [delivery catalog](catalogs/deliveries.json), [DELIVERIES.md](DELIVERIES.md), [STATE.json](STATE.json) and individual evidence records describe saved files. Recover the finished asset before considering another render. An absent ignored `work/` directory in a fresh checkout is not pending production. Old absolute workspace paths document where a check happened; they are not portable dependencies.

### Recover large Drive files without changing their bytes

The upload connector enforces a 104,857,600-byte per-file limit. Larger original files are transferred in **90,000,000-byte parts**, with a final shorter part, a `TRANSFER-MANIFEST.json` and the portable [restore_handoff.py](../../tools/handoff/restore_handoff.py) helper in the same Drive folder. Smaller files are transferred whole. Download every required part and the support files together, then run:

```bash
python3 restore_handoff.py
```

To restore one selected original, use `python3 restore_handoff.py --only "exact-original-filename"`. The helper verifies every part and the complete original SHA-256, skips an existing matching output and refuses to overwrite a differing file. It performs no encoding and needs no network connection. This is a byte-preserving transfer format, not a new rendition or phone version.

### Recover the exact current Song 11 master offline

Recover both ordinary ZIPs in the next section. If using the current Drive byte-part transfer, first run `restore_handoff.py` to reconstruct each original ZIP. Then keep both ZIPs together, extract `restore_master.py` from either, and run:

```bash
python3 restore_master.py --archive-dir .
```

The included standard-library script verifies each chunk and the whole movie and refuses to overwrite an existing output. It needs no renderer, GPU, Node or third-party Python package. The [archive receipt](evidence/s11-renewed-master-archive.json) records successful byte-for-byte restoration. Keep both ZIPs intact.

Full source recordings, prepared WAV audio, private recovery keys, decrypted picture parts and final movies do not belong in the public Git repository. They are separate owner-controlled resources. `work/`, `.tools/`, `.venv/`, generated fonts and `node_modules` are not recovered merely by cloning source.

## 4. Completed Song 11: exact identity

The complete film has **16,500 real frames at 1920×1080, 60 fps, with two temporal samples**, lasting 275 seconds. It has no AI frame interpolation or resolution upscale. Forty picture parts were rendered; the plan plus all forty jobs succeeded, with zero failures and zero retries, in [run 45108198761](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45108198761). Request ID: `s11-renewed-20261123-master`.

The original recording supplies source seconds 0–260. Preparation retains the established final 0.05-second fade and adds a 15-second silent hold. The picture delay is applied **once**: scene/source time is `max(0, output_video_time - 0.1)`. Audio is not time-stretched. Final audio uses only 1 dB attenuation, encoded directly from the unchanged prepared score. All 16,500 compressed video payloads, timestamps, durations and sizes match the visually reviewed pre-headroom assembly exactly. See [audio finalization](evidence/s11-renewed-audio-finalization.json) and [final QA](evidence/s11-renewed-final-qa.json).

| Saved file | Role and bytes | SHA-256 |
| --- | --- | --- |
| `Almighty_God_Knows_the_Future_Renewed_1080p60_final.mp4` | Original native master; recover from the two ZIPs; **911,865,528** | `c553b2a51f3917d389adc51ee6dc97c96e6b6e9e306a9bfd2bfbe38a89b34c55` |
| [Almighty_God_Knows_the_Future_Renewed_1080p60_delivery.mp4](https://chatgpt.com/library?file_id=libfile_40082ab3a2ec8191a7e32eac89a1aa59&account_id=personal) | Complete bounded-bitrate HD encode; same dimensions, no resize; **395,506,771** | `120bb4fcf4ebced490f4f468dca396170b328fd0ece3941e67e832258f5f449e` |
| [Almighty_God_Knows_the_Future_Renewed_720p60_final.mp4](https://chatgpt.com/library?file_id=libfile_d6b4552450348191adcddea6a16d340d&account_id=personal) | Existing complete downscaled viewing derivative; **220,179,614**; preserve, do not establish new phone output | `9cba8118b8fdf7c9410e5b10362ba15ee28a4668f95aceca911cee95a0848880` |
| [Almighty_God_Knows_the_Future_Native_Master_Part_01_of_02.zip](https://chatgpt.com/library?file_id=libfile_d45ece0bb38c81918be0e85866f53ab9&account_id=personal) | Exact master archive 1 of 2; **480,006,941** | `ffc3ca5352abbfe2e870ad740ace9ea4c97bf164c3c4b51b932849a4ff49d91c` |
| [Almighty_God_Knows_the_Future_Native_Master_Part_02_of_02.zip](https://chatgpt.com/library?file_id=libfile_197a9f5bb6508191b2a926f0e45a47d2&account_id=personal) | Exact master archive 2 of 2; **431,872,469** | `c4285f489fbadec9489037f50c6cab54ab839c3d1545c22dc822a0fd095284a9` |

The above are the existing saved recovery links. The handoff transfer inventory supplies the corresponding confirmed Drive copies. The native master is the highest-quality retained picture; the HD encode has a different compressed-picture identity despite retaining native dimensions. Both smaller movies preserve the finalized audio. The [final delivery receipt](evidence/s11-renewed-final-delivery.json) is the exact file authority.

The recreation retains the original story while changing twenty-four selected camera compositions, continuous conducting, final-hand prop attachment, separate modest clothing, waterways and controlled musical light. It preserves `tools/s11_full2` as the baseline and implements its new treatment in `tools/s11_renewed`. The old scene/edit transition at 74.56 seconds was corrected together to 74.70 seconds. See [the recreation record](S11-RECREATION.md), [validation](S11-RECREATION-VALIDATION.md) and [scene workflow](../../tools/s11_renewed/README.md).

## 5. Source recordings and performance references

### Song 11 inputs

| Input | Verified identity or role |
| --- | --- |
| [Original Song 11 recording](https://drive.google.com/file/d/108zDtdB4X189DOwsZn-K9p548nERubLG/view) | Drive ID `108zDtdB4X189DOwsZn-K9p548nERubLG`; 9,073,677 bytes; SHA-256 `70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004` |
| Local recording location | Catalog path `work/song-sources/s11.mp3`; renewed preparation default `work/song-inputs/s11-original.mp3`. Supply the same verified bytes or use `--audio` with the catalog path. |
| Prepared score | `work/s11_full2/score.wav`; 275 seconds; 48 kHz stereo PCM24; 79,200,102 bytes; SHA-256 `fa488e4805cdc43b1f0f38915d67044ef92a9e659a59ac916d4b75b4cbb6d29b` |
| Public derived maps | `tools/s11_cloud/inputs/features.npz` and `music_fx.npz`, respectively 471,549 and 574,386 bytes; manifests bind them to the recording and source. They contain analysis estimates, not waveform audio. |
| Private cloud recovery | [Recovery locator record](evidence/s11-cloud-recovery.json); the owner-controlled bundle preserves the decryption material. Do not place its key in Git, a public source archive or logs. |

The original decoded recording is longer than 260 seconds; the declared film trim is intentional. Do not replace it with duration inferred from a file title or silently extend the music. Musical level, band and onset estimates are not isolated instrument stems.

[The song catalog](catalogs/songs.json) records verified full reference recordings for **all eleven songs**. No live rehearsal recording has been verified. Earlier silent promo placeholders for Songs 02 and 10 do not supersede the recovered full recordings. Verify a song's exact Drive ID, byte count and hash before deriving a new score or edit map.

Audio coverage is distinct from historical rendered-movie coverage. At the handoff inventory stage, the ten earlier full-song movies and the older full Song 11 draft remained location gaps requiring the recorded inventory's final disposition. The prior full Song 11 movie was not independently recovered and compared for this recreation. The recreation used the existing procedural source, verified recording and approved thirty-second study; do not claim a direct comparison with an unavailable full old movie.

### Actual supplied moving references

Three screen recordings were recovered and sampled in the Cinematic Ten work: `ScreenRecording_11-21-2026 12-19-51_1.mp4` (close solo fan performance), `ScreenRecording_11-21-2026 12-20-32_1.mp4` (wider fan ensemble) and `ScreenRecording_11-21-2026 12-24-09_1.mp4` (illuminated globe, an effects reference). Their hashes and saved identities belong to [the motion catalog](catalogs/motions.json) and [Cinematic Ten motion record](CINEMATIC-TEN-MOTION.md).

The earlier [performance-reference intake](catalogs/performance-references.json) describes poster-only access to three YouTube references at that stage. Preserve that source-specific history. Do not assume the later screen recordings were proven to map to those exact URLs. The fan trio was an original adaptation, not reconstruction of an inaccessible performance; later authored curves and IK likewise are not newly captured choreography or recovered hidden feet/fingers.

[The motion library](MOTION-LIBRARY.md) catalogs prepared capture clips and limitations. The natural dance study reused CMU 05_02 at a 0.6-second offset between performers; its prepared 30 Hz capture is interpolated at render time. Other existing gait work includes CMU 35_01. Hands and fingers require authored behavior. Do not describe the generic Blender retarget bridge or numerical contact residuals as proof of production-quality human acting.

## 6. Earlier work and approval boundaries

These are completed or historical assets, not a queue to resume. Exact downloads and hashes belong to [DELIVERIES.md](DELIVERIES.md), [the delivery catalog](catalogs/deliveries.json) and the linked module records.

| Work | Actual status and reuse boundary |
| --- | --- |
| Nine Colours revision 3 | Approved 66-second creative reference, source `46df53b98a43f58e51a78d40ee5794108a68e13c`. A later native 4K60/10-bit quality export exists; approval of that exact export is not recorded. Its 4K status is not Song 11's status. |
| Song 11 beauty study | Approved 30-second, 1,800-frame 1080p60 study; SHA-256 `6e4533c4527dfb81c750f8ba907e86392f0c87dca638c3daac768ece8edae82a`. Its frozen picture source is `a7d68836c4fdc7156bbc9b839380cd65180ca2bb`; its delivery/source record also retains `23c9307608291a99702d687933c8d2092d1fd01d`. Approval does not transfer automatically to the new full film. |
| Consideration | Completed 18-second baseline and 15-second response/camera revision. These are expressive action studies, not a completed full Song 07. |
| Natural Dance, PR #104 | Completed and saved 18-second native 1080p60 study; source `0c42f4422a6b67464cb9cd84aac32008d45d4f4c`. One native 4K still exists. A full 4K configuration was not rendered and is not a live queue. Exact-film owner approval is unrecorded. |
| Fan and Silk Trio, PR #106 | Completed and saved 20-second study; source `dffe8f165944c627ae39a8bb7d47bc5a9e703305`. Historical authored fan/cloth work, with one 4K still. Apply current modesty before reuse; it is not the current default direction. |
| Cinematic Ten, PR #108 | Ten completed 20-second 1080p60 films, 200 seconds total; source `df4fc478116d3f0e34a85d2166097fbda55911bf`. Saved, technically checked and sampled visually. Exact-output owner approval is unrecorded. |
| Advanced Dance, PR #109 | Two revised 32-second films plus the unchanged earlier films 03–10; completed ten-film package, 224 seconds total. Picture source `254414bc0356171f7d5ad89361c75d45fd01a407`; merge `5a602349f90f50d79968bab77dd08db1a20c4339`. PR #110 is later maintenance, not new rendered pictures. Exact-output owner approval is unrecorded. |
| Flow of Light, PR #111 | Rejected direction, closed unmerged. Do not resurrect it or promote its body-fitting models to the baseline. |
| Renewed full Song 11, PR #112 | Completed 275-second 1080p60 design/review delivery described here; source `eec8d16519ea82309ef851975792e9dfc548da03`. No exact-output owner approval, no completed 4K show master. |

Historical review records often contain stage-specific limitations or then-pending checks. Preserve their dates and identities. A later completion record resolves the stage; rewriting an old receipt to pretend it always passed would destroy useful provenance.

## 7. Where the implementation lives

| Path | Responsibility |
| --- | --- |
| [engine/p3d](../../engine/p3d/) | Established luminous rendering, people, words and shared assets |
| [tools/s11_full2](../../tools/s11_full2/) | Original full-song world, phrases, stage, Zion, procession, coda, cards and musical maps |
| [tools/s11_renewed](../../tools/s11_renewed/) | `cinematography.py`: new selected paths; `performance.py`: continuous conductor and final-pose attachments; `garment.py`: independent clothing; `scene.py`: composition/water/light; `prepare.py` and `render.py`: verified clock and restartable native output |
| [tools/s11_cloud](../../tools/s11_cloud/) | Frozen requests, source/input validation, silent distributed rendering and encrypted transport |
| [tools/s11_delivery](../../tools/s11_delivery/) | Reviewed one-run assembly, audio headroom, complete technical checks, story extraction and exact master archives |
| [pipeline](../../pipeline/) and [scripts/video](../../scripts/video) | Shared project contracts, renderer adapters, preview/finishing/QA and archive workflow |
| [pipeline/kit.py](../../pipeline/kit.py), [song_scene.py](../../scenes/p3d/song_scene.py) and [song-scene-demo](../../projects/song-scene-demo/project.json) | Configurable scene entry point for existing `engine/songs` modules, with frame recovery, worker chunks, temporal samples and QA; see [reusable-scene instructions](../../docs/VIDEO-PIPELINE.md#reusable-scenes-for-any-song-november-22-2026) |
| [tools/drive_sync.py](../../tools/drive_sync.py) and [tool-proofs workflow](../../.github/workflows/tool-proofs.yml) | Owner-authorized cloud Drive list/get/put operations and scoped CPU runtime proofs; credentials remain Actions secrets |
| [tools/production_system.py](../../tools/production_system.py) and [scripts/concert](../../scripts/concert) | Catalog navigation, audio checks, planning, recovery and handoff export |
| [projects](../../projects/) | Registered concert studies and technical demos; dedicated renewed Song 11 modules are a separate entry point |
| [apps](../../apps/), [scenes/blender](../../scenes/blender/), [integrations](../../integrations/) | Three.js preview, Remotion editor, Blender scene work, Shotcraft and Blender MCP integration |
| [Catalogs](catalogs/) and [evidence](evidence/) | Asset, motion, recording and delivery identities; scoped production and verification receipts |

The `concert_kit`, `concert_addons`, `concert_motion_revision`, `concert_dance`, `concert_fan`, `cinematic_ten` and `advanced_dance` tools preserve earlier reusable work. Read each module's status and provenance before reuse. The generic `concert plan` command is a planning aid; its older registration assumptions do not discover or supersede every completed dedicated scene. The [original full Song 11 design record](../backdrops/s11-full2/DESIGN.md) supplies historical decisions; current validation resolves fixes made later.

## 8. Bootstrap, resources and runtime pins

### Recover source and establish a cloud CPU environment

Start from a full-history clone when reproduction needs historical engine pins:

```bash
git clone https://github.com/lovelaceaml-hub/concert-backdrops.git
cd concert-backdrops
python3 scripts/bootstrap.py --p3d-only --reference-fonts
./scripts/video doctor --backend p3d
./scripts/concert status
./scripts/concert verify-catalogs
```

The final integrated source backup is `Concert_Project_Final_Handoff_2026-11-22.tar.gz`,
a complete tracked-source snapshot at its recorded frozen commit. Extract from the directory containing the downloaded archive, then enter its
source root before using relative project commands:

```bash
tar -xzf Concert_Project_Final_Handoff_2026-11-22.tar.gz
cd concert-backdrops
```

Its top-level folder is `concert-backdrops/`. The tar format preserves executable modes and the two
tracked relative Shotcraft symbolic links. It deliberately contains no `.git`
history, environments, private key or movie payloads. Use its companion source
manifest and receipt for the exact commit, tree, archive hash and file modes;
the later closeout receipt on GitHub and Drive records the exported archive.

**Claude Code cloud sessions.** Start a cloud session on the GitHub repository `lovelaceaml-hub/concert-backdrops` (not the Drive folder, which is not a Git checkout). The repository's `.claude/settings.json` runs `scripts/cloud-session-setup.sh` at session start, only in cloud sessions: it installs FFmpeg/EGL and uv when missing, then runs the p3d-only bootstrap with reference fonts, and never renders. It never blocks the session; read `work/cloud-setup.log` for the outcome and rerun the script by hand if it did not finish. The hook runs only when the session starts inside the repository; a session that starts one folder above it (several repositories attached) must run `bash scripts/cloud-session-setup.sh` by hand from the repository. Since November 23 the script also installs the EGL libraries when FFmpeg is already present and retries when the package mirror times out. The cloud environment needs network access for package registries. Paste [CLAUDE-START-PROMPT.txt](CLAUDE-START-PROMPT.txt) as the first message.

These are setup/status commands, not a request to rerender Song 11. The standard setup uses [pyproject.toml](../../pyproject.toml), [uv.lock](../../uv.lock) and [package-lock.json](../../package-lock.json). The p3d-only route still needs Node/npm for locked font installation. General supported ranges are Python 3.11–3.13 and Node 22.12–24; the recorded project setup used Python 3.12.14, Node 24.22.3, npm 11.19.1 and uv 0.13.9. Required system capabilities include FFmpeg/FFprobe and software EGL/Mesa.

For the full tool setup, use `python3 scripts/bootstrap.py`, then `python3 scripts/install-integrations.py --check` and `./scripts/video doctor --probe-browser` on a suitable cloud CPU host. The [tool-proofs workflow](../../.github/workflows/tool-proofs.yml) provides the verified GitHub Actions route and runs actual capture/render/live-connection checks after setup. Read its per-tool outcomes, not only the overall job conclusion: individual proof steps use `continue-on-error`. Successful install or build output alone does not verify actual browser capture, MP4 export or live MCP operation. Network-dependent dependency downloads are not an offline bootstrap; use the resource inventory and cached packages when available.

### Exact renewed Song 11 runtime

Use [requirements-render.txt](../../tools/s11_renewed/requirements-render.txt) and the producing receipt for faithful reproduction, not an arbitrary newly resolved Python environment. An isolated environment may live under ignored `work/`:

```bash
python3.12 -m venv work/s11-runtime
work/s11-runtime/bin/python -m pip install --requirement tools/s11_renewed/requirements-render.txt
source work/s11-runtime/bin/activate
```

Check that the interpreter patch version is **3.12.14** when matching the recorded run. The fully pinned requirements include NumPy, SciPy, ModernGL/glcontext, librosa, Pillow, fontTools, Numba/llvmlite and soundfile. The generic environment lock and this dedicated render contract have different roles.

| Dependency or control | Recorded full cloud run |
| --- | --- |
| Host | Ubuntu 24.04, x86_64, glibc 2.39 |
| Python | 3.12.14 |
| FFmpeg | 6.1.1-3ubuntu5 |
| Mesa | 25.2.8-0ubuntu0.24.04.5 |
| Renderer | llvmpipe, LLVM 20.1.2, 256 bits |
| OpenSSL | 3.0.13 |
| Thread controls | `LP_NUM_THREADS=2`; `OPENBLAS_NUM_THREADS=1`; `OMP_NUM_THREADS=1`; `NUMBA_NUM_THREADS=1` |
| Other controls | `PYTHONHASHSEED=0`; `LIBGL_ALWAYS_SOFTWARE=1` |
| Native picture contract | 1920×1080, 60 fps, two temporal samples, CRF 14, H.264 `yuv420p`, limited-range Rec.709 |

The development/delivery host used a different FFmpeg/Mesa/LLVM environment, including FFmpeg 7.1.5 and LLVM 19.1.7. Do not claim cross-machine pixel equality or mix local fallback chunks into the cloud master. Blender's RGB16/AgX path is a different color/render contract from legacy p3d RGB8 display-gamma output. A verified 10-bit SDR encode does not imply HDR.

### Frozen assets, fonts and engine history

The [verified reproduction archive](https://drive.google.com/file/d/1zLhcmJRo_ZH4Kd4lO0MtyHEV2McLSWux/view?usp=drivesdk)
preserves the two pinned engine/assets trees, all 74 exact fonts, and the prepared
Song 11 score, feature arrays and provenance. It restores 392 paths from 271
deduplicated payloads. A real installation into an initially empty resource
layout passed every file hash, the medley copy and both relative font links.
See [the clean restoration proof](evidence/claude-resource-clean-restore.json).

For an extracted source snapshot, get the installer from the **resource ZIP**
using Python 3.11 or later. Run the following commands from the directory
containing that resource ZIP, and use the explicit archive filename below. The package was renamed to
the owner's local date without changing its bytes; its embedded default name
still uses the UTC creation date.

```bash
python3 -m zipfile -e Concert_Reproduction_Resources_2026-11-22.zip handoff-resources
python3 handoff-resources/restore_resources.py \
  --archive Concert_Reproduction_Resources_2026-11-22.zip \
  --project /path/to/concert-backdrops
```

Replace `/path/to/concert-backdrops` with the actual extracted source root.
This installs exact resources; it does not install Python/Node/Blender
dependencies, start services, render a movie or create Git history. The older
reviewed cloud assembler still requires the producing Git commit for its
`git show` checks. Clone or fetch that history when that assembly route is
needed. Restoring the finished movie from its archives needs no Git history.

`python -m tools.s11_cloud.prepare --fonts` restores the pinned engines, exact reference fonts and checked derived maps for silent picture rendering. It does not fetch or publish the original audio. Historical engines are restored from Git commits `d928ff9eafe02ac3150f0c646bdcc497fe5a7278` and `f43f4514e4bc42dc25166e90160d98219f5a0db4` into `work/nine_colours_minor/render1` and `work/nine_colours_revision3/claude-final` respectively. A history-free source snapshot archive alone cannot satisfy `git archive` of those commits.

The [font catalog](catalogs/study-fonts.json) and [font recovery guide](../../docs/REFERENCE-FONTS.md) preserve 74 historical TTF identities from Fontsource Cormorant Garamond, Jost and Outfit 5.3.0, including fixed metadata and hashes. Use the pinned conversion/recovery process; do not silently regenerate or substitute fonts during a frozen run. Earth, church, emblem, model and analysis identities are likewise part of the picture manifest. A new source or resource hash invalidates old rendered chunks.

## 9. Actual status of the additional tools

### Verified cloud CPU route

PR #116 is integrated at `3812463e1196f4c47b468e05060dbc1c8154ff75`. The completed [proof run 45125796332](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45125796332) tested the exact PR head `285df02e51cc68073fe17c8a06ae0d7f54737df7` on Ubuntu 24.04 GitHub runners and completed successfully at 06:47:47 UTC on November 23, 2026. All three jobs succeeded, and the actual summary records all eight tool outcomes as success: setup, browser doctor, Three.js capture, preview, Remotion, Blender rendering, reusable song scene and Blender MCP. These are scoped runtime proofs; do not silently attribute them to every later commit or every song.

| Component | Current verified scope | Remaining limit |
| --- | --- | --- |
| Existing p3d + FFmpeg | The full renewed Song 11 production completed through this route. | Recreate the recorded environment and inputs before deliberate reproduction. |
| Blender 5.2.4 LTS CPU | Background demo encoded and passed QA: 2 seconds, 60 frames, 320×180/30 fps. | A short engineering demonstration, not a full Blender concert, finished actor library or full 4K production. |
| Three.js 0.187.0 / React Three Fiber 9.8.2 / React 19.2.7 | Actual SwiftShader WebGL2 animated capture and out-of-order frame checks passed; pipeline preview encoded 4 seconds, 120 frames, 320×180/30 fps with passing QA. | The demonstrated scene does not establish correctness of every future scene or hardware environment. |
| Remotion 4.0.484 | Actual browser-driven assembly encoded the 4-second, 120-frame, 320×180/30 fps demo with passing QA. Silent projects contain zero audio streams. | Editor assembly proof. Workbench export through Remotion was proved separately (Video Shotcraft row). |
| Video Shotcraft | Exact pin `075b548c2405a07b77129eb448b0b504fc60dea3`; installation/build checks and retained historical 150-card, HTTP and lifecycle checks. | November 23 Claude Code cloud session: after fixing an import fault that stopped the Workbench page from opening, `scripts/prove-workbench.mjs` showed playback advancing and the Workbench's Render button producing a 180-frame 1280x720 MP4. Demo cards are not approved concert assets. |
| Blender MCP 2.3.1 | Stdio and live GUI under Xvfb passed; the live response identified `PIPELINE_MCP_CONNECTED 5.2.4 LTS`. The retained configuration uses safe mode, localhost-only access and disabled external generation integrations/telemetry. | A working cloud connection does not automatically activate an assistant's MCP client or install this local checkout. |
| Reusable `p3d-kit` song scene | A 4-second Song 11 example encoded at 1080p60: 240 frames, passing QA. | New reusable API proof, not a migration of all songs or the dedicated renewed Song 11 modules. |
| CPU Docker recipe | The separate cloud job built the CPU image successfully. | No container-run production proof is established by that build. |
| Drive helper | The separate cloud job read the project folder and created then removed its unique test file. | This access check is not a byte-verification receipt for future uploaded movies. |
| Mac GPU | The owner explicitly permits this path when GPU is needed. | No production Mac/Metal validation is established by these Linux records. No active cloud GPU provider is configured. |

The tool-proof runner used Python **3.12.16**, Blender **5.2.4 LTS**, Node **24.22.3** and FFmpeg **6.1.1**. This newer runtime does not replace the completed Song 11 picture contract, which used Python **3.12.14** and its recorded source/dependency/host fingerprints. All four demo QA reports mark creative approval as `not_assessed` and contain no audio stream. These cloud proofs do not establish all-song quality, a full concert render, a completed character/church asset library or approved 4K production. The November 19–20 checks remain dated history, including separate native 1080p frames, one 4K RGB16 frame and motion/cache studies; they do not enlarge the new demo scope.

The workflow is **Video tool proofs (cloud CPU)**, manually dispatched or triggered on `claude/video-tools-*` branch pushes. Its `tool-proofs` artifact includes per-tool logs and `proofs/summary.txt`; artifacts are retained for fourteen days. See [video-pipeline validation](../../docs/VIDEO-PIPELINE-VALIDATION.md), [integration status](../../integrations/STATUS.md), [4K and motion validation](../../docs/4K-MOTION-VALIDATION.md) and [the toolchain lock](../../infra/toolchain.lock.json). The working GitHub route does not bypass the older chat workspace's socket restrictions.

### This local handoff checkout

The resource audit found no local `node_modules`, pinned `.tools/video-shotcraft` checkout or isolated Blender MCP environment/profile. The two tracked Shotcraft skill symlinks are present but dangling because their `../../.tools/video-shotcraft` target is absent; preserve them during source extraction. Host Blender 4.3.2 differs from the project's 5.2.4 LTS pin. These are **local installation gaps**, not failures of the verified GitHub runner route. Restore the intended versions before using this host; source/configuration presence alone is not an installed runtime.

### Reuse scenes and move source/render files

[The reusable-scene contract](../../docs/VIDEO-PIPELINE.md#reusable-scenes-for-any-song-november-22-2026) accepts a module declaring `FPS`, `DURATION` (or `None` for project-defined length), `make_renderer()` and `frame()`, with optional `configure(params)`. [The kit adapter](../../pipeline/kit.py) supplies frame recovery, worker chunks, temporal samples and QA. Existing approved registrations remain frozen and reject parameters. [The new song scene](../../scenes/p3d/song_scene.py) selects an `engine/songs` module; the [example project](../../projects/song-scene-demo/project.json) supplies song, audio/feature input, start time, bloom scale and grain options. Keep new work at 1080p and review each song's modesty, motion and story. Selecting a legacy song does not automatically import the renewed Song 11 garment/performance treatment.

[`tools/drive_sync.py`](../../tools/drive_sync.py) provides `list`, `get`, `put` and an access `check` inside the existing Concert Backdrops - Songs tree. Cloud jobs use the Actions secret **`GOOGLE_DRIVE_OAUTH`**; **`GOOGLE_DRIVE_SA_KEY`** is the documented read-only fallback. Store no credential values in source, logs or handoff files. Full recordings remain in Drive; `get` retrieves the chosen source, whose bytes must still match the song catalog. `put` updates an existing same-name file in the selected folder or creates one, so select its destination and filename deliberately and preserve verification receipts. This helper supplements the exact handoff inventories; it does not replace their hashes or imply publication approval.

Use the recorded cloud proof as the starting point rather than restarting successful demos without a changed requirement. `node scripts/launch-workbench.mjs --check` is a setup check; it does not itself establish interactive playback/export. Those remaining Workbench checks and integration of reviewed improvements across songs are continuation work, not unfinished Song 11 render jobs.

## 10. Repeatable production and delivery workflow

### A. Choose the actual task and protect the reference

Recover the existing delivery for feedback or reuse. For an authorized new revision, identify its song, source recording, exact starting commit and intended change. Keep the approved references and previous completed film under their original hashes. For reproduction, use the original producing source and manifests; for a creative change, assign a new identity. Do not label new HEAD as the source of old pictures.

Read the song's current design, timing map and recording provenance. Design the action, camera and costume together at 1080p. Review whole gestures across preparation, action and settling, not just an attractive pose or spin. Check foot support, weight transfer, ensemble variation, final-hand prop contact, garment coverage, word readability and light recovery. A small contact residual or a smooth spline is useful evidence but does not prove graceful human performance.

### B. Prepare verified music and inspect native proof frames

With the dedicated environment active and the original recording recovered:

```bash
python -m tools.s11_renewed.prepare --audio work/song-inputs/s11-original.mp3
```

This verifies the recording and prepares the existing score/maps. The renderer's `--stills` values are absolute output-video seconds; `--start` and `--end` are absolute frame indices. The scene applies its 0.1-second delay internally. `--baseline` is an explicit comparison with the older beauty treatment. See [the scene README](../../tools/s11_renewed/README.md) for complete composition and deliberate local-Linux render commands. Local fallback is inactive; no fallback frames entered the delivered master.

### C. Freeze before cloud rendering

Use [the cloud workflow guide](../../tools/s11_cloud/README.md). A new `tools.s11_cloud.freeze --id NEW_UNIQUE_ID --mode probe` invocation verifies the local original score, records source/asset/font/input hashes and stages a request. It makes no Git commit or network mutation. Preserve the private recovery key before a new launch. A request-file push to the explicitly configured branch starts the workflow; an ordinary documentation push does not.

The existing workflow is [.github/workflows/s11-renewed-private-pictures.yml](../../.github/workflows/s11-renewed-private-pictures.yml), configured for `creative/s11-renewed-20261122` and changes to `tools/s11_cloud/request.json`. Inspect that trigger before a future launch; do not expect a new arbitrary branch or a `main` documentation update to render. Use a real unique lowercase request ID accepted by the tool, not the placeholder above. Inspect the native remote probe at 58, 105.7, 118.8, 186 and 205 seconds before freezing a new full render request.

The completed full run used forty contiguous parts, at most twenty parallel jobs, one render process per runner and the thread controls above. Its initial probe used one Mesa thread, so that probe has a distinct runtime identity. Do not edit picture source, fonts, analysis or assets while a request is rendering. Resume only chunks whose source, runtime, settings, ranges and file hashes still match.

Public workers receive the checked analysis maps and scene source, not the MP3 or prepared WAV. Artifacts use CMS AES-256-GCM with RSA-OAEP SHA256 key transport. The tracked recipient certificate is public; the private key stays under owner-controlled ignored storage. The workflow has read-only repository permissions, no persistent Actions cache and one-day artifact retention. Download/authenticate artifacts promptly and preserve durable recovery independently; an Actions artifact link is not permanent storage.

### D. Assemble using the correct runtime policy

The default `tools.s11_cloud.assemble` route rejects mixed request/runtime fingerprints and validates authenticated content, inventories, source hashes, native stream settings and contiguous frame ranges. It adds the verified local score once. Do not bypass a rejection by editing a receipt, dropping host metadata or mixing local and remote chunks.

For **only** producing commit `eec8d16519ea82309ef851975792e9dfc548da03`, run `45108198761`, request `s11-renewed-20261123-master`, [the reviewed host policy](evidence/s11-host-cohort-policy.json) permits two exact fingerprints:

- `2188eb82bbb9c539367a3424630dbcca818f313950751afc2c72e18c0f661d7c`
- `c34e7f5bde42bb5fb5568817872b16521dcf3acfffe4ab9c2c95066a15ce8ce7`

The recorded dependencies, source, request and logged renderer matched, while host image/kernel strings differed. The [reviewed assembler](../../tools/s11_delivery/assemble_reviewed.py) reads immutable producing manifests from Git, preserves full original fingerprints and applies this narrowly enumerated policy. It does not assert byte-identical environments, admit unknown future hosts or relax the normal assembler. [The host review](evidence/s11-host-cohort-review.md) and actual encoded-join inspection support this one completed delivery.

### E. Finish, verify and preserve

[The delivery README](../../tools/s11_delivery/README.md) contains exact assembly, `finish_audio`, `verify.py`, `story_review.py` and `archive_master.py` commands. Follow the current owner's output directions: preserve the existing 720p historical derivative but do not create new phone files merely because an older README records its encode command.

For a new authorized output, decode the entire encoded video/audio and verify frame count, rate, dimensions, color metadata, timestamps, score alignment and the silent hold. Inspect actual encoded frames across the story, edits, part joins, costumes, props, words and ending. Use dense temporal sequences where movement or runtime joins need review. Extraction is not inspection. Investigate a suspicious change against authored cues and a controlled reference before accepting it as a seam or dismissing it as lighting.

Preserve the native master before delivery encoding. Audio changes should start from the original verified score, with packet comparisons when preserving reviewed pictures. Archive large masters by exact bytes, test restoration and record hashes. Save outputs, update delivery/state/catalog records, and verify external copies. Record technical success, actual visual review and owner approval as separate states. A new 4K60 show export follows the owner's approval rule and needs its own native-output verification and identity.

## 11. What was actually reviewed

[Final QA](evidence/s11-renewed-final-qa.json) records complete technical decoding of all three current movies, 16,500 frames, 275 seconds, 60 fps, presentation timestamps and audio. Three ten-second audio windows at output seconds 34, 125 and 216 had zero measured lag at 8 kHz and correlation above 0.9999. The silent hold peak was zero. Final stereo decoded sample peaks were approximately 0.940574 and 0.928012, with no sample at or above full scale. These are sample-peak measurements, not oversampled true-peak measurements.

The actual visual review included:

- **311 selected assembled-master frames across all thirteen story sheets (400×225 review-scale extracts; separate native inspections are listed below):** both sides of the seventy authored edits, shot middles, all thirty-nine interior render joins and selected compositions/ending.
- **All twenty cross-host joins:** twelve consecutive encoded frames each, 240 distinct join frames, with actual per-part fingerprints retained.
- **A whole conducting phrase:** sixty-one native conductor crops at 10 fps from 117.1–123.1 seconds, in addition to dense local intervals.
- **The known phrase/architecture composition:** sixteen native samples from 163.4–166.7 seconds, including 165.8 seconds.
- **Delivery copies:** seven HD overview frames with two additional native-resolution inspections, and four samples of the existing 720p derivative.

No blocking issue was observed within that scope. Four nonblocking observations remain visible in the record: strong authored light accents temporarily reduce fine detail; a crown exceeds the top edge at 61.3833 seconds before a wider composition; a small church rooftop touches the lower phrase edge near “sal” at 165.8 seconds while the words remain readable; and a light ribbon crosses part of “love” at 187.2 seconds without erasing the phrase. The brightness rise at 34.366667 seconds was resolved against the music map and a single-renderer reference as an authored pulse, not an unexplained host seam.

The visual review used the pre-headroom master, and packet-level verification establishes identical pictures in the final native master. The HD encode was reviewed separately within its stated sample scope. **No uninterrupted real-time playback of the entire film is claimed. No owner creative approval is recorded.** Authored conducting is not a new motion capture; kinematic and technical measurements do not establish naturalness across every unsampled instant. See [the dense review](evidence/s11-renewed-dense-visual-review.md), [cross-host review](evidence/s11-renewed-cross-host-review.json) and linked opening/middle/ending evidence for exact inventories.

## 12. Future entry points

There is no completed-film queue to restart. Choose the next action from the owner's current request:

| Request | Correct starting point |
| --- | --- |
| Watch, download or hand off current Song 11 | Recover the HD file or exact master archives; use the verified transfer inventory and delivery hashes. No rerender is necessary. |
| Revise Song 11 creatively | Gather exact-output feedback, retain the completed master, author a new 1080p revision in the existing system, and repeat proportionate native motion/composition review. |
| Produce the final 4K60 show video | First establish the required design/timing/content approval. Then freeze a separate native 4K contract, validate representative cost and quality, and render/verify a new deliverable. Do not rename or upscale the existing HD master and call it native 4K. |
| Improve another song | Read its actual recording, design and catalog state; preserve its distinct world and the corrected modesty. Reuse reviewed components rather than copying the same performance/effects loop. |
| Reuse browser/editor/MCP support | Start from the verified cloud route and reusable song-scene contract in section 9. `./scripts/video song-draft <song>` drafts any catalogued song inside its scene's length (the Song 1 to 11 scenes are 60-second promo timelines); `node scripts/prove-workbench.mjs` rechecks the Workbench. Restore dependencies only where needed and integrate reviewed improvements into each song. |
| Diagnose a reported defect | Recover the exact file by hash, reproduce the specified time/view, compare with its producing source and record concrete evidence before modifying it. |

For Claude's first working turn: read the latest owner directions and current conversation, recover the completed source/media and resources, inspect current state and exact evidence, then continue the three already-authorized priorities in their recorded order. There is no unfinished rendering to restart. Keep the current modesty correction, source clock, approval boundary and runtime limitations visible. Update source, documentation and durable delivery records together without changing the historical identity of already finished films.
