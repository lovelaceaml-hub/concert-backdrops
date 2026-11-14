# Shared figure library: people of light for the nine Words of Mother's Love

Each picture is one pose of a pair of people: clean white line art on black, 1536x1024 grayscale, the drawing 940 pixels tall with the feet on the line 24 pixels above the bottom (prepared with tools/prepare_figure.py). The engine turns each pose into golden sparks with a soft outline and inner light (engine/UPGRADE-HOWTO.md, section B). Use the poses of one expression in order in a figure's `poses` list; the sparks move from one to the next.

The same two people appear in every pose: on the left, a person in a long robe with a soft hooded cowl collar; on the right, a person in a long robe with a head veil over the shoulders. Faceless, fully clothed, seen from the side. Use `flip=True` to swap sides.

Made 2026-11-13 with the media-studio make_image tool (gpt-image-2 through Codex), checked one by one (no face, no text, good hands, modest clothing). The original pictures are in ~/Pictures/AI Images/concert-backdrops-figures/ on Anthony's Mac.

## Poses

LIST_GOES_HERE

## Prompt pattern (for new special figures in the same style)

"Minimal line art illustration: clean white single-weight contour lines on a pure black background, very faint inner fill. Two people, full body, seen from the side ... Left person wears a long robe with a soft hooded cowl collar; right person wears a long robe with a head veil draped over the shoulders. <the act> Heads are smooth plain ovals with NO facial features at all (no eyes, no nose, no mouth). Both clearly clothed, modest, soft folds. Both fill about 85 percent of the image height, feet near the bottom edge. No ground line, no floor, no text, no letters, no background, no shadows, nothing else." Size 1536x1024.
