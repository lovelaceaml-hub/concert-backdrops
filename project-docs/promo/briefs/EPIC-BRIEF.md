# Epic concert promo: shared brief

Repo: lovelaceaml-hub/concert-backdrops (Python plus moderngl engine in engine/). Anthony (the owner) asked for ONE promo that is magnificent and groundbreaking: a 60 second trailer for the whole Healing Concert, set to a medley, rising from night to bright day. He approved the plan below and wants it fast. Usage does not matter; speed and quality do.

Read the approved plan first: /root/.claude/plans/vectorized-dazzling-platypus.md

## Three helpers work in parallel
| Helper | Branch | Job |
|---|---|---|
| INT | engine-epic | Merge every engine feature branch into one tested engine. |
| MED | epic-medley | Build the 60 s medley clip audio/promo/concert-medley.mp3. |
| FILM | epic-promo (from engine-epic) | Author engine/songs/epic_concert.py and render it. |

The coordinator directs the art and reviews every still.

## Feature branches (all on origin)
engine-living-figures (holds engine-theme and engine-text-anims), engine-gathering (built on living figures), engine-water-symbols, engine-creatures, engine-nature, engine-sky-camera, engine-audio, engine-output, engine-qa. Still being built, merge when they appear: engine-finale, engine-transitions, engine-sea. Each documents its song keys in engine/UPGRADE-HOWTO.md (read with `git show origin/<branch>:engine/UPGRADE-HOWTO.md`).

## Mechanics
- Renders only through .github/workflows/render.yml (cloud). Dispatch with `gh workflow run render.yml --ref <branch> -f song=<file without .py> -f audio=<path> -f mode=stills|video|draft -f stills=<seconds list> -f name=<name>`. Names must not contain parentheses.
- Run id: `gh api "repos/lovelaceaml-hub/concert-backdrops/actions/runs?branch=<branch>&event=workflow_dispatch&per_page=1" --jq '.workflow_runs[0].id'`.
- Wait with exactly ONE `gh run watch <id> --exit-status --interval 180` per run. No polling or sleep loops.
- Artifacts: `gh api repos/lovelaceaml-hub/concert-backdrops/actions/runs/<id>/artifacts`, then `.../actions/artifacts/<aid>/zip > file`, into a fresh empty directory outside the repo. Look at every still at full size with the Read tool.
- GraphQL is blocked: never `gh pr ...`; use `gh api` REST for pull requests.
- Push with `git push -u origin <branch>`, retry network errors up to 4 times.

## Rules
- No em dash or en dash anywhere (code, docs, commits, PR text). Grep your diff.
- Never commit lyrics, videos, frames or personal data. The only new audio allowed is the 60 s medley clip under audio/promo/.
- No faces on any figure (heads are soft glows), everyone clothed, Heavenly Mother only from behind or as hands.
- Nothing dark behind any text. Calm bottom third. No lyrics on screen.
- No full test suites; focused checks only. No Sonnet helpers.
- Commit messages end with:
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01DSHsMeB7ain7qg3RYXYMEW
- PR bodies end with:
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  https://claude.ai/code/session_01DSHsMeB7ain7qg3RYXYMEW
