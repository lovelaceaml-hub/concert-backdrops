# Film 10 with minor additions

The owner chose the original Film 10, Nine Colours, as the finished creative
direction. This version adds only the opening card, closing card, signature,
expression symbols, and world-to-logo sequence. It uses the original engine
snapshot from `d928ff9eafe02ac3150f0c646bdcc497fe5a7278`, the source of render 1
(run 43726203825). It does not use the rejected Restored film's scene code.

The original camera banking, choreography, word transformations and reflections,
comets, hoops, light pulses, lake, mountains, and morning arch remain intact.
The whole original clock moves by two seconds to match the existing approved
lead-in soundtrack. No individual scene is retimed. The music is the original
eight-song edit with that existing lead-in, not a new arrangement.

## Additions

- Opening: elegant serif card, readable from frame 0 through 7 s. Ink changes
  between cream and navy against the original light pulses.
- Signature: discreet bottom-left mark and concert details between the cards.
- Symbols: small traced expression drawings beside the original scenes.
- Finale: a globe with nine surrounding symbols becomes the campaign logo
  before the closing card. The original camera and morning lighting continue.
- Closing: official campaign card, fully readable from 55 s to the final frame.
  The animated logo hands over to its card counterpart without a duplicate.

## Local reproduction

Install the engine's existing dependencies and fonts as documented in the
project handbook. No paid service or GitHub Render workflow is used.

```sh
git fetch origin d928ff9eafe02ac3150f0c646bdcc497fe5a7278
python tools/nine_colours_minor/prepare.py
python tools/nine_colours_minor/check_fidelity.py
python tools/nine_colours_minor/export.py --workers 4 --parts 8
```

`prepare.py` extracts the complete original snapshot privately under
`work/nine_colours_minor/render1`, then prepares the original audio features and
the approved lead-in soundtrack. Shared or protected source files are never
modified. The wrapper only imports missing brand modules and the card renderer
from the current checkout; all existing engine modules come from the snapshot.

Output: 62 seconds, 3720 native frames, H.264/AAC, 1080p60 master and 720p60 phone
copy under `out/nine_colours_minor/`. Render parts are reusable only if their
input manifest and decoded frame counts match. Both video copies keep 60 fps.

`check_fidelity.py` compares SHA-256 hashes of raw 1080p60 frames from the
original renderer with the additions disabled, before the replaced closing
card. It separately renders the final additions in forward and reverse order
in fresh processes. These checks establish source-render fidelity, not identity
to the compressed original 720p30 share file or to the intentionally added art.

All private snapshots, features, caches, stills, logs, and reports are under
`work/nine_colours_minor/` or `out/nine_colours_minor/`. Remove those two folders
to clear this version's generated files. Do not commit them.
