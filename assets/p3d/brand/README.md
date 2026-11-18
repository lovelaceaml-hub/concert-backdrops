# Assets of the brand pieces (engine/p3d/brand*.py)

| File | What | Source | Licence |
|---|---|---|---|
| `land_2048.png` | Where the land is, for the world of light (engine/p3d/brand_world.py): an equirectangular picture 2048 x 1024, one bit a pixel, white for land. Longitude -180 at the left edge, latitude +90 at the top row | Natural Earth, "Land" at 1:50 million (`ne_50m_land`), version 5, in the GeoJSON of the natural-earth-vector repository: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson (home: https://www.naturalearthdata.com) | Public domain. Natural Earth: "All versions of Natural Earth raster and vector map data found on this website are in the public domain. You may use the maps in any manner, including modifying the content and design, electronic dissemination, and offset printing." (https://www.naturalearthdata.com/about/terms-of-use/). No permission or credit needed; credit given here anyway: Made with Natural Earth. |

Nothing else is stored. The logo, the nine expression symbols and the hearts are drawn from vector geometry
written in the code itself (engine/p3d/brand.py, brand_symbols.py, brand_hearts.py); no picture of the logo
or of the app icons is committed or read at render time.

## Rebuilding

    python tools/build_brand_land.py                    downloads the GeoJSON and writes land_2048.png
    python tools/build_brand_land.py --geojson FILE     from a copy on disk

The polygons are filled at four times the size (holes left open) and box-filtered down, then cut at half.
