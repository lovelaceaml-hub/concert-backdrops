import sys, os
from PIL import Image, ImageDraw
out = sys.argv[1]; files = sys.argv[2:]
cols = 2; w, h = 960, 540
rows = (len(files)+cols-1)//cols
sheet = Image.new("RGB", (cols*w, rows*h))
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS)
    ImageDraw.Draw(im).text((10, 8), os.path.basename(f), fill=(255, 255, 0))
    sheet.paste(im, ((i % cols)*w, (i//cols)*h))
sheet.save(out, quality=90)
