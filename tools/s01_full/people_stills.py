"""Low-resolution stills of the people of song 01 (tools/s01_full/people.py) over the approved Revision 3 look.

    python tools/nine_colours_minor/prepare.py          # once: the pinned engine and Claude Final v1 snapshots
    python tools/s01_full/people_stills.py --scale 0.5 --outdir work/s01_people_stills
    python tools/s01_full/people_stills.py --times 46,50 --scale 0.5

The world, camera and words belong to the lead's song module; this file only stands in for them so each
moment of the people can be checked: a night lake that turns golden, a calm camera per moment, no words (the
reading areas of the Compliment and Encouragement words are outlined faintly with --guides). Stills are
written under work/ (untracked). Never commit them.
"""
import argparse
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "tools/nine_colours_minor"), str(HERE)]

TIMES = (30.0, 46.0, 50.0, 70.0, 100.0, 160.0, 168.0, 195.0)


def shots(stage, people):
    """A calm camera for each still, in the stage's local metres: (camera place, look at, fov)."""
    st = stage
    wide = (st.point(0.4, 2.3, 13.5), st.point(0.6, 1.0, -0.8), 40.0)
    return {
        30.0: wide,
        46.0: (st.point(0.15, 1.45, 8.4), st.point(0.15, 1.1, 3.2), 32.0),
        50.0: (st.point(0.15, 1.45, 8.4), st.point(0.15, 1.1, 3.2), 32.0),
        70.0: (st.point(1.2, 2.2, 12.5), st.point(1.4, 1.1, -0.8), 44.0),
        100.0: (st.point(0.0, 3.0, 12.0), st.point(0.0, 0.9, -4.0), 46.0),
        160.0: (st.point(0.0, 1.45, 8.4), st.point(0.0, 0.9, 3.2), 32.0),
        168.0: (st.point(0.0, 1.45, 8.4), st.point(0.0, 0.9, 3.2), 32.0),
        195.0: wide,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--times", default=",".join(str(t) for t in TIMES))
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--outdir", type=Path, default=ROOT / "work/s01_people_stills")
    ap.add_argument("--guides", action="store_true", help="outline the words' reading area")
    args = ap.parse_args()
    times = [float(x) for x in args.times.split(",")]

    import render
    Renderer, film = render.load()
    import song
    import people
    from p3d.camera import Rig, hold

    stage = people.Stage(at=(0.0, 0.0), view=0.0)
    cast = people.build(stage)
    table = shots(stage, cast)
    moves = []
    for t in sorted(times):
        pos, look, fov = table.get(t) or table[min(table, key=lambda k: abs(k - t))]
        moves.append(hold(tuple(pos), tuple(look), t - 0.6, t + 0.6, blend=0.0, fov=fov))
    rig = Rig(moves, blend=0.0, fov=40.0, aperture=0.0, handheld=0.0)
    looks = dict(film.LOOKS)
    looks["sunrise"] = dict(base="dusk", sky_top="#141c4a", sky_mid="#4a2c5c", sky_hor="#d0784e",
                            sun_az=180.0, sun_el=2.0, sun_int=0.6, sun_glow=0.6, mist=0.08, mist_color="#5a3040",
                            haze=0.1, haze_color="#3a2038")
    world = dict(looks=looks, look=[(0.0, "floor"), (75.0, "prayer", 6.0), (118.0, "drop", 8.0),
                                    (150.0, "sunrise", 10.0)],
                 light=dict(pos=(0.0, 30.0, -200.0), color="#fff1d8", strength=0.0, size=0.5, rays=0.0),
                 lights=cast.lights(), react=dict(beat=0.0, level=0.0))

    def setup(scene):
        cast.add(scene)

    song.P3D = dict(camera=rig, world=world, setup=setup, bursts=[], motion_blur=0.0)
    for key in ("opening", "signature", "end_card"):
        pass
    song.TITLES["opening"]["t_end"] = -10.0
    song.TITLES["signature"]["windows"] = []
    song.TITLES["end_card"]["t_in"] = 1e9

    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)
    renderer.cards.overlay = lambda t: False
    from PIL import Image, ImageDraw
    args.outdir.mkdir(parents=True, exist_ok=True)
    for t in times:
        start = time.process_time()
        data = renderer.out.frame(t, int(round(t * 60)))
        img = Image.frombytes("RGB", (w, h), data)
        if args.guides and (38 <= t <= 55 or 156 <= t <= 177):
            d = ImageDraw.Draw(img)
            d.rectangle([w * 0.2, h * 0.12, w * 0.8, h * 0.42], outline=(90, 90, 140))
        out = args.outdir / f"people-{t:06.1f}.png"
        img.save(out)
        print(f"{t:.1f}: {time.process_time() - start:.1f} CPU s -> {out}", flush=True)


if __name__ == "__main__":
    os.environ.setdefault("P3D_CACHE", str(ROOT / "work/p3d_cache"))
    main()
