# Film 10, opening and world revision

The owner chose the original Film 10, Nine Colours, and requested three focused
changes to the previous additions: the centered reference opening with the
sparkle explosion behind its words, a replacement for the Respect scene, and a
clearly visible Earth with orbiting expression symbols before the final card.

This version uses the original engine snapshot from
`d928ff9eafe02ac3150f0c646bdcc497fe5a7278`, the source of render 1
(run 43726203825). It does not use the rejected Restored film's scene code.
Shared engine, song, acting, music and workflow files remain untouched.

## Revised passages

- Opening: cream serif title and official logo over the original night lake.
  The centered card remains fully readable until 7 s, then dissolves by 7.45 s
  as Greeting arrives. A smooth, animated veil keeps the burst behind the words
  legible without a cropped text-mask edge. Four extra seconds precede the
  earlier delivered version, making the movie 66 s.
- Respect: the two rim-lit profiles are replaced by two answering streams of
  gold and lavender light, opening into nine luminous petals beneath the phrase.
  The original Respect words and their timing remain. Comets and lanterns are
  gated only in this passage, retaining each original entry's draw order and
  render flags outside it.
- Finale: a large blue/gold Earth appears against a night sky with all nine
  expression symbols and colored orbit trails. It becomes the official heart
  logo before the pastel closing card. The original arch and bright morning
  burst are replaced in this passage so the globe remains visible.
- Closing: the official coral/navy card is fully readable from 59 s through
  the last frame. Pastel hearts drift at the edges over the moving lake.

The original camera paths, performances, word transformations, reflections and
music remain outside the requested passages. The complete original clock moves
by six seconds. The existing approved lead-in soundtrack receives four seconds
of additional silence, with no tempo, gain or internal edit changes. The owner
explicitly permitted extra opening time. This retains the selected Film 10
soundtrack, including its final accent, rather than substituting a new medley.

## Local reproduction

Install the engine's existing dependencies and fonts as documented in the
project handbook. No paid service or GitHub Render workflow is used.

```sh
git fetch origin d928ff9eafe02ac3150f0c646bdcc497fe5a7278
python tools/nine_colours_minor/prepare.py
python tools/nine_colours_minor/check_fidelity.py
python tools/nine_colours_minor/export.py --workers 4 --parts 8
python tools/nine_colours_minor/verify.py out/nine_colours_revision2/Film-10-Nine-Colours-Revision-2-1080p60.mp4 out/nine_colours_revision2/Film-10-Nine-Colours-Revision-2-phone-720p60.mp4
```

`prepare.py` reuses the private original snapshot under
`work/nine_colours_minor/render1`. The wrapper imports only missing brand modules
and the card renderer from the current checkout. Existing engine modules come
from the pinned snapshot. Features remain on the original clock.

Output: 66 seconds, 3960 native frames, H.264/AAC, 1080p60 master and 720p60 phone
copy under `out/nine_colours_revision2/`. Render parts are reusable only if their
input manifest and decoded frame counts match. Both video copies keep 60 fps.

`check_fidelity.py` compares raw frames at 12 moments outside the intentionally
revised passages against the original engine, with additions disabled. It also
renders 16 final moments in forward and reverse order in fresh processes.
`verify.py` checks encoded timing, repeated frames, chunk joins and audio levels.
Neither check substitutes for visual review or claims that the new art is
pixel-identical to the original movie.

Private features, caches, stills, logs and reports are under
`work/nine_colours_revision2/` and `out/nine_colours_revision2/`. Remove these two
folders to clear this revision's generated files. The original engine snapshot
in `work/nine_colours_minor/render1` is shared with the previous version; leave
it in place unless clearing both versions. Never commit generated media.
