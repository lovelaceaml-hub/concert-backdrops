"""Output settings (I10): 4K and 60 fps, the seamless pre-show / intermission loop, and its event card.

Nothing here changes a song that does not ask for it:

- OUT_RES ("1080p", the default, or "4k") and OUT_FPS (30, the default, or 60) are environment variables set by
  the Render workflow. The song's layout stays on its 1920x1080 design canvas (S.W, S.H); only the size of the
  frames the engine draws and the number of frames per second change. Everything the engine draws is a pure
  function of the time in seconds, so 60 fps is simply twice as many samples of the same motion.
- LOOP_SECONDS in a song file makes the video a seamless loop of that length: frame 0 follows the last frame
  with no jump. The song should keep its settings calm and periodic (loop_wave below helps); the engine then
  hides whatever still drifts (cloud noise, twinkles, motes) with a gentle crossfade over the first
  LOOP_XFADE seconds (default 6): it fades from the picture at time LOOP_SECONDS + t into the picture at t, so
  the first frame is exactly the frame that would come after the last one.
- EVENT_CARD = dict(lines=[campaign, concert, date and time, place], ...) shows a calm card with the event's
  details (see UPGRADE-HOWTO.md, section I10).

song.py calls apply() on the song module before anything else reads it; render.py calls Output(R) once, and
frame() for every frame.
"""
import math
import os

import numpy as np

RES = {"1080p": (1920, 1080), "4k": (3840, 2160)}


def settings():
    """(resolution name, frames per second) from the environment, checked."""
    res = (os.environ.get("OUT_RES") or "1080p").strip().lower()
    if res not in RES:
        raise SystemExit(f"OUT_RES must be one of {sorted(RES)}, got {res!r}")
    fps = (os.environ.get("OUT_FPS") or "").strip()
    if fps and fps not in ("30", "60"):
        raise SystemExit(f"OUT_FPS must be 30 or 60, got {fps!r}")
    return res, (int(fps) if fps else None)


def apply(m):
    """Applies OUT_FPS and LOOP_SECONDS to a freshly imported song module (before its Song() is built)."""
    _res, fps = settings()
    old = getattr(m, "FPS", 30)
    if fps and fps != old:
        m.FPS = fps
    loop = getattr(m, "LOOP_SECONDS", None)
    if loop:
        m.TOTAL = float(loop)
    if loop or (fps and fps != old):
        total = getattr(m, "TOTAL", None)
        m.NFRAMES = int(round(total * m.FPS)) if total else int(round(m.NFRAMES * m.FPS / old))


def scale(S):
    """How much larger than the song's design canvas the frames are drawn (1 for 1080p, 2 for 4K)."""
    res, _ = settings()
    return RES[res][1] / float(S.H)


def loop_wave(t, period, cycles=1, phase=0.0):
    """sin() that repeats exactly `cycles` times per `period` seconds: for settings that must loop."""
    return math.sin(2.0 * math.pi * (cycles * t / period + phase))


def _setu(prog, **kw):
    for k, v in kw.items():
        if k in prog:
            prog[k].value = tuple(float(x) for x in np.ravel(v)) if isinstance(v, np.ndarray) else v


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


class Output:
    def __init__(self, R):
        import song as S
        self.S, self.R = S, R
        self.loop = float(getattr(S, "LOOP_SECONDS", 0.0) or 0.0)
        self.xfade = min(float(getattr(S, "LOOP_XFADE", 6.0)), self.loop * 0.5) if self.loop else 0.0
        self.card = None
        ev = getattr(S, "EVENT_CARD", None)
        if ev:
            tex, bounds = render_card(ev)
            t = R.ctx.texture((S.W, S.H), 3, data=tex.tobytes(), dtype="f1")
            import moderngl
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            self.card = dict(tex=t, bounds=bounds, meta=ev)

    # ------------------------------------------------------------ the event card
    def card_alpha(self, t):
        if self.card is None:
            return 0.0
        m = self.card["meta"]
        if self.loop:
            t = t % self.loop
        fade = float(m.get("fade", 2.0))
        a0, a1 = m.get("t_show"), m.get("t_hide")
        a = 1.0
        if a0 is not None:
            a *= _ss(a0, a0 + fade, t)
        if a1 is not None:
            a *= 1.0 - _ss(a1 - fade, a1, t)
        return a * float(m.get("alpha", 0.95))

    def card_slot(self, t):
        """The card as text slot B (texture, form params, bounds, shade, offset), or None when it is hidden."""
        a = self.card_alpha(t)
        if a <= 0.001:
            return None
        return (self.card["tex"], (100.0, 1.0, -1.0, a), self.card["bounds"], 1.0, (0.0, 0.0))

    def draw_card(self, t):
        a = self.card_alpha(t)
        if a <= 0.001:
            return
        S, R = self.S, self.R
        m = self.card["meta"]
        period = self.loop or 12.0   # a slow breath of the glow, a whole number of times per loop
        breath = 0.5 + 0.5 * loop_wave(t, period, max(1, round(period / 12.0))) if m.get("breathe", True) else 0.0
        self.card["tex"].use(location=0)
        import moderngl
        _setu(R.p_text, uTex=0, uFormT=100.0, uFormDur=1.0, uFlyT=-1.0, uAspect=S.ASPECT, uAlpha=a,
             uPulse=0.6 * breath, uBounds=self.card["bounds"], uCol=S.lin(m.get("color", "#fff5df")),
             uGlowCol=S.lin(m.get("glow", "#ffc48c")))
        R.v_text.render(moderngl.TRIANGLE_STRIP)

    # ------------------------------------------------------------ frames
    def frame(self, t, index=0):
        """One frame as rgb bytes. In a loop song the time wraps, and the first LOOP_XFADE seconds fade from the
        picture one loop later into the picture now, so the loop has no seam."""
        R = self.R
        if not self.loop:
            return R.frame(t, index)
        t = t % self.loop
        if t >= self.xfade:
            return R.frame(t, index)
        k = _ss(0.0, self.xfade, t)
        late = np.frombuffer(R.frame(t + self.loop, index), np.uint8).astype(np.float32)
        now = np.frombuffer(R.frame(t, index), np.uint8).astype(np.float32)
        return np.clip(late * (1.0 - k) + now * k + 0.5, 0, 255).astype(np.uint8).tobytes()


def render_card(ev):
    """The event card: campaign title (small capitals), concert title (large serif), then the date and time and
    the place (italic). Returns (rgb texture bottom-up, bounds) on the song's design canvas."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    import text as T
    W, H = T.W, T.H
    lines = list(ev["lines"])
    sizes = list(ev.get("sizes", (34, 104, 54, 44)))
    while len(sizes) < len(lines):
        sizes.append(sizes[-1])
    maxw = float(ev.get("max_width", 1580))
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)

    def fit(text, path, size):
        while True:
            f = ImageFont.truetype(path, int(size))
            if f.getlength(text) <= maxw or size <= 24:
                return f
            size -= 2

    rows = []   # (font, text, height, fill, tracked)
    for i, (ln, sz) in enumerate(zip(lines, sizes)):
        if i == 0 and ev.get("label_first", True):
            f = ImageFont.truetype(T.F_LABEL, int(sz))
            rows.append((f, ln.upper(), sz * 1.9, 236, True))
        elif i == 1:
            f = fit(ln, T.F_TITLE, sz)
            rows.append((f, ln, f.size * 1.30, 255, False))
        else:
            f = fit(ln, T.F_TAG, sz)
            rows.append((f, ln, f.size * 1.32, 244, False))
    block = sum(r[2] for r in rows)
    y = float(ev.get("y", 0.40)) * H - block / 2.0
    wl = 0.0
    for f, ln, hgt, fill, tracked in rows:
        base = y + hgt * 0.72
        if tracked:
            wl = max(wl, T._tracked(d, (W / 2.0, base), ln, f, 0.42 * f.size, fill))
        else:
            d.text((W / 2.0, base), ln, font=f, fill=fill, anchor="ms")
            wl = max(wl, f.getlength(ln))
        y += hgt
    sharp = np.asarray(img)
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(8)))
    back = T.shield(img)
    return np.dstack([sharp, glow, back])[::-1].copy(), ((W / 2 - wl / 2) / W, (W / 2 + wl / 2) / W)
