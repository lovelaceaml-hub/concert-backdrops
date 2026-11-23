# Final source checkpoint

## Final snapshot and verified baseline

**Use the final snapshot for the complete handoff source.** The verified recovery baseline C contains **877 tracked entries** at `252e14145d535d8c8472c72144d85587967f3b2f`. It includes PR #116, but predates the owner updates in PRs #117–119. Preserve it as provenance; it is not the latest code.

The final snapshot covers all owner updates observed through **PR #119**, together with the handoff closeout. Its exact closing merge commit, archive hash and entry count are recorded **after that merge** in the external manifest and receipt. Obtain these four files from [Source and Documentation](https://drive.google.com/drive/folders/1ARIxA-UsuIR0xEVeDIBMH-MMgoxnafHn):

- `Concert_Project_Final_Handoff_2026-11-22.tar.gz`
- `FINAL-SOURCE-MANIFEST.json`
- `README_FINAL_SOURCE.md`
- `FINAL-HANDOFF-RECEIPT.json`

Check their matching identity and verification status; this page does not substitute a guessed commit or hash. [GitHub main and history](https://github.com/lovelaceaml-hub/concert-backdrops) remain the source authority. A source archive preserves a snapshot, not Git history.

## Start Claude in the cloud

Open the Git repository and read [AGENTS.md](../../AGENTS.md), [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md) and [VIDEO-PIPELINE.md](../../docs/VIDEO-PIPELINE.md).

PR #117 adds [the Claude startup hook](../../.claude/settings.json) and [cloud-session-setup.sh](../../scripts/cloud-session-setup.sh). In a remote Claude session it prepares the p3d runtime and reference fonts; it does not render or establish full-tool readiness. Setup is best effort and exits successfully even on failure: read `work/cloud-setup.log` for the actual outcome.

PR #118 adds opt-in engine quality settings, shared gesture/foot/prop helpers and `video reproduce`; PR #119 adds reproduction safeguards. Legacy defaults and frozen-film identities remain separate from new quality choices. Reproduction uses the original source commit in an isolated worktree, with matching engine files and restored private inputs. Read the pipeline guide's per-film commit requirements. Full-film validation of the new quality treatment and end-to-end reproduction of every approved film have **not** been established.

## Recover the final source and resources

From the directory containing the downloaded final archive:

```bash
tar -xzf Concert_Project_Final_Handoff_2026-11-22.tar.gz
cd concert-backdrops
```

The tar preserves executable modes and relative symlinks. Dependencies, private media and Git history are separate. If the **392 reproduction resource paths** are needed, prepare and activate the Python environment described in the handoff. From the directory containing the resource ZIP:

```bash
python3 -m zipfile -e Concert_Reproduction_Resources_2026-11-22.zip handoff-resources
python3 handoff-resources/restore_resources.py \
  --archive Concert_Reproduction_Resources_2026-11-22.zip \
  --project /path/to/concert-backdrops
```

Use the actual extracted project path. Resource restoration is not dependency installation or a render.

The completed 275-second Song 11 film retains producing source `eec8d16519ea82309ef851975792e9dfc548da03` and its recorded media hashes. Exact-film owner design approval remains unrecorded; final 4K60 follows approval. No new phone versions or unfinished film-render queue is implied by this source checkpoint.
