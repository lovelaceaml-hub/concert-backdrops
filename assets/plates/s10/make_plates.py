"""Paints the song 10 plate "peace across the world" (earth_web.jpg) from code.

No image tool is available in the cloud run, so this plate is drawn here: the curve of the night Earth seen from
high above, deep midnight blue, a deep gold line of light along its edge like a dawn that has not yet come, the
great lamp resting at the exact centre of that edge, warm lights of people scattered across the dark side and a
web of thin gold paths joining them to the lamp (the words passed on from person to person). The bottom third
stays dark and calm for the performers. No text, no people.

Run: python3 assets/plates/s10/make_plates.py   (writes assets/plates/s10/earth_web.jpg, about 0.5 MB)
"""
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

W, H = 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))


def lin(hexs):
    h = hexs.lstrip("#")
    return (np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0) ** 2.2


def value_noise(shape, cells, seed):
    r = np.random.default_rng(seed).random((cells[0] + 3, cells[1] + 3))
    y = np.linspace(0, cells[0], shape[0], endpoint=False)
    x = np.linspace(0, cells[1], shape[1], endpoint=False)
    yi, xi = np.floor(y).astype(int), np.floor(x).astype(int)
    fy, fx = y - yi, x - xi
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = r[yi][:, xi] * (1 - fx) + r[yi][:, xi + 1] * fx
    b = r[yi + 1][:, xi] * (1 - fx) + r[yi + 1][:, xi + 1] * fx
    return a * (1 - fy)[:, None] + b * fy[:, None]


def main():
    rng = np.random.default_rng(10)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    img = np.zeros((H, W, 3))

    # space above the Earth: midnight blue, darker at the top
    v = yy / H
    img += lin("#01030b") * (1 - v)[..., None] + lin("#081233") * v[..., None]

    # quiet stars in the space above
    n = 900
    sx, sy = rng.random(n) * W, rng.random(n) ** 1.6 * 560
    sb = rng.random(n) ** 3.0
    star = np.zeros((H, W))
    star[sy.astype(int).clip(0, H - 1), sx.astype(int).clip(0, W - 1)] = 0.15 + 0.85 * sb
    star = ndi.gaussian_filter(star, 0.8) * 5.0
    img += star[..., None] * lin("#dfe6ff")[None, None, :] * 0.6

    # the Earth: a huge circle whose top edge is at y = 560 at the centre
    R = 2600.0
    cx, cy = W / 2.0, 560.0 + R
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    inside = d <= R
    depth = np.clip((R - d) / 520.0, 0.0, 1.0)            # 0 at the edge, 1 deep inside
    land = value_noise((H, W), (9, 16), 3) * 0.6 + value_noise((H, W), (27, 48), 4) * 0.4
    surf = lin("#040920") * (0.70 + 0.5 * land)[..., None] + lin("#0e1c44") * ((1 - depth) ** 3)[..., None]
    surf *= (1.0 - 0.45 * np.clip((yy - 700) / 380, 0, 1))[..., None]   # darker towards the bottom (calm)
    img = np.where(inside[..., None], surf, img)

    # the deep gold line of light along the edge: strongest at the centre (where the lamp rests)
    ang = np.arctan2(xx - cx, cy - yy)                    # 0 straight up from the centre
    centre = np.exp(-(ang / 0.22) ** 2)
    edge_d = d - R                                       # >0 outside, <0 inside
    rim = np.exp(-np.abs(edge_d) / 3.0) * 0.9
    glow_out = np.exp(-np.clip(edge_d, 0, None) / 38.0) * (edge_d > 0)
    glow_out2 = np.exp(-np.clip(edge_d, 0, None) / 160.0) * (edge_d > 0)
    glow_in = np.exp(-np.clip(-edge_d, 0, None) / 70.0) * (edge_d <= 0)
    gold = lin("#ffcd63")
    deep = lin("#ff9a3c")
    k = 0.30 + 0.70 * centre
    img += gold * (rim * (0.35 + 0.65 * k))[..., None]
    img += deep * (glow_out * 0.35 * k + glow_out2 * 0.07 * centre)[..., None]
    img += lin("#6a4a3a") * (glow_in * 0.30 * k)[..., None]

    # the great lamp at the exact centre of the edge
    ld = np.sqrt((xx - cx) ** 2 + (yy - 560.0) ** 2)
    img += lin("#fff1cf") * (np.exp(-(ld / 9.0) ** 2) * 2.2)[..., None]
    img += lin("#ffbf4f") * (np.exp(-ld / 60.0) * 0.55 + np.exp(-ld / 240.0) * 0.18)[..., None]

    # warm lights of people across the dark side, in loose clusters, dimmer in the lower third
    pts = []
    for c in range(60):
        a = rng.uniform(-0.40, 0.40)
        dd = R - 25 - rng.random() ** 1.1 * 560
        px, py = cx + dd * np.sin(a), cy - dd * np.cos(a)
        if not (40 < px < W - 40 and 570 < py < H - 20):
            continue
        m = rng.integers(6, 26)
        spread = 6 + 26 * rng.random()
        for _ in range(m):
            qx, qy = px + rng.normal(0, spread), py + rng.normal(0, spread * 0.45)
            pts.append((qx, qy, 0.3 + 0.7 * rng.random() ** 2))
        pts.append((px, py, 1.4))
    city = np.zeros((H, W))
    for qx, qy, b in pts:
        ix, iy = int(qx), int(qy)
        if 0 <= ix < W and 0 <= iy < H:
            city[iy, ix] += b
    city = ndi.gaussian_filter(city, 1.1) * 7.0 + ndi.gaussian_filter(city, 6.0) * 6.0
    calm = 1.0 - 0.82 * np.clip((yy - 700) / 120, 0, 1)
    img += lin("#ffb066") * (city * calm * inside)[..., None]

    # a web of thin gold paths: from the lamp out to the clusters, and between neighbours
    hubs = [(x, y) for x, y, b in pts if b > 1.0 and y < 790]
    web = np.zeros((H, W))

    def arc(p0, p1, sag, w):
        tt = np.linspace(0.0, 1.0, 900)
        mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0 + sag
        bx = (1 - tt) ** 2 * p0[0] + 2 * (1 - tt) * tt * mx + tt ** 2 * p1[0]
        by = (1 - tt) ** 2 * p0[1] + 2 * (1 - tt) * tt * my + tt ** 2 * p1[1]
        ix, iy = bx.astype(int), by.astype(int)
        ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        np.add.at(web, (iy[ok], ix[ok]), w)

    for hx, hy in hubs:
        arc((cx, 562.0), (hx, hy), 25 + 30 * rng.random(), 0.20)
    for i, (hx, hy) in enumerate(hubs):
        dist = [((hx - x2) ** 2 + (hy - y2) ** 2, j) for j, (x2, y2) in enumerate(hubs) if j != i]
        for _, j in sorted(dist)[:2]:
            arc((hx, hy), hubs[j], 8, 0.15)
    web = np.clip(ndi.gaussian_filter(web, 0.9) * 3.0, 0, 1.0) + ndi.gaussian_filter(web, 4.0) * 1.2
    web *= np.clip((790 - yy) / 70, 0, 1)                 # keep the paths out of the lower third
    img += lin("#ffd99a") * (web * 0.42)[..., None]

    out = np.clip(img, 0, 1) ** (1 / 2.2)
    out = (out * 255 + rng.random(out.shape) * 1.0).clip(0, 255).astype(np.uint8)   # a little dither
    Image.fromarray(out).save(os.path.join(HERE, "earth_web.jpg"), quality=88)


if __name__ == "__main__":
    main()
