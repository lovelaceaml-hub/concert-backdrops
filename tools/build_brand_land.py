"""Bakes the land mask of the world of light (engine/p3d/brand_world.py) from Natural Earth.

    python tools/build_brand_land.py                      downloads ne_50m_land.geojson and writes the mask
    python tools/build_brand_land.py --geojson FILE       uses a file already on disk

Writes assets/p3d/brand/land_2048.png: an equirectangular picture (2048 x 1024, one bit a pixel), white where
there is land. Longitude -180 at the left edge, +180 at the right; latitude +90 at the top row, -90 at the
bottom. Source and licence: assets/p3d/brand/README.md (Natural Earth, public domain).
"""
import argparse
import json
import os
import urllib.request

from PIL import Image, ImageDraw

URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "p3d", "brand", "land_2048.png")
W, H, SS = 2048, 1024, 4


def rings(geom):
    if geom["type"] == "Polygon":
        yield geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            yield poly


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geojson", default=None)
    args = ap.parse_args()
    if args.geojson:
        with open(args.geojson, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with urllib.request.urlopen(URL) as r:
            data = json.loads(r.read().decode("utf-8"))
    img = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(img)

    def xy(ring):
        return [((lon + 180.0) / 360.0 * W * SS, (90.0 - lat) / 180.0 * H * SS) for lon, lat in ring]

    for feat in data["features"]:
        for poly in rings(feat["geometry"]):
            d.polygon(xy(poly[0]), fill=255)
            for hole in poly[1:]:
                d.polygon(xy(hole), fill=0)
    img = img.resize((W, H), Image.BOX).point(lambda v: 255 if v >= 128 else 0).convert("1")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
