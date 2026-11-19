"""Real World Mission Society Church of God buildings, modelled as simple parts for the song 11 backdrop v2
(churches of light round Mount Zion). Owned by the MODELS thread. No em dash or en dash anywhere in this file.

Every entry is a different real building, each with its own public source (the church's own dedication service
posts on watv.org and english.watv.org). Reference only: the silhouette and character of each building (wings,
towers, glass bands, arched windows, roofs, fins, canopies) is modelled by hand from the published photograph.
No sign, emblem, logo or lettering is copied, no photograph is stored in the repo, and no AI image is used.

Not repeated here (already modelled by the placement helper in s11_churches.py): Homaesil (Suwon), Sejong,
Moran (Seongnam), the Bitgaram sail tower (Naju, from the Gangwon post), Sydney, Manaus and Brasilia, the golden
arch tower (Seoul and Daejeon post), the training institute, and the New Jerusalem Pangyo Temple.

Where one post shows several churches without a caption on each photograph, the name follows the order in which
the post introduces the churches and shows the photographs; such entries say so in "note".

DATA FORMAT (one dict per building, in BUILDINGS)
  id, name, city, country, source, year (dedication year or None), note (optional),
  size: (width_m, depth_m, height_m), approximate real size (computed from the parts when not given),
  parts: list of dicts. Metres; x across, z depth, y up; origin at the centre of the ground footprint;
  the front faces -z. "rot" is degrees about the vertical axis through the part's own (x, z) (default 0).
    box          x, z, y0, w, d, h                     a block (w along x, d along z)
    cyl          x, z, y0, w, h                        a cylinder, w = diameter
    gable        x, z, y0, w, d, h, axis ("x" or "z")  a pitched roof over a w by d footprint, ridge along axis
    hip          x, z, y0, w, d, h                     a hipped roof over a w by d footprint
    dome         x, z, y0, w, h                        a dome of diameter w and rise h
    spire        x, z, y0, w, h                        a pointed square spire, base w
    arch_windows x, z, y0, w, h, face, n, rows         n round topped windows per row over a w by h area
    windows      x, z, y0, w, h, face, n, rows         a grid of rectangular windows over a w by h area
    glass_band   x, z, y0, w, h, face, angle           a band of glass on a face; angle slants it (degrees)
    fin_row      x, z, y0, w, h, face, n, d            n vertical fins of depth d spread over width w
    canopy       x, z, y0, w, d, h                     a thin flat slab (h = thickness)
    disc         x, z, y0, w, face                     a round disc on a face, centre at height y0
    cross        x, z, y0, w, h                        only where the real building has one
    steps        x, z, y0, w, d, h, n                  a flight of n steps rising toward +z
  For face parts, (x, z) is the centre of the area ON the face plane, and face is one of
  "front" (-z), "back" (+z), "left" (-x), "right" (+x).
  col: "pearl", "white", "glass", "teal", "gold", "rose", "warm", "stone", "grey".
"""

W_SRC = "https://watv.org/"


def box(x, z, w, d, h, col, y0=0.0, rot=0):
    return {"kind": "box", "x": x, "z": z, "y0": y0, "w": w, "d": d, "h": h, "rot": rot, "col": col}


def cyl(x, z, w, h, col, y0=0.0):
    return {"kind": "cyl", "x": x, "z": z, "y0": y0, "w": w, "d": w, "h": h, "rot": 0, "col": col}


def gable(x, z, w, d, h, col, y0, axis="x", rot=0):
    return {"kind": "gable", "x": x, "z": z, "y0": y0, "w": w, "d": d, "h": h, "rot": rot, "col": col,
            "axis": axis}


def hip(x, z, w, d, h, col, y0, rot=0):
    return {"kind": "hip", "x": x, "z": z, "y0": y0, "w": w, "d": d, "h": h, "rot": rot, "col": col}


def dome(x, z, w, h, col, y0):
    return {"kind": "dome", "x": x, "z": z, "y0": y0, "w": w, "d": w, "h": h, "rot": 0, "col": col}


def spire(x, z, w, h, col, y0):
    return {"kind": "spire", "x": x, "z": z, "y0": y0, "w": w, "d": w, "h": h, "rot": 0, "col": col}


def face_part(kind, x, z, w, h, col, y0, face="front", **kw):
    p = {"kind": kind, "x": x, "z": z, "y0": y0, "w": w, "d": 0.0, "h": h, "rot": 0, "col": col, "face": face}
    p.update(kw)
    return p


def arches(x, z, w, h, n, rows, col="glass", y0=0.0, face="front"):
    return face_part("arch_windows", x, z, w, h, col, y0, face, n=n, rows=rows)


def wins(x, z, w, h, n, rows, col="glass", y0=0.0, face="front"):
    return face_part("windows", x, z, w, h, col, y0, face, n=n, rows=rows)


def band(x, z, w, h, col="glass", y0=0.0, face="front", angle=0):
    return face_part("glass_band", x, z, w, h, col, y0, face, angle=angle)


def fins(x, z, w, h, n, depth, col="white", y0=0.0, face="front"):
    p = face_part("fin_row", x, z, w, h, col, y0, face, n=n)
    p["d"] = depth
    return p


def canopy(x, z, w, d, col="white", y0=3.0, h=0.4):
    return {"kind": "canopy", "x": x, "z": z, "y0": y0, "w": w, "d": d, "h": h, "rot": 0, "col": col}


def disc(x, z, w, col, y0, face="front"):
    return face_part("disc", x, z, w, w, col, y0, face)


def steps(x, z, w, d, h, n=6, col="stone", y0=0.0):
    return {"kind": "steps", "x": x, "z": z, "y0": y0, "w": w, "d": d, "h": h, "rot": 0, "col": col, "n": n}


GANGWON = W_SRC + "church-dedication-service-gangwon/"
HWASEONG = W_SRC + "church-dedication-service-hwaseong/"
JINJU = W_SRC + "church-dedication-service-jinju/"
YANGSAN26 = W_SRC + "church-dedication-service-yangsan/"
SUWON24 = W_SRC + "church-dedication-service-suwon/"

BUILDINGS = [
    # ---- batch 1 ----------------------------------------------------------------------------------------
    {"id": "kr_hongcheon", "name": "Hongcheon church", "city": "Hongcheon", "country": "Korea",
     "source": GANGWON, "year": 2023,
     "note": "two buildings: a stone block with a great blue glass front, and a glass stair tower by a white wing",
     "parts": [
         box(-6, 0, 22, 18, 11, "stone"),
         band(-6, -9, 17, 8, y0=1.5),
         box(10, 1, 10, 16, 12, "pearl"),
         wins(11, -7, 6, 8, 2, 3, "glass", y0=2),
         box(5, -5, 6, 6, 15, "glass"),
         fins(5, -8, 6, 15, 4, 0.3, "white"),
         canopy(5, -9.5, 6, 3, y0=3),
     ]},
    {"id": "kr_wonju", "name": "Wonju church", "city": "Wonju", "country": "Korea",
     "source": GANGWON, "year": 2023,
     "note": "five storey white tower banded in green, beside a long raised hall of blue glass with a wave roof edge",
     "parts": [
         box(-14, 0, 14, 16, 19, "white"),
         wins(-14, -8, 12, 16, 4, 5, "teal", y0=2),
         box(6, 0, 30, 20, 4, "grey"),
         box(6, 0, 30, 20, 6, "glass", y0=4),
         fins(6, -10, 28, 5, 16, 0.4, "white", y0=4.5),
         canopy(6, 0, 31, 21, "pearl", y0=10, h=0.6),
         box(-5, -8, 5, 5, 6, "stone"),
     ]},
    {"id": "kr_yeosu", "name": "Yeosu church", "city": "Yeosu", "country": "Korea",
     "source": GANGWON, "year": 2023,
     "note": "a broad pale stone front over a terrace and ramp, a taller white block with a glass slot to the left",
     "parts": [
         box(6, 0, 34, 22, 14, "pearl"),
         wins(6, -11, 30, 3, 8, 1, "glass", y0=1),
         box(-16, 2, 14, 18, 17, "white"),
         band(-15, -7, 3, 10, y0=4),
         box(23.5, 0, 1.2, 22, 15, "rose"),
         canopy(4, -13, 30, 4, "grey", y0=2, h=0.4),
         steps(4, -17, 30, 4, 2, 5),
     ]},
    {"id": "kr_maegok_suncheon", "name": "Maegok church", "city": "Suncheon", "country": "Korea",
     "source": GANGWON, "year": 2023,
     "note": "a stone block with one great round arched glass window up the front and a curved stone flank",
     "parts": [
         box(0, 0, 24, 20, 22, "stone"),
         arches(-2, -10, 7, 18, 1, 1, "glass"),
         band(-10, -10, 3, 14, y0=4),
         wins(7, -10, 6, 16, 2, 5, "white", y0=3),
         cyl(11, 4, 8, 21, "stone"),
         box(0, 0, 10, 8, 2, "stone", y0=22),
     ]},
    {"id": "kr_gwangsan_gwangju", "name": "Gwangsan church", "city": "Gwangju", "country": "Korea",
     "source": GANGWON, "year": 2023,
     "note": "warm brick blocks with blue glass curtain walls and a brick stair tower slit with glass",
     "parts": [
         box(-6, 0, 20, 16, 12, "warm"),
         band(-6, -8, 16, 9, y0=1.5),
         box(6, -1, 8, 10, 15, "warm"),
         band(6, -6, 2.5, 13, y0=1),
         box(16, 4, 14, 20, 12, "warm"),
         wins(16, -6, 10, 8, 3, 2, "glass", y0=2),
         box(10, 14, 12, 8, 9, "white"),
     ]},
    {"id": "kr_hyangnam_hwaseong", "name": "Hyangnam church", "city": "Hwaseong", "country": "Korea",
     "source": HWASEONG, "year": 2022,
     "note": "white four storey block, a golden panel with tall slot windows on the left, a blue glass wall right",
     "parts": [
         box(0, 0, 26, 18, 15, "white"),
         box(-8, -9.6, 9, 1.2, 11, "gold", y0=2),
         wins(-8, -10.2, 7, 8, 5, 1, "white", y0=3),
         band(6, -9, 12, 11, y0=2),
         box(13.5, 0, 1.5, 18, 16, "white"),
         canopy(0, -9.5, 27, 2, "white", y0=15, h=0.6),
     ]},
    {"id": "kr_majang_icheon", "name": "Majang church", "city": "Icheon", "country": "Korea",
     "source": HWASEONG, "year": 2022,
     "note": "a blue glass building under a big golden framed upper box with white fins, a tall glass tower right",
     "parts": [
         box(0, 0, 34, 22, 9, "glass"),
         box(-4, -2, 22, 18, 7, "warm", y0=9),
         fins(-4, -11, 16, 5, 10, 0.6, "white", y0=10),
         box(6, 0, 8, 16, 17, "glass"),
         box(12, 0, 7, 8, 22, "glass"),
         box(-15, 0, 6, 12, 12, "glass"),
         canopy(0, -12, 26, 2, "white", y0=4),
     ]},
    {"id": "kr_eunhaeng_siheung", "name": "Eunhaeng church", "city": "Siheung", "country": "Korea",
     "source": HWASEONG, "year": 2022,
     "note": "a tall white stone tower with a slanting teal glass slit and a curved back, a lower white wing",
     "parts": [
         box(-8, 0, 16, 16, 9, "white"),
         wins(-8, -8, 12, 6, 4, 2, "glass", y0=1.5),
         box(4, 0, 8, 14, 22, "white"),
         band(4, -7, 2.5, 19, "teal", y0=1, angle=6),
         cyl(8, 1, 10, 20, "white"),
         steps(11, -9, 5, 10, 3, 8),
     ]},
    {"id": "kr_banghwa_seoul", "name": "Banghwa church", "city": "Seoul", "country": "Korea",
     "source": HWASEONG, "year": 2022,
     "note": "pale stone in steps, rows of small windows, a slim tower with a glass strip and a dark lantern on top",
     "parts": [
         box(-4, 0, 24, 18, 13, "stone"),
         box(-12, 0, 8, 18, 15, "stone"),
         wins(-4, -9, 20, 10, 6, 4, "white", y0=1.5),
         box(10, 0, 7, 10, 21, "stone"),
         band(8.5, -5, 2, 18, y0=1),
         box(10, 0, 4, 4, 4, "grey", y0=21),
         wins(10, -2, 3, 3, 2, 1, "glass", y0=21.5),
     ]},
    {"id": "kr_jinju", "name": "Jinju church", "city": "Jinju", "country": "Korea",
     "source": JINJU, "year": 2023,
     "parts": [
         box(0, 0, 36, 22, 16, "warm"),
         fins(0, -11, 34, 14, 12, 1.0, "pearl", y0=1),
         cyl(0, -12, 12, 15, "glass"),
         box(0, -2, 14, 12, 4, "white", y0=16),
         box(0, 2, 3, 3, 30, "warm"),
         canopy(0, -18.5, 8, 2, "white", y0=3.5),
     ]},
    {"id": "mx_puebla", "name": "Puebla church", "city": "Puebla", "country": "Mexico",
     "source": JINJU, "year": None,
     "note": "shown in the Jinju post among new temples abroad: white blocks, a stone strip, bands of windows",
     "parts": [
         box(-3, 0, 16, 16, 11, "white"),
         box(7, 0, 8, 16, 12, "white"),
         box(-3, -8.3, 2, 0.6, 11, "grey"),
         wins(-7, -8, 6, 8, 2, 3, "glass", y0=1.5),
         wins(1.5, -8, 4, 8, 1, 3, "glass", y0=1.5),
         canopy(-3, -9, 6, 2, "white", y0=3, h=0.3),
     ]},
    {"id": "mx_atlixco", "name": "Atlixco church", "city": "Atlixco", "country": "Mexico",
     "source": JINJU, "year": None,
     "note": "shown in the Jinju post: a broad white front with two bands of teal glass and a small porch on steps",
     "parts": [
         box(0, 0, 34, 20, 12, "white"),
         band(0, -10, 30, 2, "teal", y0=9),
         band(0, -10, 26, 1.6, "teal", y0=6),
         box(-3, -11, 5, 2, 4, "white"),
         gable(-3, -11, 5.4, 2, 1, "white", y0=4, axis="z"),
         steps(-3, -13.5, 5, 3, 1.5, 5, "grey"),
         wins(-12, -10, 6, 2.5, 3, 1, "glass", y0=1),
         wins(6, -10, 6, 2.5, 3, 1, "glass", y0=1),
     ]},
    {"id": "kr_woongsang_yangsan", "name": "Woongsang church", "city": "Yangsan", "country": "Korea",
     "source": YANGSAN26, "year": 2026,
     "note": "a white tower with a round arched top, and a front of tall blue and white wave fins over a curved canopy",
     "parts": [
         box(-6, 0, 6, 8, 24, "white"),
         dome(-6, 0, 6, 3, "white", y0=24),
         band(-6, -4, 2, 20, y0=2),
         box(4, 0, 18, 20, 18, "white"),
         fins(6, -10, 12, 15, 7, 1.2, "glass", y0=3),
         canopy(2, -12, 20, 4, "white", y0=3, h=0.5),
         box(-14, 0, 8, 16, 8, "pearl"),
     ]},
    {"id": "kr_miryang", "name": "Miryang church", "city": "Miryang", "country": "Korea",
     "source": YANGSAN26, "year": 2026,
     "note": "white walls with two rows of tall round arched windows under a grey hipped roof, a small pediment door",
     "parts": [
         box(2, 0, 26, 22, 13, "white"),
         hip(2, 0, 26, 22, 4, "grey", y0=13),
         arches(3, -11, 22, 9, 7, 2, "glass", y0=2),
         box(-15, 0, 8, 22, 14, "white"),
         arches(-15, -11, 5, 10, 2, 3, "glass", y0=2),
         box(-6, -11.5, 4, 1, 3.5, "white"),
         gable(-6, -11.5, 4.6, 1.2, 1.2, "white", y0=3.5, axis="z"),
     ]},
    {"id": "kr_seryu_suwon", "name": "Seryu church", "city": "Suwon", "country": "Korea",
     "source": SUWON24, "year": 2024,
     "note": "white blocks with a tall golden slab tower dotted with small windows, and vertical strips of blue glass",
     "parts": [
         box(-3, 0, 18, 16, 15, "white"),
         box(6, -1, 6, 12, 20, "gold"),
         wins(6, -7, 4, 14, 3, 6, "white", y0=3),
         band(2.5, -8, 1.5, 19),
         band(-6, -8, 4, 10, y0=4),
         box(12, 0, 6, 14, 14, "white"),
         band(12, -7, 1.5, 12, y0=1),
     ]},
]


def _fill_size(b):
    if "size" in b:
        return
    xs, zs, ys = [], [], []
    for p in b["parts"]:
        w, d = p.get("w", 0.0), p.get("d", 0.0)
        if p["kind"] in ("box", "cyl", "gable", "hip", "dome", "spire", "canopy", "steps"):
            xs += [p["x"] - w / 2, p["x"] + w / 2]
            zs += [p["z"] - d / 2, p["z"] + d / 2]
        ys.append(p["y0"] + p.get("h", 0.0))
    b["size"] = (round(max(xs) - min(xs), 1), round(max(zs) - min(zs), 1), round(max(ys), 1))


for _b in BUILDINGS:
    _b.setdefault("note", "")
    _fill_size(_b)


def all_buildings():
    return BUILDINGS
