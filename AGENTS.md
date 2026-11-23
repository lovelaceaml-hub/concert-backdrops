# Project navigation

## Owner directions (Anthony, November 22, 2026)

These are standing rules for every agent (Claude, Codex, ChatGPT, Gemini). They govern over older records and reviews.

- **Improve the current system, do not replace it.** His words: "ChatGPT was used because it's free. I only used it to establish it and improve the current system ... The intention is to improve the current one; not replace the current one with ChatGPT." Build on the existing engine and render setup; keep what works.
- **The new tools stay.** Blender, the Three.js scene preview, Remotion, Video Shotcraft and the Blender MCP were added "for you to set up and use and make reusable." Get them working and reusable; do not delete or shelve them.
- **No phone versions.** "I don't need a 'phone version'." Do not build phone copies or phone-only review files.
- **Resolution.** The final show performance video is 4K at 60 fps (3840x2160, 60 fps). Work at 1080p until a video is completely figured out (design, timing and content approved); render 4K only after that. "No need to make it 4k until video is completely figured out."
- **GPU work runs on his Mac.** "If GPU is ever needed just use my local computer." His Mac is an Apple M1 Pro (16-core GPU, Metal 4). This is a project exception to the cloud-first rule for GPU work only; CPU work stays in the cloud. Before a heavy local run, check the 1-minute load (stop if above 50) and run with `nice -n 19`. `pipeline/render.py` refuses macOS by default; use its explicit local allowance only for GPU work.
- **Ask when unclear.** "Ask me clarification questions when needed." When a request is ambiguous or changes what he gets, ask him with short clickable options and a recommendation instead of guessing.

- **Chat sandbox limits and working cloud routes.** The earlier browser 3D preview, Remotion and live Blender restrictions applied to the chat sandbox. PR #116 subsequently verified the supported GitHub Actions cloud CPU route; see `docs/VIDEO-PIPELINE-VALIDATION.md`. The earlier sandbox limits did not establish a missing GPU. Anthony's choice: "Try the cloud first" (for example GitHub Actions runners or another cloud setup); use his Mac only if no cloud route works, and say why.
- **Current priorities, in order:** 1) get the new tools (Blender, Three.js preview, Remotion, Video Shotcraft, Blender MCP) working and reusable for any song; 2) build this week's proven quality gains into the current engine so every song gets them; 3) clean up and organize (one plain status page, stale pull requests, rendering spread across many cloud machines). Finished videos from ChatGPT's file library go into the Drive folder "Concert Backdrops - Songs", Videos.
- **Working mode:** Anthony said "Go ahead on your own" for these priorities. Stop only for real decisions or approvals.

- **Access set up for smooth cloud production (2026-11-22).** Cloud jobs run on GitHub Actions (see `docs/VIDEO-PIPELINE-VALIDATION.md`). They read songs from and save renders to the Drive folder with `tools/drive_sync.py` and the `GOOGLE_DRIVE_OAUTH` secret. Every agent on the Mac commits as `lovelaceaml-hub <281993171+lovelaceaml-hub@users.noreply.github.com>` (GitHub rejects pushes that expose the private Gmail). Gemini helpers may run read-only git history commands. Never print, copy or commit these secrets.

## Claude project handoff, November 22, 2026

Start with [CLAUDE-HANDOFF.md](project-docs/production-system/CLAUDE-HANDOFF.md)
and the [dated Drive handoff folder](https://drive.google.com/drive/folders/1lxcic8BcSzNgPtEY_Yg_2TBAbNam72dZ).
The handoff covers the whole concert project, including exact media identities,
reproduction resources, retained integrations, current owner directions and
historical recovery gaps. The current transfer and source-snapshot receipts
are in [the handoff completion record](project-docs/production-system/evidence/claude-drive-completion.json).

The Song 11 recreation is complete at native 1080p60 for design/review. Exact-output
owner creative approval is not recorded, so it is not an approved final 4K60
show master. Preserve earlier 720p artifacts as history; do not generate new
phone versions. Recover existing finished files before considering a new render.
There is no unfinished render queue or active background production service.

## Earlier navigation (historical; superseded by the owner directions above)

On November 22, 2026, the user withdrew the previously provided AGENTS.md
instructions. This page records that change and points to project facts. The
current conversation supplies the working directions; the earlier instructions
remain available in Git history.

## Completed Song 11 production

The complete **Almighty God Knows the Future** recreation is rendered, checked and saved; source integration is tracked
in [PR #112](https://github.com/lovelaceaml-hub/concert-backdrops/pull/112).
Start with the current [handoff](project-docs/production-system/AI-HANDOFF.md)
and [recreation record](project-docs/production-system/S11-RECREATION.md).
The owner corrected the earlier body-fitting fan-study direction; PR #111 is
closed without merging. Current work uses separately shaped modest garments
and the established Song 11 concert world. Exact render/delivery state belongs
to the current production record, not the historical Advanced Dance summary.

## Current project records

- [Start here](project-docs/production-system/START-HERE.md): current delivery,
  recovery path and historical production notes.
- [Session handoff](project-docs/production-system/AI-HANDOFF.md): concise
  continuation and source identities.
- [State](project-docs/production-system/STATE.json): current maintenance status.
- [Deliveries](project-docs/production-system/DELIVERIES.md): finished films,
  support files and exact saved links.
- [Advanced Dance workflow](tools/advanced_dance/README.md): choreography,
  anatomy, validation, deliberate reproduction and packaging commands.

Advanced Dance's two revised 32-second films and complete ten-film package
are saved. [PR #109](https://github.com/lovelaceaml-hub/concert-backdrops/pull/109)
merged on November 22, 2026 at commit
`5a602349f90f50d79968bab77dd08db1a20c4339`. The delivered picture source is
`254414bc0356171f7d5ad89361c75d45fd01a407`; later maintenance records describe
documentation and code upkeep separately from those rendered pictures.
