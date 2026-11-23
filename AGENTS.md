# Project navigation

## Owner directions (Anthony, November 22, 2026)

These are standing rules for every agent (Claude, Codex, ChatGPT, Gemini). They govern over older records and reviews.

- **Improve the current system, do not replace it.** His words: "ChatGPT was used because it's free. I only used it to establish it and improve the current system ... The intention is to improve the current one; not replace the current one with ChatGPT." Build on the existing engine and render setup; keep what works.
- **The new tools stay.** Blender, the Three.js scene preview, Remotion, Video Shotcraft and the Blender MCP were added "for you to set up and use and make reusable." Get them working and reusable; do not delete or shelve them.
- **No phone versions.** "I don't need a 'phone version'." Do not build phone copies or phone-only review files.
- **Resolution.** The final show performance video is 4K at 60 fps (3840x2160, 60 fps). Work at 1080p until a video is completely figured out (design, timing and content approved); render 4K only after that. "No need to make it 4k until video is completely figured out."
- **GPU work runs on his Mac.** "If GPU is ever needed just use my local computer." His Mac is an Apple M1 Pro (16-core GPU, Metal 4). This is a project exception to the cloud-first rule for GPU work only; CPU work stays in the cloud. Before a heavy local run, check the 1-minute load (stop if above 50) and run with `nice -n 19`. `pipeline/render.py` refuses macOS by default; use its explicit local allowance only for GPU work.
- **Ask when unclear.** "Ask me clarification questions when needed." When a request is ambiguous or changes what he gets, ask him with short clickable options and a recommendation instead of guessing.

- **Tools blocked in the cloud.** The browser 3D preview, Remotion and live Blender are blocked by cloud sandbox limits, not by a missing GPU. Anthony's choice: "Try the cloud first" (for example GitHub Actions runners or another cloud setup); use his Mac only if no cloud route works, and say why.
- **Current priorities, in order:** 1) get the new tools (Blender, Three.js preview, Remotion, Video Shotcraft, Blender MCP) working and reusable for any song; 2) build this week's proven quality gains into the current engine so every song gets them; 3) clean up and organize (one plain status page, stale pull requests, rendering spread across many cloud machines). Finished videos from ChatGPT's file library go into the Drive folder "Concert Backdrops - Songs", Videos.
- **Working mode:** Anthony said "Go ahead on your own" for these priorities. Stop only for real decisions or approvals.

## Earlier navigation

On November 22, 2026, the user withdrew the previously provided AGENTS.md
instructions. This page records that change and points to project facts. The
current conversation supplies the working directions; the earlier instructions
remain available in Git history.

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
