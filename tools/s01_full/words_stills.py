"""Low-resolution stills of song 01's words over the approved Revision 3 look (lane WORDS check tool).

Renders the R3 world (tools/nine_colours_minor, pinned engine d928ff9) with its own nine expressions and
their symbols taken out, and the song 01 words of tools/s01_full/words.py put in, evaluated at SONG time.
Each still picks an R3 film moment as the background and a sky look close to the song's light at that
time (night lake, blue hour, sunrise). Also writes a quarter-size copy of each still, to judge reading
from the back of a hall.

    python tools/nine_colours_minor/prepare.py            # once
    python tools/s01_full/words_stills.py --outdir <dir> [--times 40,46,56,64,119,150,166,176] [--scale .5]

Never commit the stills. Cloud only. No em dash or en dash anywhere in this file.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_TIMES = "40,46,56,64,119,150,166,176"

# song time range -> (R3 film clock for the background, sky look)
BACKGROUND = [
    (0.0, 110.0, 3.5, "night"),
    (110.0, 140.0, 24.0, "bluehour"),
    (140.0, 999.0, 44.0, "sunrise"),
]
LOOKS = {
    "bluehour": dict(base="night", sky_top="#1b2558", sky_mid="#44508f", sky_hor="#9a8fc0", stars=.35,
                     milky=.2, mist=.22, mist_color="#5a5f9a", haze=.12, haze_color="#6d6aa8"),
    "sunrise": dict(base="day", sun_az=180.0, sun_el=6.0, sun_int=.9, sun_glow=.8, mist=.22, rays=.3,
                    sky_top="#7fa6d6", sky_mid="#f2c79a", sky_hor="#ffcf8a"),
}


def background(ts):
    for a, b, clock, look in BACKGROUND:
        if a <= ts < b:
            return clock, look
    return BACKGROUND[-1][2:]


class Shift:
    value = 0.0


class LayoutCamera:
    """The R3 camera seen through song time: song time ts shows the film clock ts - shift."""

    def __init__(self, rig):
        self.rig = rig

    def state(self, ts, aspect=16.0 / 9.0):
        return self.rig.state(ts - Shift.value, aspect)


class Proxy:
    """One scene entry: the song words sampled at song time = film clock + shift."""
    wants_camera = True

    def __init__(self, words):
        self.words = words

    def sample(self, t, cam=None):
        out = []
        for w in self.words:
            out += w.sample(t + Shift.value, cam) or []
        return out


class ShiftedBoxes:
    def __init__(self, words):
        self.words = words

    def boxes(self, t, cam=None):
        return self.words.boxes(t + Shift.value, cam)


def render_group(look, items, outdir, scale):
    sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
    sys.path.insert(0, str(HERE))
    import render as r3
    Renderer, film = r3.load()
    import song
    import words as S01W
    camera = LayoutCamera(film.P3D["camera"])
    Shift.value = items[0][0] - items[0][1]
    WORDS = S01W.build(camera)
    old_setup = film.P3D["setup"]

    def setup(scene):
        old_setup(scene)
        for name in list(scene.names()):
            if name.startswith("word ") or name.startswith("addition symbol"):
                scene.remove(name)
        for e in scene.entries():
            if e.name in ("comets", "hoops", "lanterns"):
                inner = getattr(e.pointset, "inner", e.pointset)
                e.pointset = S01W._Clear(inner, ShiftedBoxes(WORDS))
        scene.add("s01 words", Proxy(WORDS), reflect=False, depth_of_field=True)

    world = dict(film.P3D["world"])
    if look != "night":
        world["looks"] = dict(world["looks"], **{look: LOOKS[look]})
        world["look"] = [(0.0, look)]
    film.P3D = dict(film.P3D, setup=setup, world=world)
    song.P3D = film.P3D
    w, h = int(1920 * scale) // 2 * 2, int(1080 * scale) // 2 * 2
    renderer = Renderer(w, h)
    from PIL import Image
    report = []
    for ts, clock in items:
        Shift.value = ts - clock
        start = time.process_time()
        data = renderer.out.frame(clock, int(round(clock * 60)))
        img = Image.frombytes("RGB", (w, h), data)
        name = f"s{int(ts // 60)}m{ts % 60:04.1f}"
        img.save(outdir / f"{name}.png")
        img.resize((w // 4, h // 4), Image.LANCZOS).save(outdir / f"{name}-quarter.png")
        boxes = WORDS.boxes(ts, camera.state(ts))
        report.append(dict(song_time=ts, film_clock=clock, look=look, active=WORDS.active(ts),
                           boxes=[[round(v, 3) for v in b] for b in boxes]))
        print(f"{ts:.1f} ({look}, film {clock}): {time.process_time() - start:.1f} CPU s", flush=True)
    (outdir / f"report-{look}.json").write_text(json.dumps(report, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--times", default=DEFAULT_TIMES)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--scale", type=float, default=.5)
    ap.add_argument("--group", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    times = [float(v) for v in args.times.split(",")]
    groups = {}
    for ts in times:
        clock, look = background(ts)
        groups.setdefault(look, []).append((ts, clock))
    if args.group:
        render_group(args.group, groups[args.group], args.outdir, args.scale)
        return
    # one fresh process per sky look (each builds its own renderer and world)
    procs = [subprocess.Popen([sys.executable, __file__, "--times", args.times, "--outdir", str(args.outdir),
                               "--scale", str(args.scale), "--group", look]) for look in groups]
    if any(p.wait() for p in procs):
        raise SystemExit("a still group failed")


if __name__ == "__main__":
    main()
