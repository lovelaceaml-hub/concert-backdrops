# Project status

Updated November 24, 2026, America/Los_Angeles. Machine receipts use UTC.

## Current film

**Almighty God Who Knows the Future** is in a full-film creative interview. The 4:35 1080p60 comparison cut passed technical checks and is available in the private Drive project. The first opening choice is pending. The owner confirmed the promo-style Earth-to-emblem transformation starting at the final chord and the pastel closing card. No render is queued for the next cut. Full review approval precedes the 4K60 show master.

[Next-cut plan](S11-NEXT-CUT.md) · [New-chat prompt](S11-START-PROMPT.txt) · [Current review evidence](evidence/s11-handoff-review-20261124.json) · [Deliveries](DELIVERIES.md)

## Handoff

- 40 media, reference and recovery originals are retained in Drive with exact whole-file or part verification.
- 2 additional verified archives preserve 392 resource paths and 467 visual-review evidence files; the resource installer passed a real clean restoration. The separate [637 MB cloud tool-proof archive](https://drive.google.com/file/d/1IW2BxB1qKPpz-4nrIfD3KSV7H9p6CmdB/view?usp=drivesdk) is retained with a full authenticated Drive hash check.
- The [verified cloud-tools source checkpoint](https://drive.google.com/file/d/1NSXgPH0YSHKTEP9d2dGppXfnQNUSn919/view?usp=drivesdk) preserves all **877 tracked entries** at `252e14145d535d8c8472c72144d85587967f3b2f`, including the merged cloud tools, executable modes and relative symlinks. Actual extraction and restoration with all 392 resource paths passed. The earlier 861-entry archive remains historical; GitHub retains history.
- The existing project index covers 62 folders and 542 objects. It distinguishes metadata locations from actual byte checks.
- 11 historically reported full-film targets remain unrecovered. A different complete-length Song 03 alternate is retained separately. These gaps do not describe the completed renewed Song 11.

[Drive handoff](https://drive.google.com/drive/folders/1lxcic8BcSzNgPtEY_Yg_2TBAbNam72dZ) · [Complete guide](CLAUDE-HANDOFF.md) · [Claude starting prompt](CLAUDE-START-PROMPT.txt) · [Exact completion evidence](evidence/claude-drive-completion.json)

For the final integrated source including subsequent owner PRs #117–#119, use [the final source checkpoint](FINAL-SOURCE-CHECKPOINT.md) and its final manifest/receipt in the source folder. The 877-entry backup above remains a verified recovery baseline. The later changes add Claude cloud-session setup, opt-in engine quality/motion helpers and guarded original-source reproduction; preserve the documented limits of their proofs.

## Tools and reusable scenes

[PR #116](https://github.com/lovelaceaml-hub/concert-backdrops/pull/116) merged at `3812463e1196f4c47b468e05060dbc1c8154ff75`. The completed [cloud proof run 45125796332](https://github.com/lovelaceaml-hub/concert-backdrops/actions/runs/45125796332), source `285df02e51cc68073fe17c8a06ae0d7f54737df7`, passed all three jobs and all eight recorded tool outcomes. It demonstrates real Three.js capture, Remotion assembly, Blender background rendering, live Blender MCP under Xvfb, a CPU Docker build and Drive read/write access. The reusable Song 11 scene proof is 4 seconds at 1080p60; the other encoded demos are 320×180/30 fps. All are technical proofs with creative approval not assessed.

Use the [reusable song-scene instructions](../../docs/VIDEO-PIPELINE.md#reusable-scenes-for-any-song-november-22-2026), [example project](../../projects/song-scene-demo/project.json), [kit adapter](../../pipeline/kit.py) and [cloud proof workflow](../../.github/workflows/tool-proofs.yml). [`tools/drive_sync.py`](../../tools/drive_sync.py) can list/get/put files in the project Drive tree using the Actions secret `GOOGLE_DRIVE_OAUTH`; never copy its value into documentation. These tool changes preserve the finished film's original producing identity.

Remaining limits are specific: Shotcraft Workbench interactive browser playback/export and running production inside the built Docker image are not proved. Short demos do not verify every song or approved 4K production. This local handoff host still lacks the pinned Node/Shotcraft/MCP installations and has Blender 4.3.2 rather than 5.2.4 LTS. Those local gaps do not negate the working GitHub CPU route. [Exact scope and runtime distinctions](CLAUDE-HANDOFF.md#9-actual-status-of-the-additional-tools).

## Owner-authorized continuation

1. Build on the verified cloud tools and reusable scene contract, complete the distinct Workbench interactive checks and make the retained tools useful for every song. Preserve the local-installed/cloud-verified distinction. Try permitted cloud routes first for any remaining sandbox restriction; use the owner's Mac only if none works and explain why.
2. Integrate the proven quality improvements into the existing engine for all songs.
3. Simplify status, stale PRs and distributed cloud rendering. This page is the plain status entry; STATE.json and the evidence files retain the details.

Follow [root AGENTS.md](../../AGENTS.md), including the Mac GPU/load/priority conditions and the actual approval boundary. Continue routine authorized work without asking again; stop for real decisions. Use exact current proof receipts rather than treating historical queues or source presence as runtime evidence.
