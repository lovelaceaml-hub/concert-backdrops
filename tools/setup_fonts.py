"""Converts the latin woff2 files from the @fontsource packages into the ttf files the engine expects."""
import glob, os, sys
from fontTools.ttLib import TTFont
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
n = 0
for f in sorted(glob.glob(os.path.join(src, "**", "files", "*-latin-*.woff2"), recursive=True)):
    # Preserve source timestamps so identical inputs produce identical font bytes.
    with TTFont(f, recalcTimestamp=False) as t:
        t.flavor = None
        t.save(os.path.join(dst, os.path.basename(f)[:-6] + ".ttf"))
    n += 1
print("fonts converted:", n)
