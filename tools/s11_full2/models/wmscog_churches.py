"""Real World Mission Society Church of God buildings, modelled as simple parts for the song 11 backdrop v2
(churches of light round Mount Zion). Owned by the MODELS thread. No em dash or en dash anywhere in this file.

Every entry is a different real building, each with its own public source (the church's own dedication service
posts on watv.org and english.watv.org). Reference only: the silhouette and character of each building (wings,
towers, glass bands, arched windows, roofs, fins, canopies) is modelled by hand from the published photograph.
No sign, emblem, logo or lettering is copied, no photograph is stored in the repo, and no AI image is used.

Not repeated here (already modelled by the placement helper in s11_churches.py): Homaesil (Suwon), Sejong,
Moran (Seongnam), the Bitgaram sail tower (Naju, from the Gangwon post), Sydney, Manaus and Brasilia, the golden
arch tower (Seoul and Daejeon post), the training institute, and the New Jerusalem Pangyo Temple.

Overseas churches come from the church's own event posts (Passover, Pentecost, Resurrection) where a photograph
of the members in front of the building carries a caption naming that church; only buildings clearly visible are used.

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
RES25 = W_SRC + "resurrection-assemblies-2025/"
ASC26 = W_SRC + "2026-ascension-day-pentecost/"
PASS26 = W_SRC + "passover-2026/"
YESAN = W_SRC + "church-dedication-service-yesan-pyeongtaek-incheon/"
YBU = W_SRC + "church-dedication-service-yangsan-busan-ulsan/"
CHEONGJU = W_SRC + "church-dedication-service-cheongju/"
CHEONAN = W_SRC + "church-dedication-service-cheonan/"
UIWANG = W_SRC + "church-dedication-service-uiwang/"
WONJU26 = W_SRC + "church-dedication-service-wonju/"
ASAN23 = W_SRC + "church-dedication-service-asan/"
EN = "https://english.watv.org/news/print.asp?idx="

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
    # ---- batch 2 ----------------------------------------------------------------------------------------
    {"id": "za_pretoria", "name": "Pretoria church", "city": "Pretoria", "country": "South Africa",
     "source": RES25, "year": None,
     "note": "a brick hall under one steep pitched roof, its tall front gable filled with white fins and glass, "
             "a slim white bell slab to the right",
     "parts": [
         box(0, 0, 24, 36, 6, "warm"),
         gable(0, 0, 24, 36, 12, "grey", y0=6, axis="z"),
         band(0, -18, 14, 10, y0=1),
         fins(0, -18, 16, 13, 9, 0.8, "white"),
         box(18, -6, 3, 2, 24, "white"),
         box(-16, 0, 8, 20, 4, "warm"),
     ]},
    {"id": "us_atlanta", "name": "Atlanta church", "city": "Atlanta, Georgia", "country": "U.S.",
     "source": RES25, "year": None,
     "note": "long brick halls under grey gable roofs, a front gable wing, and a white steeple on the ridge",
     "parts": [
         box(4, 0, 36, 22, 7, "warm"),
         gable(4, 0, 36, 22, 6, "grey", y0=7, axis="x"),
         box(14, -6, 12, 26, 7, "warm"),
         gable(14, -6, 12, 26, 6, "grey", y0=7, axis="z"),
         wins(14, -19, 9, 4, 3, 1, "glass", y0=1.5),
         box(4, 0, 2.5, 2.5, 4, "white", y0=13),
         spire(4, 0, 2.5, 8, "white", y0=17),
         box(-20, 2, 14, 14, 4.5, "warm"),
         hip(-20, 2, 14, 14, 2, "grey", y0=4.5),
     ]},
    {"id": "us_miami", "name": "Miami church", "city": "Miami, Florida", "country": "U.S.",
     "source": RES25, "year": None,
     "note": "a very steep pointed A frame roof with a glass slit up its gable, behind a long white arcade of round arches",
     "parts": [
         box(0, -14, 40, 4, 5, "white"),
         arches(0, -16, 38, 4.5, 8, 1, "white"),
         box(0, 6, 18, 30, 4, "warm"),
         gable(0, 6, 18, 30, 20, "grey", y0=4, axis="z"),
         band(0, -9, 1.5, 18, y0=3),
     ]},
    {"id": "us_chicago", "name": "Chicago church", "city": "Chicago, Illinois", "country": "U.S.",
     "source": ASC26, "year": None,
     "note": "a two storey red brick block with a white pediment, beside a long low brick wing under a grey gable",
     "parts": [
         box(-12, 0, 18, 20, 10, "warm"),
         gable(-12, 0, 18, 20, 4, "white", y0=10, axis="z"),
         wins(-12, -10, 14, 7, 4, 2, "white", y0=1.5),
         box(8, 2, 26, 14, 4.5, "warm"),
         gable(8, 2, 26, 14, 3, "grey", y0=4.5, axis="x"),
         wins(8, -5, 22, 2.5, 6, 1, "glass", y0=1),
     ]},
    {"id": "za_durban", "name": "Durban church", "city": "Durban", "country": "South Africa",
     "source": ASC26, "year": None,
     "note": "a single storey face brick hall under a broad hipped roof, a white gabled entrance porch and white fins",
     "parts": [
         box(0, 0, 26, 18, 4, "warm"),
         hip(0, 0, 28, 20, 4, "grey", y0=4),
         box(0, -10, 8, 4, 4, "white"),
         gable(0, -10, 9, 4, 2.5, "grey", y0=4, axis="z"),
         fins(7, -9, 10, 3.5, 4, 0.3, "white"),
         wins(-8, -9, 8, 2, 2, 1, "glass", y0=1),
     ]},
    {"id": "cr_san_jose", "name": "San Jose church", "city": "San Jose", "country": "Costa Rica",
     "source": ASC26, "year": None,
     "note": "a white two storey house with a steep red hipped roof and a gabled dormer, a modern glass block beside it",
     "parts": [
         box(2, 0, 14, 12, 6.5, "white"),
         hip(2, 0, 15, 13, 4, "rose", y0=6.5),
         gable(2, -6, 6, 2, 3, "rose", y0=6.5, axis="z"),
         wins(2, -6, 10, 4, 3, 1, "glass", y0=2),
         box(6, -8, 4, 4, 3, "white"),
         steps(6, -11, 4, 2, 1, 4),
         box(-10, 0, 10, 12, 9, "grey"),
         wins(-10, -6, 8, 7, 3, 2, "glass", y0=1),
     ]},
    {"id": "np_itahari", "name": "Itahari church", "city": "Itahari", "country": "Nepal",
     "source": ASC26, "year": None,
     "note": "a white three storey building with long balconies, and a small pitched roof pavilion on the roof",
     "parts": [
         box(0, 0, 28, 14, 10, "white"),
         canopy(-4, -7.5, 12, 2, "white", y0=3.5, h=0.3),
         canopy(-4, -7.5, 12, 2, "white", y0=7, h=0.3),
         wins(-4, -7, 10, 6, 3, 2, "glass", y0=1),
         wins(7, -7, 12, 7, 4, 2, "glass", y0=1.5),
         box(11, -3, 6, 6, 3, "white", y0=10),
         gable(11, -3, 7, 7, 2, "rose", y0=13, axis="x"),
     ]},
    {"id": "nz_auckland2", "name": "Auckland 2nd church", "city": "Auckland", "country": "New Zealand",
     "source": ASC26, "year": None,
     "note": "a grey metal clad block with a glass top storey, and a round entrance portico of tall white fins",
     "parts": [
         box(-8, 0, 24, 20, 12, "grey"),
         band(-8, -10, 22, 3, y0=9),
         cyl(6, -6, 8, 10, "glass"),
         fins(6, -10, 8, 10, 7, 1.0, "white"),
         box(14, 0, 6, 10, 5, "grey"),
     ]},
    {"id": "na_windhoek", "name": "Windhoek church", "city": "Windhoek", "country": "Namibia",
     "source": PASS26, "year": None,
     "note": "a white two storey building with a flat roof, wide windows and an outside stair up to the upper hall",
     "parts": [
         box(0, 0, 20, 12, 7, "white"),
         canopy(0, 0, 21, 13, "white", y0=7, h=0.5),
         wins(2, -6, 12, 2.5, 3, 1, "glass", y0=4),
         wins(2, -6, 12, 2.5, 4, 1, "glass", y0=0.8),
         steps(-8, -9, 2, 6, 3.5, 8, "white"),
         canopy(-8, -6.5, 3, 1.5, "white", y0=3.5, h=0.3),
     ]},
    {"id": "kr_yulha_gimhae", "name": "Yulha church", "city": "Gimhae", "country": "Korea",
     "source": YANGSAN26, "year": 2026,
     "note": "slim blocks side by side: white, blue glass, a dark slab, white and a tall glass corner",
     "parts": [
         box(-8, 0, 8, 16, 16, "white"),
         wins(-8, -8, 6, 3, 3, 1, "glass", y0=6),
         box(-2, 0, 6, 16, 18, "glass"),
         box(3, -2, 5, 12, 17, "grey"),
         box(7, 0, 3, 16, 20, "white"),
         box(10, 0, 4, 16, 20, "glass"),
         canopy(-4, -9, 10, 2, "rose", y0=3),
     ]},
    {"id": "kr_yesan", "name": "Yesan church", "city": "Yesan (Naepo)", "country": "Korea",
     "source": YESAN, "year": 2025,
     "note": "a white block under a floating roof plane edged in warm brown, with a glass corner bay",
     "parts": [
         box(0, 0, 30, 20, 14, "white"),
         canopy(0, 0, 34, 22, "warm", y0=14.5, h=0.8),
         box(-15.5, 0, 1.2, 22, 15, "warm"),
         box(8, -8, 8, 6, 14, "glass"),
         wins(-4, -10, 18, 10, 7, 3, "glass", y0=2),
         box(14, -6, 6, 8, 4, "warm"),
         steps(12, -14, 8, 4, 1.2, 4),
     ]},
    {"id": "kr_pyeongtaek_godeok", "name": "Pyeongtaek Godeok church", "city": "Pyeongtaek", "country": "Korea",
     "source": YESAN, "year": 2025,
     "note": "a grey stone block, a taller glass stair tower, and a white block with a glass curtain wall",
     "parts": [
         box(-10, 0, 12, 16, 10, "stone"),
         box(-2, 0, 6, 10, 14, "glass"),
         box(8, 0, 16, 18, 11, "white"),
         band(8, -9, 12, 9, y0=1),
         canopy(4, -10, 8, 2, "grey", y0=3.5),
     ]},
    {"id": "kr_incheon_donggu", "name": "Incheon Dong-gu church", "city": "Incheon", "country": "Korea",
     "source": YESAN, "year": 2025,
     "note": "a slim pale stone tower with a projecting bay of blue glass and an open frame on the roof",
     "parts": [
         box(0, 0, 10, 12, 18, "pearl"),
         box(-1, -6.5, 6, 1.5, 15, "glass", y0=2),
         box(6.5, 0, 4, 12, 14, "glass"),
         box(-1, 0, 8, 8, 2, "white", y0=18),
         fins(-1, -4, 8, 2, 6, 0.2, "white", y0=18),
         steps(-9, -6, 3, 10, 3, 10),
     ]},
    {"id": "kr_songdo", "name": "Songdo church", "city": "Incheon (Songdo)", "country": "Korea",
     "source": YESAN, "year": 2025,
     "note": "pale stone with a rounded corner and louvres, a glass curtain wall screened by vertical fins, a brick base",
     "parts": [
         box(-4, 0, 20, 18, 13, "stone"),
         cyl(-14, 0, 8, 12, "stone"),
         box(8, 0, 8, 16, 14, "glass"),
         fins(10, -8, 4, 12, 6, 0.5, "grey"),
         box(-4, -9.2, 8, 0.6, 3, "warm"),
         wins(-4, -9, 6, 3, 2, 1, "glass", y0=6),
     ]},
    {"id": "kr_sasong_yangsan", "name": "Sasong church", "city": "Yangsan", "country": "Korea",
     "source": YBU, "year": 2025,
     "note": "a white box lifted on columns with a great dark glass upper wall, and a side tower of white fins",
     "parts": [
         box(2, 0, 26, 20, 10, "white", y0=5),
         band(4, -10, 20, 6, y0=9),
         box(2, 2, 20, 14, 5, "glass"),
         box(-10, -9, 1, 1, 5, "white"),
         box(14, -9, 1, 1, 5, "white"),
         box(-13, 0, 5, 14, 15, "white"),
         fins(-13, -7, 4, 14, 6, 0.3, "white"),
         box(-16, 0, 1.5, 12, 15, "glass"),
     ]},
    # ---- batch 3 ----------------------------------------------------------------------------------------
    {"id": "kr_gangseo_busan", "name": "Gangseo church", "city": "Busan", "country": "Korea",
     "source": YBU, "year": 2025,
     "note": "white stone blocks stepping up to a tall centre, two shafts of blue glass, narrow windows on the right",
     "parts": [
         box(-10, 0, 10, 16, 13, "white"),
         box(-1, 0, 8, 18, 18, "white"),
         band(-5, -9, 3, 15, y0=1),
         band(2.5, -9, 2.5, 17, y0=1),
         box(9, 0, 10, 16, 15, "white"),
         wins(9, -8, 8, 9, 4, 1, "glass", y0=4),
         wins(-10, -8, 6, 8, 2, 3, "glass", y0=2),
     ]},
    {"id": "kr_bukgu_ulsan", "name": "Buk-gu church", "city": "Ulsan", "country": "Korea",
     "source": YBU, "year": 2025,
     "note": "two grey stone wings with grids of windows round a broad stair, a glass bridge and a dark slot between",
     "parts": [
         box(-14, 0, 14, 18, 15, "stone"),
         wins(-14, -9, 12, 12, 4, 3, "glass", y0=1.5),
         box(-14, 0, 15, 19, 1.2, "white", y0=15),
         box(-5, 2, 4, 14, 16, "grey"),
         box(8, 4, 20, 16, 14, "stone"),
         wins(8, -4, 18, 10, 6, 3, "glass", y0=3),
         steps(-2, -10, 14, 8, 4, 10),
         canopy(4, -5, 10, 3, "grey", y0=4),
     ]},
    {"id": "kr_yullyang_cheongju", "name": "Yullyang church", "city": "Cheongju", "country": "Korea",
     "source": CHEONGJU, "year": 2024,
     "note": "a white tower with a long glass strip and a grey four storey block with rows of framed windows",
     "parts": [
         box(-8, 0, 8, 14, 17, "white"),
         band(-8, -7, 2, 15, y0=1),
         box(5, 1, 20, 14, 12, "grey"),
         wins(5, -6, 18, 9, 5, 3, "white", y0=3),
         canopy(5, 1, 21, 15, "glass", y0=12, h=0.6),
         box(5, 1, 20, 14, 2.5, "stone"),
     ]},
    {"id": "kr_seonghwa_cheongju", "name": "Seonghwa church", "city": "Cheongju", "country": "Korea",
     "source": CHEONGJU, "year": 2024,
     "note": "a long pale block with rows of tall narrow windows, a taller stair block with vertical glass strips",
     "parts": [
         box(-6, 2, 28, 16, 13, "pearl"),
         wins(-8, -6, 22, 7, 10, 1, "glass", y0=5),
         wins(-8, -6, 22, 3, 6, 1, "glass", y0=0.5),
         box(12, 0, 10, 18, 16, "pearl"),
         band(10, -9, 1.2, 15, y0=1),
         band(12.5, -9, 1.2, 15, y0=1),
         band(15, -9, 1.2, 15, y0=1),
     ]},
    {"id": "kr_seongjeong_cheonan", "name": "Seongjeong church", "city": "Cheonan", "country": "Korea",
     "source": CHEONAN, "year": 2024,
     "note": "a white block over a parking deck, its upper floors wrapped in a deep band of blue glass, thin glass "
             "slits below (named by the order of the post)",
     "parts": [
         box(0, 0, 30, 20, 4, "grey"),
         box(0, 0, 30, 20, 12, "white", y0=4),
         band(0, -10, 26, 6, y0=9),
         band(15, 0, 16, 6, y0=9, face="right"),
         wins(0, -10, 26, 4, 9, 1, "glass", y0=4.5),
         box(13, -6, 4, 6, 18, "white"),
     ]},
    {"id": "kr_asan_cheonan", "name": "Asan church", "city": "Asan", "country": "Korea",
     "source": CHEONAN, "year": 2024,
     "note": "a full height curtain wall of green glass held between two rounded glass towers and white stone wings "
             "(named by the order of the post)",
     "parts": [
         box(0, 0, 30, 18, 17, "white"),
         band(0, -9, 12, 15, "teal", y0=2),
         cyl(-8, -8, 4.5, 16, "glass"),
         cyl(8, -8, 4.5, 16, "glass"),
         box(-12.5, -6, 4, 8, 17, "white"),
         box(12.5, -6, 4, 8, 17, "white"),
         canopy(0, -11, 12, 3, "white", y0=3.5),
         steps(0, -14, 12, 3, 1.2, 4),
     ]},
    {"id": "kr_gwonseon_suwon", "name": "Gwonseon church", "city": "Suwon", "country": "Korea",
     "source": SUWON24, "year": 2024,
     "note": "a curved front of green glass in horizontal bands, with a white stone tower and a slim chimney like shaft",
     "parts": [
         box(-6, 4, 14, 14, 14, "white"),
         cyl(4, -2, 16, 10, "teal"),
         box(10, -6, 10, 10, 8, "glass"),
         canopy(4, -2, 17, 17, "white", y0=10, h=0.6),
         box(-9, 4, 3, 3, 22, "white"),
         wins(-6, -3, 10, 10, 3, 3, "glass", y0=2),
     ]},
    {"id": "kr_uiwang", "name": "Uiwang church", "city": "Uiwang", "country": "Korea",
     "source": UIWANG, "year": 2026,
     "note": "a campus of four long low white buildings under shallow brown roofs on a green hillside",
     "parts": [
         box(-10, 6, 34, 12, 6, "white"),
         gable(-10, 6, 35, 13, 1.5, "warm", y0=6, axis="x"),
         wins(-10, 0, 30, 3, 9, 1, "glass", y0=2),
         box(14, -8, 18, 12, 7, "white"),
         canopy(14, -8, 19, 13, "warm", y0=7, h=0.6),
         wins(14, -14, 16, 4, 6, 1, "glass", y0=1.5),
         box(-24, -8, 10, 8, 4, "white"),
         box(-4, -10, 6, 5, 3, "white"),
     ]},
    {"id": "kr_seongnam_jungang", "name": "Seongnam Jungang church", "city": "Seongnam", "country": "Korea",
     "source": UIWANG, "year": 2026,
     "note": "a five storey white block with a framed grey bay of blue glass jutting from its face, a tall glass strip",
     "parts": [
         box(0, 0, 18, 16, 18, "white"),
         box(3, -8.5, 10, 2, 6, "grey", y0=5),
         band(3, -9.6, 8, 4.5, y0=5.7),
         wins(3, -8, 10, 4, 3, 1, "glass", y0=13),
         band(-7, -8, 2.5, 18),
         box(-11, 2, 4, 12, 16, "glass"),
     ]},
    {"id": "kr_taejang_wonju", "name": "Taejang church", "city": "Wonju", "country": "Korea",
     "source": WONJU26, "year": 2026,
     "note": "a white stone cube with a full height bronze fin column and a glass slot, white wings stepping back",
     "parts": [
         box(-4, 0, 16, 16, 17, "white"),
         box(5, -6, 3, 4, 20, "warm"),
         band(7, -8, 1.2, 18),
         box(11, 2, 8, 14, 15, "white"),
         box(17, 4, 6, 10, 13, "white"),
         wins(-4, -8, 8, 1.5, 1, 1, "teal", y0=13),
     ]},
    {"id": "kr_jangjae_asan", "name": "Jangjae church", "city": "Asan", "country": "Korea",
     "source": ASAN23, "year": 2023,
     "note": "a tall white slab with a slim vertical glass line, a grey framed block with a glass base, white wings behind",
     "parts": [
         box(2, 0, 8, 14, 22, "white"),
         band(4, -7, 0.8, 20, y0=1),
         box(-8, -2, 12, 12, 11, "grey"),
         band(-8, -8, 11, 3, y0=0.5),
         box(10, 4, 10, 14, 15, "white"),
         wins(10, -3, 8, 10, 3, 4, "glass", y0=2),
     ]},
    {"id": "kr_dangjin", "name": "Dangjin church", "city": "Dangjin", "country": "Korea",
     "source": ASAN23, "year": 2023,
     "note": "a white block with a glass centre, a teal framed glass shaft and a brown stone wing",
     "parts": [
         box(-4, 0, 22, 18, 15, "white"),
         band(-2, -9, 8, 14, y0=1),
         wins(-11, -9, 6, 12, 3, 4, "glass", y0=2),
         box(7, -2, 4, 14, 16, "teal"),
         band(7, -9, 2.5, 14, y0=1),
         box(14, 2, 10, 14, 11, "warm"),
     ]},
    {"id": "kr_jangji_hwaseong", "name": "Jangji church", "city": "Hwaseong", "country": "Korea",
     "source": HWASEONG, "year": 2022,
     "note": "a glass block striped with dark grey fins over a brick base and brick wing, a grey cantilevered box on top",
     "parts": [
         box(-4, 0, 20, 16, 16, "glass"),
         fins(-4, -8, 18, 14, 5, 1.0, "grey", y0=2),
         box(-4, -8.5, 22, 1, 3, "warm"),
         box(10, 2, 10, 14, 11, "warm"),
         box(10, 2, 12, 10, 3, "grey", y0=11),
         box(-16, 2, 4, 12, 17, "grey"),
     ]},
    {"id": "kr_janghowon_icheon", "name": "Janghowon church", "city": "Icheon", "country": "Korea",
     "source": HWASEONG, "year": 2022,
     "note": "a long two storey hall striped with brown piers, behind a courtyard, and a taller white block with fins",
     "parts": [
         box(-6, 4, 36, 14, 8, "white"),
         fins(-6, -3, 34, 8, 14, 0.5, "warm"),
         box(16, 0, 8, 16, 11, "white"),
         fins(16, -8, 6, 10, 3, 0.8, "stone"),
         band(10, -4, 4, 4, y0=0.5),
     ]},
    {"id": "kr_dalseong_daegu", "name": "Dalseong church", "city": "Daegu", "country": "Korea",
     "source": JINJU, "year": 2023,
     "note": "a white tower with a dark glass slit beside a glass block topped by a pitched glass roof, a dark entrance porch",
     "parts": [
         box(8, 2, 10, 16, 20, "white"),
         band(4, -6, 1.2, 18, y0=1),
         box(-6, 0, 18, 16, 12, "glass"),
         gable(-6, 0, 18, 16, 3, "glass", y0=12, axis="x"),
         box(-4, -9, 8, 3, 4, "grey"),
         steps(-4, -12, 8, 3, 1.2, 4),
     ]},
    # ---- batch 4 (english.watv.org dedication posts, each photograph captioned with its church) -------------
    {"id": "kr_boseong", "name": "Boseong church", "city": "Boseong", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "a brick hall with arched windows and a tall brick tower whose top sweeps up to a point, a round window high up",
     "parts": [
         box(-6, 0, 24, 18, 9, "warm"),
         arches(-8, -9, 14, 6, 4, 1, "glass", y0=1),
         box(8, -2, 8, 8, 22, "warm"),
         gable(8, -2, 8, 8, 5, "warm", y0=22, axis="z"),
         disc(8, -6, 2, "glass", y0=19),
         band(10, -6, 1, 10, "teal", y0=7),
         arches(6, -6, 3, 5, 1, 1, "glass"),
     ]},
    {"id": "kr_gimje", "name": "Gimje church", "city": "Gimje", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "a curved block of dark blue glass, a glass tower capped in red, and a white wing of narrow windows",
     "parts": [
         cyl(-8, -2, 12, 11, "glass"),
         box(1, 0, 6, 10, 20, "glass"),
         box(1, 0, 7, 11, 1, "rose", y0=20),
         box(10, 0, 12, 16, 15, "white"),
         wins(10, -8, 10, 12, 4, 4, "glass", y0=1.5),
         canopy(-2, -8, 8, 3, "rose", y0=3),
         steps(-2, -11, 10, 4, 1.5, 5),
     ]},
    {"id": "kr_nonsan", "name": "Nonsan church", "city": "Nonsan", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "a long white three storey block with bands of blue windows and a slender white tower with a rounded top",
     "parts": [
         box(4, 0, 30, 16, 10, "white"),
         box(8, 2, 16, 12, 4, "white", y0=10),
         wins(4, -8, 28, 3, 10, 1, "glass", y0=6),
         band(4, -8, 28, 2.5, y0=0.5),
         box(-9, -4, 3, 3, 24, "white"),
         dome(-9, -4, 3, 1.5, "white", y0=24),
     ]},
    {"id": "kr_donggu_daejeon", "name": "Donggu church", "city": "Daejeon", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "a long brick hall of tall round arched windows and an open brick bell tower crowned with glass",
     "parts": [
         box(-4, 0, 34, 18, 11, "warm"),
         canopy(-4, 0, 35, 19, "glass", y0=11, h=0.4),
         arches(-6, -9, 28, 8, 8, 1, "glass", y0=2),
         box(14, -6, 4, 4, 22, "warm"),
         box(14, -6, 4, 4, 3, "glass", y0=22),
     ]},
    {"id": "kr_sannae_daejeon", "name": "Sannae church", "city": "Daejeon", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "a three storey brick block with long ribbon windows under a blue tiled hipped roof",
     "parts": [
         box(0, 0, 26, 14, 11, "warm"),
         band(0, -7, 22, 2, y0=4),
         band(0, -7, 22, 2, y0=7.5),
         band(0, -7, 14, 2, y0=0.8),
         hip(0, 0, 28, 16, 3, "glass", y0=11),
     ]},
    {"id": "kr_hoideok_daejeon", "name": "Hoideok church", "city": "Daejeon", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "white and glass floors stepping back in terraces up a slope, with a dark slim tower at the corner",
     "parts": [
         box(0, 0, 30, 18, 5, "white"),
         canopy(0, 0, 31, 19, "white", y0=5),
         box(2, 1, 26, 14, 4, "glass", y0=5),
         canopy(2, 1, 27, 15, "white", y0=9),
         box(4, 2, 18, 10, 4, "white", y0=9),
         box(12, -2, 4, 4, 17, "grey"),
     ]},
    {"id": "kr_eoyang_iksan", "name": "Eoyang church", "city": "Iksan", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "red brick blocks with a round arched glass entrance and a tall white blade tower with a slanted top",
     "parts": [
         box(0, 0, 22, 16, 10, "warm"),
         box(-4, -8, 10, 6, 8, "warm"),
         arches(-4, -11, 6, 6, 1, 1, "glass"),
         box(3, -6, 3, 2, 22, "white"),
         spire(3, -6, 3, 4, "white", y0=22),
     ]},
    {"id": "kr_gwangyang", "name": "Gwangyang church", "city": "Gwangyang", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "a grey stone four storey block with an outside stair and a round glass tower at the corner",
     "parts": [
         box(-2, 0, 24, 16, 15, "stone"),
         wins(-4, -8, 18, 12, 4, 4, "glass", y0=2),
         cyl(11, -6, 5, 17, "glass"),
         steps(-2, -10, 4, 4, 8, 10, "stone"),
     ]},
    {"id": "kr_seosin_jeonju", "name": "Seosin church", "city": "Jeonju", "country": "Korea",
     "source": EN + "37845", "year": 2015,
     "note": "a cream two storey hall under a broad brown hipped roof with a small white gabled porch",
     "parts": [
         box(2, 0, 24, 18, 8, "warm"),
         hip(2, 0, 25, 19, 4, "grey", y0=8),
         box(-12, 2, 8, 14, 9, "warm"),
         wins(-12, -5, 6, 6, 2, 2, "glass", y0=1.5),
         box(4, -10, 6, 3, 4, "white"),
         gable(4, -10, 7, 3, 1.5, "grey", y0=4, axis="z"),
     ]},
    {"id": "kr_jungang_pohang", "name": "Jungang church", "city": "Pohang", "country": "Korea",
     "source": EN + "38366", "year": 2015,
     "note": "a pale stone front with three tall round arched glass windows, a white blade tower, an arcade along the side",
     "parts": [
         box(0, 0, 22, 20, 14, "stone"),
         arches(-2, -10, 12, 11, 3, 1, "glass", y0=1),
         box(-8, -6, 3, 2, 28, "white"),
         arches(11, 0, 16, 8, 6, 1, "white", face="right"),
         canopy(-2, -11, 14, 2, "white", y0=3),
     ]},
    {"id": "kr_doryang_gumi", "name": "Doryang church", "city": "Gumi", "country": "Korea",
     "source": EN + "38366", "year": 2015,
     "note": "a five storey block with a rounded end, wrapped in alternating bands of white and green glass",
     "parts": [
         box(-4, 0, 24, 16, 16, "white"),
         cyl(8, 0, 16, 16, "white"),
         band(-4, -8, 22, 2, "teal", y0=4),
         band(-4, -8, 22, 2, "teal", y0=8),
         band(-4, -8, 22, 2, "teal", y0=12),
         canopy(1, 0, 30, 18, "grey", y0=16, h=0.5),
     ]},
    {"id": "kr_andong", "name": "Andong church", "city": "Andong", "country": "Korea",
     "source": EN + "38366", "year": 2015,
     "note": "a white four storey block with a wide blue glass curtain wall and a round glass corner tower",
     "parts": [
         box(0, 0, 26, 16, 15, "white"),
         band(2, -8, 16, 11, y0=2),
         cyl(-12, -5, 5, 15, "glass"),
         canopy(2, -2, 18, 10, "white", y0=15, h=0.6),
     ]},
    {"id": "kr_geochang", "name": "Geochang church", "city": "Geochang", "country": "Korea",
     "source": EN + "38366", "year": 2015,
     "note": "cream walls with arched windows and a central glass hall under a steep green gable roof",
     "parts": [
         box(2, 0, 28, 18, 8, "pearl"),
         arches(10, -9, 10, 4, 3, 1, "glass", y0=3),
         box(-2, -2, 10, 14, 10, "glass"),
         gable(-2, -2, 11, 15, 5, "teal", y0=10, axis="z"),
         box(-16, 4, 10, 10, 6, "pearl"),
         hip(-16, 4, 11, 11, 2.5, "grey", y0=6),
         box(-4, -10, 8, 2, 4, "white"),
     ]},
    {"id": "kr_hongseong", "name": "Hongseong church", "city": "Hongseong", "country": "Korea",
     "source": EN + "41443", "year": 2016,
     "note": "a white classical block with two rows of round arched windows, a cornice and a taller pedimented corner",
     "parts": [
         box(2, 0, 26, 16, 14, "white"),
         arches(5, -8, 20, 10, 6, 2, "glass", y0=3),
         box(-13, 0, 6, 16, 18, "white"),
         gable(-13, 0, 6, 16, 2, "white", y0=18, axis="x"),
         canopy(2, -8, 27, 1.5, "white", y0=14, h=0.6),
         arches(-6, -8, 4, 4, 1, 1, "glass"),
     ]},
    {"id": "kr_yeoju", "name": "Yeoju church", "city": "Yeoju", "country": "Korea",
     "source": EN + "41917", "year": 2016,
     "note": "a long white two storey building, its entrance end framed by a magenta band",
     "parts": [
         box(0, 0, 32, 14, 9, "white"),
         box(6, -7.4, 14, 0.8, 9, "rose"),
         wins(-8, -7, 14, 7, 7, 2, "glass", y0=1),
         wins(6, -8, 12, 5, 4, 2, "glass", y0=2),
         box(18, 0, 4, 12, 6, "white"),
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


assert len({b["id"] for b in BUILDINGS}) == len(BUILDINGS), "duplicate building id"


def all_buildings():
    return BUILDINGS
