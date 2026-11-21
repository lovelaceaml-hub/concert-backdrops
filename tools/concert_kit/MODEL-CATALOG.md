# Native concert model kit

This is a bounded first expansion of the approved promo's code-drawn light world. It contains six deterministic procedural model families, twelve named variants, and one complete Consideration performance. It is not a claim that every model needed by all eleven full songs is complete.

## Implemented builders

Use `tools.concert_kit.models.build_model(family, **parameters)` after placing the repository's `engine` directory on the import path. Every model returns native p3d batches through `sample(t)`. Units are metres, Y points upward, and the mirror water lies at Y = 0. A numeric seed controls geometric variation. Absolute time controls opening, wind and light. No frame-order state is added by these model builders.

| Family | Named variants | Shape and motion | Useful parameters |
| --- | --- | --- | --- |
| seat | stone, garden | Elliptical seat, curved supports; garden variant has a raised back | at, width, depth, height, seed |
| path | shore, bridge | Winding shore edges and sampled ground; bridge adds an arched height profile | at, length, width, seed |
| reeds | reed, grain | Curved stems, alternating leaves, seed-specific wind, fine or large seed heads | at, count, radius, height, bloom, seed |
| flowers | lotus, star | Six or eight real 3D petal curves open from buds in a timed wave | at, count, radius, height, bloom, seed |
| willow | willow, blossom | Branching crown, hanging strands, wind and timed foliage; blossom has shorter hanging growth and larger pink petals | at, height, spread, bloom, seed |
| lantern | hanging, cup | Curved geometric ribs, an inner light and subtle movement; hanging variant adds a suspension stem | at, size, lit, seed |

These are deliberately stylized light models. The flowers are geometric motifs, not botanical reconstructions. The bridge is a visual model and has not yet been used as a walking contact surface. The seat is placed around the captured seated actor. Future scenes must check contact for their own actor height and pose.

`atlas.py` renders the actual twelve variants into individual 960x540 images and a labeled overview. An implemented builder and an image in an atlas are different from approval in a finished song.

## Human performance

`people.ConsiderationPair` uses the repository's man shape twice, warm gold tunics, detailed hands and the paired `pull_up` and `helped_up` captures. The existing clips are preserved for 6.5 seconds. An isolated shared-grip overlay corrects the retargeted palm gap during the held contact. Independent reference actors avoid a recursive dependency through the existing living-hand layer. Both performers then settle at their captured final root positions into a reciprocal acknowledgement. The recipient adds a hand-on-heart gesture.

The ending settlement is authored for this scene. It is not part of the original capture. It uses a smooth transition to the standing pose and still needs visual scrutiny for foot movement; numerical grip proximity alone does not establish believable acting. The foreground figures use the live skeletal evaluator, not the 15 fps crowd cache.

The scene's pink light originates at an actual posed hand. Its larger world response begins at 11.5 seconds, after the shared action. The light crosses the shore, opens flowers and reaches the tree before the wider reveal. Large text is reserved for the final shot.

## Provenance

- **New environmental models:** original procedural numpy geometry in `models.py`. No photographs, generated images, stock plates or traced building imagery are read by these builders.
- **Human geometry:** existing `assets/p3d/body_v1.npz`, whose source record is `assets/p3d/README.md`. That record identifies the MakeHuman hm08 base, skeleton, skinning and shape targets obtained through the anny 0.6.2 asset package, with its recorded CC0 terms.
- **Paired movement:** the same committed body asset contains the CMU 22_01 and 23_01 clips. The repository records the CMU database and Bruce Hahne BVH conversion provenance. Retain the acknowledgement: The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
- **Campaign identity:** exact existing `p3d.words.EXPRESSIONS` wording and existing `p3d.brand.logo_image` geometry. No substitute emblem was designed.
- **Renderer and body system:** existing current `engine/` source, used through an isolated adapter. Production files are unchanged.
- **Fonts:** the project's Cormorant Garamond and Jost font files. Their bytes are included in render identity.
- **Sound:** the selected authorized Song 07 recording excerpt is prepared separately. Picture model builders do not synthesize music or claim instrument separation.

Legacy folders `assets/figures`, `assets/plates` and `assets/song_figures` contain older AI-generated rasters according to their own README records. They are excluded from this workflow.

## Next reusable families

Build in this order, with a visible proof for each: a carrying pair with one shared prop; a listening pair with seated and standing variants; an after-you action with a gate or bridge; a parent and child encounter; near-camera choir and instrumental performances with solved prop contact; selected detailed church facades; then more varied shore, terrain and vegetation modules. Reuse the existing crowd, church, sky, globe and campaign-symbol libraries for distant scale.

The nine expressions remain the organizing theme. Warm gold humans are the ordinary campaign look. Song 11's blue ensemble is a specific scene treatment. Keep casting and Heavenly Mother portrayal constraints with each scene recipe instead of assuming any generic asset is authorized for every role.
