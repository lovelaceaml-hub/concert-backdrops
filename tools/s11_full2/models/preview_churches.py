"""Contact sheet of the modelled churches (wmscog_churches.py) as simple line drawings, front three-quarter view,
one building per cell with its name and city under it, all at one scale. No em dash or en dash in this file.

  python3 tools/s11_full2/models/preview_churches.py OUT.png [first_index] [count]
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmscog_churches import all_buildings  # noqa: E402

COL = {"pearl": (230, 237, 255), "white": (250, 250, 250), "glass": (122, 184, 255), "teal": (98, 226, 210),
       "gold": (255, 206, 90), "rose": (255, 150, 170), "warm": (255, 212, 154), "stone": (200, 196, 186),
       "grey": (150, 158, 172)}
YAW = math.radians(-32)
ELEV = math.radians(18)


def proj(x, y, z):
    xr = x * math.cos(YAW) - z * math.sin(YAW)
    zr = x * math.sin(YAW) + z * math.cos(YAW)
    return xr, y * math.cos(ELEV) + zr * math.sin(ELEV)


def rot_local(p, u, v):
    """local offset (u along x, v along z) of a part, turned by its rot, to world x, z"""
    a = math.radians(p.get("rot", 0))
    return p["x"] + u * math.cos(a) - v * math.sin(a), p["z"] + u * math.sin(a) + v * math.cos(a)


def face_pt(p, u, y):
    f = p.get("face", "front")
    x, z = p["x"], p["z"]
    if f == "front":
        return x + u, y, z
    if f == "back":
        return x - u, y, z
    if f == "left":
        return x, y, z - u
    return x, y, z + u


def segments(p):
    """3D line segments for one part"""
    k, y0, w, d, h = p["kind"], p["y0"], p.get("w", 0), p.get("d", 0), p.get("h", 0)
    S = []

    def corners(hw, hd):
        return [rot_local(p, sx * hw, sz * hd) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]

    if k in ("box", "canopy"):
        c = corners(w / 2, d / 2)
        for i in range(4):
            a, b = c[i], c[(i + 1) % 4]
            S += [((a[0], y0, a[1]), (b[0], y0, b[1])), ((a[0], y0 + h, a[1]), (b[0], y0 + h, b[1])),
                  ((a[0], y0, a[1]), (a[0], y0 + h, a[1]))]
    elif k == "steps":
        n = p.get("n", 6)
        for i in range(n + 1):
            zz = -d / 2 + d * i / n
            yy = y0 + h * min(i + 1, n) / n
            a, b = rot_local(p, -w / 2, zz), rot_local(p, w / 2, zz)
            S.append(((a[0], yy, a[1]), (b[0], yy, b[1])))
        a, b = rot_local(p, -w / 2, -d / 2), rot_local(p, -w / 2, d / 2)
        S.append(((a[0], y0, a[1]), (b[0], y0 + h, b[1])))
    elif k in ("cyl", "dome"):
        r = w / 2
        n = 28
        rings = [y0, y0 + h] if k == "cyl" else [y0 + h * math.sin(math.pi / 2 * j / 4) for j in range(5)]
        for j, yy in enumerate(rings):
            rr = r if k == "cyl" else r * math.cos(math.pi / 2 * j / 4)
            pts = [(p["x"] + rr * math.cos(2 * math.pi * i / n), yy, p["z"] + rr * math.sin(2 * math.pi * i / n))
                   for i in range(n + 1)]
            S += list(zip(pts[:-1], pts[1:]))
        if k == "cyl":
            for ang in (0, math.pi / 2, math.pi, 3 * math.pi / 2, math.pi * 1.25, math.pi * 1.75):
                xx, zz = p["x"] + r * math.cos(ang), p["z"] + r * math.sin(ang)
                S.append(((xx, y0, zz), (xx, y0 + h, zz)))
        else:
            for ang in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
                pts = [(p["x"] + r * math.cos(t) * math.cos(ang), y0 + h * math.sin(t), p["z"] + r * math.cos(t) * math.sin(ang))
                       for t in [math.pi / 2 * i / 8 for i in range(9)]]
                S += list(zip(pts[:-1], pts[1:]))
    elif k in ("gable", "hip", "spire"):
        c = corners(w / 2, d / 2)
        base = [(a[0], y0, a[1]) for a in c]
        for i in range(4):
            S.append((base[i], base[(i + 1) % 4]))
        if k == "spire":
            top = (p["x"], y0 + h, p["z"])
            S += [(b, top) for b in base]
        else:
            along_x = p.get("axis", "x") == "x" if k == "gable" else w >= d
            inset = 0 if k == "gable" else min(w, d) / 2
            if along_x:
                r1, r2 = rot_local(p, -w / 2 + inset, 0), rot_local(p, w / 2 - inset, 0)
            else:
                r1, r2 = rot_local(p, 0, -d / 2 + inset), rot_local(p, 0, d / 2 - inset)
            t1, t2 = (r1[0], y0 + h, r1[1]), (r2[0], y0 + h, r2[1])
            S.append((t1, t2))
            if along_x:
                S += [(base[0], t1), (base[3], t1), (base[1], t2), (base[2], t2)]
            else:
                S += [(base[0], t1), (base[1], t1), (base[3], t2), (base[2], t2)]
    elif k in ("windows", "arch_windows"):
        n, rows = p.get("n", 1), p.get("rows", 1)
        cw, ch = w / n, h / rows
        ww, wh = cw * 0.62, ch * 0.72
        for i in range(n):
            for j in range(rows):
                u0 = -w / 2 + cw * (i + 0.5)
                v0 = y0 + ch * (j + 0.5)
                if k == "windows":
                    q = [(u0 - ww / 2, v0 - wh / 2), (u0 + ww / 2, v0 - wh / 2), (u0 + ww / 2, v0 + wh / 2),
                         (u0 - ww / 2, v0 + wh / 2), (u0 - ww / 2, v0 - wh / 2)]
                else:
                    r = ww / 2
                    top = v0 + wh / 2 - r
                    q = [(u0 - r, top), (u0 - r, v0 - wh / 2), (u0 + r, v0 - wh / 2), (u0 + r, top)]
                    q += [(u0 + r * math.cos(math.pi * t / 10), top + r * math.sin(math.pi * t / 10)) for t in range(11)]
                pts = [face_pt(p, u, v) for u, v in q]
                S += list(zip(pts[:-1], pts[1:]))
    elif k == "glass_band":
        sh = math.tan(math.radians(p.get("angle", 0))) * h
        q = [(-w / 2, y0), (w / 2, y0), (w / 2 + sh, y0 + h), (-w / 2 + sh, y0 + h), (-w / 2, y0)]
        pts = [face_pt(p, u, v) for u, v in q]
        S += list(zip(pts[:-1], pts[1:]))
        for i in range(1, 4):
            u = -w / 2 + w * i / 4
            S.append((face_pt(p, u, y0), face_pt(p, u + sh, y0 + h)))
    elif k == "fin_row":
        n = p.get("n", 5)
        f = p.get("face", "front")
        out = {"front": (0, -1), "back": (0, 1), "left": (-1, 0), "right": (1, 0)}[f]
        for i in range(n):
            u = -w / 2 + w * (i + 0.5) / n
            a = face_pt(p, u, y0)
            b = face_pt(p, u, y0 + h)
            a2 = (a[0] + out[0] * d, a[1], a[2] + out[1] * d)
            b2 = (b[0] + out[0] * d, b[1], b[2] + out[1] * d)
            S += [(a, b), (a2, b2), (b, b2)]
    elif k == "disc":
        r = w / 2
        pts = [face_pt(p, r * math.cos(2 * math.pi * i / 24), y0 + r * math.sin(2 * math.pi * i / 24)) for i in range(25)]
        S += list(zip(pts[:-1], pts[1:]))
    elif k == "cross":
        S += [((p["x"], y0, p["z"]), (p["x"], y0 + h, p["z"])),
              ((p["x"] - w / 2, y0 + h * 0.7, p["z"]), (p["x"] + w / 2, y0 + h * 0.7, p["z"]))]
    return S


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "churches_sheet.png"
    blds = all_buildings()
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    count = int(sys.argv[3]) if len(sys.argv) > 3 else len(blds) - first
    blds = blds[first:first + count]
    cols = 5
    cw, chh = 400, 340
    rows = (len(blds) + cols - 1) // cols
    img = Image.new("RGB", (cols * cw, rows * chh + 40), (10, 14, 32))
    dr = ImageDraw.Draw(img)
    dr.text((12, 12), f"World Mission Society Church of God buildings, modelled in parts ({first + 1} to "
                      f"{first + len(blds)}); one scale; front three-quarter view", fill=(200, 210, 240))
    segs_all = [[(proj(*a), proj(*b), COL.get(p["col"], (255, 255, 255))) for p in b_["parts"] for a, b in segments(p)]
                for b_ in blds]
    span = 0
    for segs in segs_all:
        xs = [q[0] for s in segs for q in s[:2]]
        ys = [q[1] for s in segs for q in s[:2]]
        span = max(span, (max(xs) - min(xs)) / (cw - 40), (max(ys) - min(ys)) / (chh - 80))
    sc = 1.0 / span
    for i, (b_, segs) in enumerate(zip(blds, segs_all)):
        ox, oy = (i % cols) * cw, (i // cols) * chh + 40
        xs = [q[0] for s in segs for q in s[:2]]
        ymin = min(q[1] for s in segs for q in s[:2])
        cx = (max(xs) + min(xs)) / 2
        base_y = oy + chh - 62
        dr.line([(ox + 20, base_y + 4), (ox + cw - 20, base_y + 4)], fill=(40, 50, 80))
        for a, bb, c in segs:
            dr.line([(ox + cw / 2 + (a[0] - cx) * sc, base_y - (a[1] - ymin) * sc),
                     (ox + cw / 2 + (bb[0] - cx) * sc, base_y - (bb[1] - ymin) * sc)], fill=c, width=1)
        sz = b_["size"]
        dr.text((ox + 14, base_y + 12), f"{first + i + 1}. {b_['name']}", fill=(255, 255, 255))
        dr.text((ox + 14, base_y + 28), f"{b_['city']}, {b_['country']}  {b_['year'] or ''}  "
                                        f"{sz[0]:.0f} x {sz[1]:.0f} x {sz[2]:.0f} m", fill=(170, 180, 210))
    img.save(out)
    print(out, len(blds))


if __name__ == "__main__":
    main()
