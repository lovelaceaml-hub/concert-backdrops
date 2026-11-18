"""Tile stills (t0012.00.png ...) into a labelled contact sheet JPEG.  No em dash or en dash in this file.
    python tools/s07_full2/sheet.py <dir> <out.jpg> [columns] [tile width] [quality]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

d, out = Path(sys.argv[1]), sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 640
q = int(sys.argv[5]) if len(sys.argv) > 5 else 85
files = sorted(d.glob("t*.png"), key=lambda p: float(p.stem[1:]))
th = tw * 9 // 16
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 26)), (20, 20, 28))
font = ImageFont.truetype(str(Path(__file__).resolve().parents[2] / "fonts/jost-latin-500-normal.ttf"), 18)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
    x, y = (i % cols) * tw, (i // cols) * (th + 26)
    sheet.paste(im, (x, y + 26))
    t = float(f.stem[1:])
    ImageDraw.Draw(sheet).text((x + 8, y + 3), f"{f.stem[1:]} s  ({int(t // 60)}:{t % 60:04.1f})", fill=(235, 225, 200),
                               font=font)
sheet.save(out, quality=q)
print(out, sheet.size)
