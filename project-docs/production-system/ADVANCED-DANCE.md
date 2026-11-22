# Advanced Dance production and repair record

The Words of Mother's Love bring peace.

## Current scope

This increment replaces the first two dance slots in Cinematic Ten with complete
32-second performances. Silk in Light is a solo. Petals in Motion is a five-person
ensemble. The other eight delivered movies retain their exact existing bytes in
the newly named complete package.

The frozen corrected picture source is
`254414bc0356171f7d5ad89361c75d45fd01a407`, branch
`creative/advanced-choreography-20261121`,
[PR #109](https://github.com/lovelaceaml-hub/concert-backdrops/pull/109).
The solo 1080p60 master is complete, technically passed, sampled in 150 encoded
frames and saved. Its exact identity and review are in
`evidence/advanced-dance-solo-delivery.json`. The ensemble full-duration even-frame
proof has passed timing and decoding checks. Independent review covered 257 native
window frames and 65 decoded overview samples with no sampled blocker. Its final
60 fps master is now rendering the missing native frames with three workers in
64-frame batches. The complete ten-film package remains pending. Earlier interrupted
workers were recovered without changing pictures; see
`evidence/advanced-dance-execution-policy.json`. No new exact-output owner
approval is recorded. Current status belongs to `STATE.json`.

## Choreography and visual treatment

Each performance connects eight eight-count phrases, 96 explicit steps and two
three-turn runs. The phrase sequence moves from an opening through traveling
sweeps, quick turns, low circles, side chasses and answering fan exchanges to a
shared expanding flower. A closing gesture and breathing continue to 32 seconds.
The five performers use distinct paths and canon timing, with the left pair
turning in the opposite direction.

Pleated fans open and partially fold with the movement. Their handles, short
light trails and released sparks use the final posed hand. Landing accents,
light arches, a mirrored lake, distant trees and lanterns complete the existing
native luminous concert style. There are four camera shots per film.

The supplied moving solo and ensemble references informed pace, diagonal fans,
turns, level changes and formation. This is original authored choreography. Feet
hidden by skirts were not treated as reliable measured motion. The 64-count
clock follows saved machine-estimated beats at original recording speed.

## Repairs made in this increment

- Hands follow the solved forearm with bounded wrist rotation. Finger groups
  curl progressively around the transverse handle and the thumb opposes them.
- A nearly parallel palm-normal preference now releases smoothly instead of
  becoming a rapid forearm flip when its projection approaches zero.
- Palm cues are fitted to each posed shoulder and actual arm length. Their
  fitting distance is recorded separately from the final hand-solve residual.
- Breathing occurs before final hand and foot placement, so a later automatic
  pass cannot move an already solved limb.
- Landing feet anticipate the following support interval. Knees follow actual
  toe direction, and sole geometry controls swing clearance.
- Inner ensemble roles exchange complete mirrored arm paths during the canon.
  The earlier height-only exchange caused short-reach elbows and fan/head
  proximity; targeted corrected checks removed those defects.
- The full flared skirt remains simulated over complete fitted clothing.
  Soft shape forces run for a fixed eight passes, followed by adaptive hard
  edge and body/floor collision convergence. This prevents the soft forces
  from repeatedly reopening the hard constraints.

## Reusable workflow

The [executable module guide](../../tools/advanced_dance/README.md) contains the
commands for source-pinned audio, dense movement checks, costume bakes, exact
cache validation, native rendering and verified packaging. The core modules are
`score.py`, `anatomy.py`, `costume.py`, `props.py` and `lights.py`. They leave the
previous films and default engine behavior intact.

Motion QA evaluates final joint transforms on the output frame and shutter
clocks, plus endpoints and support boundaries. It separates blocking defects
from deliberate high-speed passages needing visual review. The cast checker
uses exact captured poses for body and prop proximity. Costume QA checks the
full cached simulation and the actual rendered interpolation times.

Use the saved problem timestamp to examine preparation, contact, release and
recovery in context. Correct the responsible cue or solve layer, rerun the
relevant checks, freeze the new source and rebuild caches whose identities
change. Inspect a continuous encoded proof and native detail before final
assembly. Keep machine checks, sampled visual review and exact-output owner
approval as separate records.

Exact fan trajectories may be prepared from hash-bound final-FK captures through
the unchanged real fan implementation. Fresh live probes and the actual trail
consumer must match byte-for-byte. Cached cloth is also compared against a
fresh native render in separate processes. These caches reuse computed geometry;
they do not retime the dance or lower picture resolution.

The production flow renders native even frames first for a full 30 fps internal
proof, then reuses them while completing the missing frames for the native
60 fps final movie. Final package validation requires 1,920 frames and 32 seconds
for each revised film, full H.264/AAC decode, exact frame cadence, Rec.709 color
and stereo 48 kHz audio. The eight retained films are hash-verified and copied
without re-encoding.

## Evidence at this checkpoint

- `evidence/advanced-dance-first-checkpoint-inputs.json` preserves the initial
  authored picture snapshot.
- `evidence/advanced-dance-frozen-inputs.json` pins the corrected 236 picture
  dependencies.
- `evidence/advanced-dance-unit-checkpoint.json` records the 28 focused tests
  and the earlier 114 existing pipeline tests.
- Final movement, costume, visual and exact delivered-media evidence will be
  recorded at completion. Intermediate passed checks do not claim a final
  movie or owner approval.
