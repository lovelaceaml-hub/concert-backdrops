"""Render every implemented native model variant and a labeled contact sheet."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def main():
    from PIL import Image,ImageDraw,ImageFont
    from tools.concert_kit.render import make_renderer,frame,fonts_path,source_hashes
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,default=ROOT/"work/concert-kit/atlas")
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    r=make_renderer(960,540,1,60,scene="model_atlas")
    from songs.model_atlas import CATALOG
    sheet=Image.new("RGB",(1920,1200),(8,12,24))
    draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(str(fonts_path()/"jost-latin-500-normal.ttf"),19)
    identities=source_hashes()
    for i,(family,variant,parameters) in enumerate(CATALOG):
        image=Image.frombytes("RGB",(960,540),frame(r,int((i*2+1)*60),60))
        image.save(a.out/f"{family}-{variant}.png")
        x=(i%3)*640;y=(i//3)*300
        sheet.paste(image.resize((640,270),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+14,y+274),f"{family} / {variant}",font=font,fill=(240,223,190))
        print(f"Rendered {family}/{variant}",flush=True)
    sheet.save(a.out/"model-atlas.jpg",quality=94)
    (a.out/"atlas-manifest.json").write_text(json.dumps({"source_hashes":identities,
        "models":[{"family":f,"variant":v,"parameters":p} for f,v,p in CATALOG],
        "individual_native_size":[960,540],"sheet_size":[1920,1200]},indent=2)+"\n")


if __name__=="__main__":main()
