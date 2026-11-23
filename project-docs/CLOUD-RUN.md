# Cloud run: finish the engine and rebuild all 11 promos

## Current continuation — November 22, 2026

Start with [the Claude handoff](production-system/CLAUDE-HANDOFF.md),
[current state](production-system/STATE.json) and the standing owner directions
in [root AGENTS.md](../AGENTS.md). The sections below retain their earlier
production/design context. Dated instructions about queues, phone copies,
missing song recordings or cloud-only GPU use do not override the current
handoff and owner directions. All eleven original song recordings are retained;
older full-song movie recovery gaps are documented separately. The completed
renewed Song 11 movie is a 1080p60 design/review delivery; final4K60 requires
owner approval of design, timing and content. There is no unattended render queue.

You are the cloud coordinator for this project. Anthony (not a programmer; plain words; never write an em dash or en dash anywhere) started you from his phone because his Mac was overloaded: "This is loading my laptop too much. All of this needs to be run in the cloud." Everything here runs in the cloud: your own session, your helper agents, and renders in GitHub Actions. He has approved: cloud helpers without limit ("Each thread can use as many Haiku agents as necessary. No limit in the cloud"), Opus for the creative and engine work, merging the work into main ("Have all the docs updated, committed, pushed, and merged"), and attacker reviews ("rounds where Astra will review everything as an attacker, with a really strong will against what you're doing").

## The goal, in his words
"make sure the full expressions a created and used beyond only using current engine effects. Do not be lazy. Make these videos magnificint. They shouldnt just look like one scene but multiple things should go based on the theme" and "The scenes should look different from each other." The message of the whole concert: the Words of Mother's Love bring peace.

## Read first
project-docs/README.md, project-docs/DESIGN-SYSTEM.md (rules, each song's look, decisions), project-docs/UPGRADE-SPEC.md, project-docs/PHASE2.md (what every rebuilt promo must have and the song-specific fixes), project-docs/status/engine.md (engine handoff), project-docs/designs/ (each song's design with its "Promo v2: scenes" plan), project-docs/status/NN.md (what each song already has), project-docs/reviews/ (Astra rounds 0 and 1).

## Step 1: finish the engine (one Opus helper, or yourself)
On branch engine-scenes-figures (pull request 15), after merging origin/main into it:
- Check the demo: download only the "Engine Upgrade Demo frames" artifact of run 43553805648 and look at every sheet. Known problems: words washed out on the bright sunrise, shard lines too thick, light column too strong, figures too small and faint. Fix them.
- Astra round 1 shared fixes (reviews/ASTRA-ROUND-1.md): text protection and dimming behind all text plus the malformed H in HEALING (finding 3); Track rejects keys that are not strictly increasing (8); arch links only after both stars are visible (10); a thin persistent ring per relight plus RINGS_AT_START (11); BOTTOM_CALM on by default for new song files (12); a three-line end card (PHASE2.md item 7).
- Add a share copy to the Render workflow's finish job: 1280x720, under 25 MB, its own artifact "<name> (share)".
- Re-render the demo in the cloud and look at every frame sheet; fix until magnificent and readable. Update engine/UPGRADE-HOWTO.md, docs/HANDOFF.md, project-docs/status/engine.md. Then merge pull request 15 into main.

## Step 2: rebuild the 11 promos (11 parallel Opus helpers, one per song)
After step 1 is merged, give each helper one song and these instructions: follow PHASE2.md exactly, using the song's plates (assets/plates/sNN/), its special figures (assets/song_figures/sNN/, prepared with tools/prepare_figure.py), the shared figure library (assets/figures/), the scene plan in its design text (project-docs/designs/NN *.md, section "Promo v2: scenes"), and the song's look (DESIGN-SYSTEM.md section 6). Where a song lacks plates (song 05 has 3, check each status file), the helper paints the missing ones only if it has an image tool in the cloud; otherwise it builds those scenes from the engine's own layers. Each helper works on branch promo2/sNN from main, rewrites engine/songs/sNN_*.py, renders stills in the cloud and looks at every one at full size, fixes, renders the video, checks the frame sheets and length, writes project-docs/status/NN.md, and opens a pull request. 3 to 6 scenes; people of light act out every expression shown with the full words; at least two signature effects; the reading-time contract; legibility; calm bottom third; the three-line end card; exact star history.

## Step 3: attacker review, then fixes
When all 11 are in, run one attacker helper per song plus one for the whole set, briefed to argue hard against the work: Is every expression acted out, legible, held at least 6 seconds solid, correctly placed? Do the 11 promos look clearly different (composition and objects, not just color)? Are they magnificent and on message? Any bugs, overlaps, busy bottom third? The owning helper fixes and re-renders. Repeat until no HIGH findings remain. Write the findings and their outcome to project-docs/reviews/CLOUD-ATTACK-ROUND-2.md. (The coordinator on Anthony's Mac will also run a review with Astra, the Codex model, afterward.)

## Step 4: merge and report
Merge the 11 pull requests into main. Write project-docs/status/CLOUD-RUN-STATUS.md with: each song's promo run id and artifact names (full and share copies), what was checked, anything unresolved, and the line "CLOUD RUN DONE <date>". The coordinator on the Mac will copy the promos into Anthony's Google Drive folder and send them to him.

## Rules
- Renders only through .github/workflows/render.yml. GitHub API: one "gh run watch <id> --exit-status --interval 180" per run, never poll in loops.
- Full campaign wording for every expression; "(or root)" stays. No faces; Heavenly Mother only from behind or as hands; everyone clothed. No lyrics copied beyond short on-screen fragments. No em dash or en dash anywhere.
- Concession (song 06) and Respect (song 05) are provisional exceptions awaiting Anthony; keep them, described honestly.
- Songs 02 and 10 have no recording: visual only, silent track, file names say "visual only, no music yet".
