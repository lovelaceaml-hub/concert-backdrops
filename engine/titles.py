"""The concert's title and date, designed (song key TITLES; UPGRADE-HOWTO section Y). Four parts, any of them:

    TITLES = dict(
        opening=dict(t_end=4.0, y=0.30, palette="night"),
        signature=dict(windows=[(12.0, 15.5, "br", "night"), (31.0, 34.0, "tl", "day")]),
        date_light=dict(t_form=40.2, t_burst=43.5, y=0.30, palette="night"),
        end_card=dict(t_in=55.0),
    )

opening     N4: the logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), a gold hairline,
            SUNDAY, DECEMBER 6 · 4:30 PM, LAS VEGAS; whole on frame 0, then it crumbles into glowing dust that
            drifts up and away and is gone by t_end
signature   N5: the logo mark in a corner beside the title in italic on one line, DEC 6 · 4:30 PM and
            HEALING CONCERT · LAS VEGAS; shown only inside its windows, fading over 0.6 s each way
date_light  C: "December 6" written in points of light across the sky, with HEALING CONCERT · 4:30 PM small
            beneath; it forms from t_form, holds, and bursts apart at t_burst
end_card    N6, in the style of the official campaign poster (Outfit): the logo, HEALING CONCERT, The Words of
            / Mother's Love / That Bring Peace, a coral ribbon with the date, the church and the address, over a
            soft veil of light; it sweeps in from t_in and stays to the end (or t_out). It replaces the
            engine's closing title and tagline (song keys TITLE and TAGLINE)
palette     "night": warm white, gold accents, a warm glow. "day": navy #1f2a6b, gold accents, a soft white glow
            (the end card has its own colours, the campaign's: coral, navy, deep blue, yellow)

Type, sizes, tracking and glow follow Anthony's approved mockups (scratchpad titlemock: mock.py, mock2.py). The
lockups are drawn over the finished picture (after the bloom and the tone curve), so they show exactly as
designed; before the bloom the light of the scene behind them is dimmed (text protection), so no spark or ray
crosses a letter. The logo's slot is kept free while there is no logo. Everything is a pure function of t. A
song without TITLES never loads this module.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import song as S

FONTS = os.path.join(S.ROOT, "fonts")
PALETTES = dict(
    night=dict(col=(255, 246, 232), acc=(246, 211, 139), glow=(255, 214, 150), dot=(255, 236, 200), light=True),
    day=dict(col=(31, 42, 107), acc=(180, 132, 44), glow=(255, 255, 255), dot=(31, 42, 107), light=False,
             small=(243, 87, 99)),                       # the signature's small line on a bright sky: coral
)
KEEP = 0.985           # how much of the scene's light the protection takes away behind a lockup (to 1.5 percent)
SEP = "  ·  "          # the middle dot between two parts of a line, with two spaces each side
TITLE = "The Words of Mother\u2019s Love\nThat Bring Peace"   # Anthony's correction (2026-11-15)
# the same wording for the films' end cards and credits (song keys TITLE and CREDIT), so it is written once:
#   TITLE = dict(label="Healing Concert", lines=titles.TITLE_LINES, ...); CREDIT = dict(concert=titles.CONCERT, ...)
TITLE_LINES = TITLE.split("\n")
CONCERT = " ".join(TITLE_LINES)


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), max(int(round(size)), 4))


def CG(w, s, it=False):
    return _font(f"cormorant-garamond-latin-{w}-{'italic' if it else 'normal'}", s)


def OF(w, s):
    """Outfit (@fontsource/outfit, OFL): the face of the official campaign design, for the end card."""
    return _font(f"outfit-latin-{w}-normal", s)


def JO(w, s):
    return _font(f"jost-latin-{w}-normal", s)


def _tracked(draw, xy, text, fnt, fill, track, align="center"):
    """Letters drawn one by one with extra spacing (as the mockups): align center, left or right at xy."""
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if align == "center":
        x -= total / 2.0
    elif align == "right":
        x -= total
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + track
    return total


def _compose(layer, radius, strength, glow):
    """The text layer over its glow, as one premultiplied RGBA picture (floats 0..1), and the text's own alpha."""
    a = np.asarray(layer.split()[3], np.float32) / 255.0
    g = np.asarray(layer.split()[3].filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255.0 * strength
    rgb = np.asarray(layer.convert("RGB"), np.float32) / 255.0
    gc = np.asarray(glow, np.float32) / 255.0
    out = np.zeros(a.shape + (4,), np.float32)
    out[..., :3] = rgb * a[..., None] + gc[None, None, :] * (g * (1.0 - a))[..., None]
    out[..., 3] = a + g * (1.0 - a)
    return out, a, rgb


def _crop(arrs, pad=2):
    """Crops full-frame arrays to where the first one has anything: (cropped arrays, (x0, y0, x1, y1))."""
    al = arrs[0][..., 3] if arrs[0].ndim == 3 else arrs[0]
    ys, xs = np.nonzero(al > 1.0 / 255.0)
    h, w = al.shape
    x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad + 1, w)
    y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad + 1, h)
    return [a[y0:y1, x0:x1] for a in arrs], (x0, y0, x1, y1)


def _rgba(rgb, k, alpha):
    """Premultiplied colours (n, 4) for points: light (alpha False: added) or paint (alpha True: laid over)."""
    k = np.asarray(k, np.float32)
    rgb = np.broadcast_to(np.asarray(rgb, np.float32), (len(k), 3))
    return np.concatenate([rgb * k[:, None], (k if alpha else np.zeros_like(k))[:, None]], axis=1).astype(np.float32)


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float32) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


# ------------------------------------------------------------------------------------------------ the shaders
FULL_VS = """
#version 330
in vec2 aPos; out vec2 vUV; uniform float uFlip;
void main(){ vUV = aPos*0.5+0.5; gl_Position = vec4(aPos.x, aPos.y*uFlip, 0.0, 1.0); }
"""
OVL_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTex, uNoise;
uniform vec4 uRect;      // x0, y0 (from the top), width, height: fractions of the frame
uniform float uAlpha;
uniform vec4 uDis;       // dissolve: front (below -0.5: none), edge, share of the sweep, 1: appear
void main(){
  vec2 q = (vec2(vUV.x, 1.0 - vUV.y) - uRect.xy)/uRect.zw;     // the engine's passes have the top at vUV.y = 1
  if(q.x < 0.0 || q.y < 0.0 || q.x > 1.0 || q.y > 1.0) discard;
  vec4 c = texture(uTex, q);
  float k = uAlpha;
  if(uDis.x > -0.5){
    float d = mix(texture(uNoise, q).r, q.x, uDis.z);
    float g = smoothstep(d - uDis.y, d, uDis.x);
    k *= uDis.w > 0.5 ? g : 1.0 - g;
  }
  o = c*k;
}
"""
PROT_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
uniform vec4 uRect; uniform float uK;
void main(){
  vec2 q = (vec2(vUV.x, 1.0 - vUV.y) - uRect.xy)/uRect.zw;
  if(q.x < 0.0 || q.y < 0.0 || q.x > 1.0 || q.y > 1.0) discard;
  float m = smoothstep(0.0, 0.45, texture(uTex, q).a);
  o = vec4(vec3(1.0 - uK*m), 1.0);
}
"""
PT_VS = """
#version 330
in vec2 aXY; in float aSize; in vec4 aCol;
uniform vec2 uRes; uniform float uFlip;
out vec4 vCol;
void main(){
  vec2 v = aXY/uRes;
  gl_Position = vec4(v.x*2.0 - 1.0, uFlip*(1.0 - v.y*2.0), 0.0, 1.0);     // y: pixels from the top
  gl_PointSize = max(aSize, 1.0);
  vCol = aCol*min(aSize, 1.0);
}
"""
PT_FS = """
#version 330
in vec4 vCol; out vec4 o;
void main(){
  vec2 d = gl_PointCoord*2.0 - 1.0;
  float r2 = dot(d, d);
  if(r2 > 1.0) discard;
  o = vCol*exp(-r2*3.2);
}
"""


def prepare():
    """Called by the renderer before it builds any text: with an end card in TITLES, the engine's closing title
    and tagline (song keys TITLE and TAGLINE) never show, so the designed card is the only end text
    (TITLES keep_end_text=True keeps them)."""
    cfg = getattr(S, "TITLES", None) or {}
    if not cfg.get("end_card") or cfg.get("keep_end_text"):
        return
    if isinstance(getattr(S, "TITLE", None), dict):
        S.TITLE["form"] = S.TITLE["hold"] = 1e9
    if isinstance(getattr(S, "TAGLINE", None), dict):
        S.TAGLINE["t0"], S.TAGLINE["t1"] = 1e9, 1e9 + 4.0


class Titles:
    def __init__(self, R):
        import moderngl
        self.R, self.ctx, self.mgl = R, R.ctx, moderngl
        self.w, self.h = R.w, R.h
        self.s = R.h / 1080.0
        self.cfg = dict(getattr(S, "TITLES", None) or {})
        # the concert's title; a line break (\\n) splits it in two lines in the opening and the signature
        self.title = str(self.cfg.get("title", TITLE))
        ctx = self.ctx
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        self.p_ovl = ctx.program(vertex_shader=FULL_VS, fragment_shader=OVL_FS)
        self.p_prot = ctx.program(vertex_shader=FULL_VS, fragment_shader=PROT_FS)
        self.p_pt = ctx.program(vertex_shader=PT_VS, fragment_shader=PT_FS)
        self.v_ovl = ctx.vertex_array(self.p_ovl, [(quad, "2f", "aPos")])
        self.v_prot = ctx.vertex_array(self.p_prot, [(quad, "2f", "aPos")])
        self.pt_buf = ctx.buffer(reserve=16)
        self.pt_vao = None
        self.layers = {}
        op, sg, dl = self.cfg.get("opening"), self.cfg.get("signature"), self.cfg.get("date_light")
        if op:
            self.op = dict(t_end=float(op.get("t_end", 4.0)), y=float(op.get("y", 0.30)),
                           palette=op.get("palette", "night"), dissolve=float(op.get("dissolve", 1.6)))
            self._build_opening()
        else:
            self.op = None
        self.sig = []
        if sg:
            for win in sg.get("windows", []):
                a, b, corner = float(win[0]), float(win[1]), str(win[2])
                pal = win[3] if len(win) > 3 else sg.get("palette", "night")
                if corner not in ("tl", "tr", "bl", "br"):
                    raise ValueError(f"TITLES signature: corner must be tl, tr, bl or br, got {corner!r}")
                self.sig.append((a, b, corner, pal, self._layer(("sig", corner, pal), self._signature, corner, pal)))
            self.sig_fade = float(sg.get("fade", 0.6))
        ec = self.cfg.get("end_card")
        if ec:
            place = ec.get("place", ("World Mission Society Church of God", "6720 W Sahara Ave, Las Vegas"))
            self.ec = dict(t_in=float(ec["t_in"]), t_out=float(ec.get("t_out", 1e9)), y=float(ec.get("y", 0.5)),
                           fade=float(ec.get("fade", 1.6)), reveal=str(ec.get("reveal", "sweep")),
                           scale=float(ec.get("scale", 1.0)), veil=float(ec.get("veil", 1.0)),
                           backdrop=ec.get("backdrop", self.cfg.get("endcard_backdrop")) or None,
                           day=str(ec.get("day", "Sunday, December 6")), time=str(ec.get("time", "4:30 PM")),
                           place=[str(x) for x in (place.split("\n") if isinstance(place, str) else place)])
            self.ec_layer, self.ec_veil = self._end_card()
        else:
            self.ec = None
        if dl:
            self.dl = dict(t_form=float(dl["t_form"]), t_burst=float(dl["t_burst"]), y=float(dl.get("y", 0.30)),
                           palette=dl.get("palette", "night"), text=dl.get("text", "December 6"),
                           sub=dl.get("sub", "HEALING CONCERT" + SEP + "4:30 PM"))
            self._build_date()
        else:
            self.dl = None

    # ------------------------------------------------------------------ building the pictures (once)
    def _tex(self, arr, comps=4):
        a = np.ascontiguousarray(np.clip(arr * 255.0 + 0.5, 0, 255).astype(np.uint8))
        t = self.ctx.texture((a.shape[1], a.shape[0]), comps, data=a.tobytes())
        t.filter = (self.mgl.LINEAR, self.mgl.LINEAR)
        t.repeat_x = t.repeat_y = False
        return t

    def _layer(self, key, fn, *args):
        if key not in self.layers:
            self.layers[key] = fn(*args)
        return self.layers[key]

    def _finish(self, layer, radius, strength, pal, noise=False):
        P = PALETTES[pal]
        out, a, rgb = _compose(layer, radius * self.s, strength, P["glow"])
        (out, a, rgb), (x0, y0, x1, y1) = _crop([out, a, rgb])
        L = dict(tex=self._tex(out), rect=(x0 / self.w, y0 / self.h, (x1 - x0) / self.w, (y1 - y0) / self.h),
                 box=(x0, y0, x1, y1), a=a, rgb=rgb, pal=pal)
        # the text protection: a broad soft shape round the letters and between the lines
        g = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40 * self.s)),
                       np.float32) / 255.0
        pr = np.zeros(a.shape + (4,), np.float32)
        pr[..., 3] = np.clip(g * 16.0, 0.0, 1.0)
        L["prot"] = self._tex(pr)
        if noise:
            rng = np.random.default_rng(11)
            n = rng.random(a.shape).astype(np.float32)
            n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(max(1.2 * self.s, 0.8))), np.float32)
            r = np.empty(n.size, np.float32)                 # spread evenly over 0..1
            r[np.argsort(n.ravel(), kind="stable")] = np.linspace(0.0, 1.0, n.size, dtype=np.float32)
            L["noise"] = r.reshape(n.shape)
            L["t_noise"] = self._tex(L["noise"], 1)
        return L

    def _logo(self, part, height):
        """The campaign logo for a part as an RGBA picture `height` pixels high (render size), or None while there is
        no logo: the slot stays empty and the layout does not move. TITLES logo (for all parts, or per part):
        a path from the repository root, or dict(path=..., height=...) with the height in 1080p pixels; False in a
        part leaves that part without it."""
        lg = (self.cfg.get(part) or {}).get("logo", self.cfg.get("logo"))
        if not lg:
            return None
        path = lg.get("path") if isinstance(lg, dict) else lg
        if not path:
            return None
        if not os.path.isabs(path):
            path = os.path.join(S.ROOT, path)
        if not os.path.exists(path):
            print(f"titles: no logo file at {path}; the slot stays empty", flush=True)
            return None
        im = Image.open(path).convert("RGBA")
        h = float(lg["height"]) * self.s if isinstance(lg, dict) and "height" in lg else float(height)
        h = max(int(round(h)), 2)
        return im.resize((max(int(round(im.width * h / im.height)), 1), h), Image.LANCZOS)

    def _title_lines(self):
        """The title's lines: the first upright, the second (when there is one) in italic."""
        return [ln for ln in self.title.split("\n") if ln.strip()]

    def _opening(self, pal):
        """N4: the logo, HEALING CONCERT, the title (its second line in italic), a gold hairline, the date line,
        LAS VEGAS, all centred. The logo's slot is kept free when there is no logo, so the lockup never moves."""
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        lines = self._title_lines()
        lh = 130.0                                         # the logo slot (1080p pixels), then a gap of 28
        two = len(lines) > 1
        total = lh + 28 + 320 + 30 - (0 if two else 102)
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        cx = W / 2.0
        top = self.op["y"] * H - total * s / 2.0           # the top of the logo slot
        logo = self._logo("opening", lh * s)
        if logo is not None:
            L.alpha_composite(logo, (int(round(cx - logo.width / 2.0)), int(round(top + (lh * s - logo.height)))))
        y = top + (lh + 28) * s
        _tracked(d, (cx, y), "HEALING CONCERT", JO(500, 30 * s), acc + (255,), 9 * s)
        d.text((cx, y + 40 * s), lines[0], font=CG(500, 96 * s), fill=col + (255,), anchor="ma")
        if two:
            d.text((cx, y + 142 * s), lines[1], font=CG(500, 70 * s, it=True), fill=col + (255,), anchor="ma")
        else:
            y -= 102 * s
        d.line((cx - 60 * s, y + 242 * s, cx + 60 * s, y + 242 * s), fill=acc + (200,), width=max(1, int(round(2 * s))))
        _tracked(d, (cx, y + 262 * s), "SUNDAY, DECEMBER 6" + SEP + "4:30 PM", JO(500, 40 * s), col + (255,), 6 * s)
        _tracked(d, (cx, y + 320 * s), "LAS VEGAS", JO(400, 26 * s), acc + (235,), 8 * s)
        return self._finish(L, 14, 0.55, pal, noise=True)

    def _signature(self, corner, pal):
        """N5: the logo mark on the outer side, then the title in italic on one line, DEC 6 · 4:30 PM, and
        HEALING CONCERT · LAS VEGAS, aligned toward the logo (left in the left corners, mirrored in the right).
        A little larger than the mockup (1.1) so the date reads on a phone. Until there is a logo a thin gold
        hairline stands in its place."""
        s, W, H = self.s * 1.1, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        line = " ".join(self._title_lines())
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        right = corner[1] == "r"
        mx, my = 104 * self.s, 92 * self.s                 # margins: well inside the frame on a phone
        blk = 112.0 * s                                     # height of the block of three lines
        y0 = (H - my - blk) if corner[0] == "b" else my
        logo = self._logo("signature", 96 * s)
        if logo is not None:
            lx = (W - mx - logo.width) if right else mx
            L.alpha_composite(logo, (int(round(lx)), int(round(y0 + (blk - logo.height) / 2.0))))
            gap = logo.width + 22 * s
        else:
            hx = (W - mx) if right else mx
            d.line((hx, y0 + 6 * s, hx, y0 + blk - 6 * s), fill=acc + (220,), width=max(1, int(round(2 * self.s))))
            gap = 22 * s
        tx = (W - mx - gap) if right else (mx + gap)
        al = "right" if right else "left"
        d.text((tx, y0 - 4 * s), line, font=CG(500, 40 * s, it=True), fill=col + (240,), anchor="ra" if right else "la")
        _tracked(d, (tx, y0 + 48 * s), "DEC 6" + SEP + "4:30 PM", JO(500, 30 * s), col + (255,), 5 * s, align=al)
        small = P.get("small")
        _tracked(d, (tx, y0 + 88 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500 if small else 400, 22 * s),
                 (small or acc) + (255 if small else 230,), 5 * s,
                 align=al)
        return self._finish(L, 9, 0.5, pal)

    def _ec_xy(self, x, y):
        """A point of the end card mockup (1080p pixels) on the render: scaled about the frame's middle, with the
        block's middle moved to `y`."""
        k = self.s * self.ec["scale"]
        return self.w / 2.0 + (x - 960.0) * k, self.ec["y"] * self.h + (y - 540.0) * k

    def logo_box(self, part="end_card"):
        """Where a part's logo stands (its slot, whether or not there is a logo), as fractions of the frame:
        (x0, y0, x1, y1) from the top left. For a film whose particle logo (BRAND) lands in the end card."""
        if part == "end_card" and self.ec is not None:
            k = self.s * self.ec["scale"]
            (x0, y0), h = self._ec_xy(960.0 - 136.0, 48.0), 170.0 * k
            return x0 / self.w, y0 / self.h, (x0 + 272.0 * k) / self.w, (y0 + h) / self.h
        if part == "opening" and self.op is not None:
            lines = self._title_lines()
            total = 130 + 28 + 320 + 30 - (0 if len(lines) > 1 else 102)
            top, lh = self.op["y"] * self.h - total * self.s / 2.0, 130.0 * self.s
            cx, w = self.w / 2.0, lh * 1.6
            return (cx - w / 2.0) / self.w, top / self.h, (cx + w / 2.0) / self.w, (top + lh) / self.h
        return None

    def _end_card(self):
        """N6 (Anthony approved, after the official campaign poster): the logo, HEALING CONCERT (Outfit 600, coral,
        tracked), "The Words of" (Outfit 500, navy), "Mother's Love" (Outfit 800, large, coral, a little tight),
        "That Bring Peace" (Outfit 800, a deep blue gradient), a coral ribbon with notched ends holding
        "Sunday, December 6" in yellow and " · 4:30 PM" in white, then the church and the address (Outfit 500,
        navy). Returns the text layer and the veil of light behind it (two layers: the veil fades, the text
        sweeps in)."""
        W, H = self.w, self.h
        ec = self.ec
        k = self.s * ec["scale"]
        NAVY, CORAL, BLUE1, BLUE2, YEL = (39, 39, 81), (243, 87, 99), (3, 69, 165), (3, 45, 129), (255, 228, 120)
        lines = self._title_lines()
        first = lines[0]
        # "The Words of" / "Mother's Love": the official poster splits the first line before its last two words
        cut = first.rsplit(" ", 2)
        small, big = (cut[0], " ".join(cut[1:])) if len(cut) == 3 else ("", first)
        last = lines[1] if len(lines) > 1 else ""
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)

        def tr(cx, y, text, f, fill, track):
            """Tracked like the mockup: each letter at the width of the text before it (kerning kept)."""
            x = cx - (f.getlength(text) + track * (len(text) - 1)) / 2.0
            for i, c in enumerate(text):
                d.text((x + f.getlength(text[:i]) + track * i, y), c, font=f, fill=fill)

        logo = self._logo("end_card", 170.0 * k)
        cx = W / 2.0
        if logo is not None:
            lx, ly = self._ec_xy(960.0, 48.0)
            L.alpha_composite(logo, (int(round(lx - logo.width / 2.0)), int(round(ly))))
        tr(cx, self._ec_xy(0, 236)[1], "HEALING CONCERT", OF(600, 30 * k), CORAL + (255,), 9 * k)
        if small:
            tr(cx, self._ec_xy(0, 278)[1], small, OF(500, 78 * k), NAVY + (255,), -2 * k)
        tr(cx, self._ec_xy(0, 352)[1], big, OF(800, 176 * k), CORAL + (255,), -4 * k)
        if last:
            m = Image.new("L", (W, H), 0)
            dm = ImageDraw.Draw(m)
            f = OF(800, 124 * k)
            x = cx - (f.getlength(last) - 3 * k * (len(last) - 1)) / 2.0
            y = self._ec_xy(0, 540)[1]
            for i, c in enumerate(last):
                dm.text((x + f.getlength(last[:i]) - 3 * k * i, y), c, font=f, fill=255)
            bb = m.getbbox()
            u = np.clip((np.arange(H, dtype=np.float32) - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)[:, None, None]
            g = np.asarray(BLUE1, np.float32) * (1 - u) + np.asarray(BLUE2, np.float32) * u
            G = Image.fromarray(np.broadcast_to(g, (H, W, 3)).astype(np.uint8)).convert("RGBA")
            G.putalpha(m)
            L.alpha_composite(G)
            d = ImageDraw.Draw(L)
        # the ribbon with notched ends, like the official theme banner
        (rx0, ry0), (rx1, ry1), notch = self._ec_xy(520, 712), self._ec_xy(1400, 792), 34 * k
        d.polygon([(rx0 - notch, ry0), (rx1 + notch, ry0), (rx1, (ry0 + ry1) / 2), (rx1 + notch, ry1),
                   (rx0 - notch, ry1), (rx0, (ry0 + ry1) / 2)], fill=CORAL + (255,))
        f = OF(600, 44 * k)
        p1, p2 = ec["day"], "  \u00b7  " + ec["time"]
        x = cx - (f.getlength(p1) + f.getlength(p2)) / 2.0
        y = self._ec_xy(0, 728)[1]
        d.text((x, y), p1, font=f, fill=YEL + (255,))
        d.text((x + f.getlength(p1), y), p2, font=f, fill=(255, 255, 255, 255))
        for i, ln in enumerate(ec["place"][:2]):
            tr(cx, self._ec_xy(0, 826 + 52 * i)[1], ln, OF(500, 42 * k), NAVY + (255,), 0)
        T = self._finish(L, 10, 0.7, "day", noise=True)
        # the soft veil of light behind the block (light, never dark)
        v = Image.new("L", (W, H), 0)
        (vx0, vy0), (vx1, vy1) = self._ec_xy(360, 40), self._ec_xy(1560, 1040)
        ImageDraw.Draw(v).ellipse((vx0, vy0, vx1, vy1), fill=int(round(150 * min(ec["veil"], 1.7))))
        va = np.asarray(v.filter(ImageFilter.GaussianBlur(120 * k)), np.float32) / 255.0
        vo = np.zeros(va.shape + (4,), np.float32)
        vo[..., :3] = (np.asarray((255, 247, 234), np.float32) / 255.0)[None, None, :] * va[..., None]
        vo[..., 3] = 0.75 * va
        (vo,), (x0, y0, x1, y1) = _crop([vo])
        V = dict(tex=self._tex(vo), rect=(x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H), box=(x0, y0, x1, y1))
        if ec["backdrop"]:
            self.ec_back = self._pastel()
        return T, V

    def _pastel(self):
        """A soft pastel light over the whole frame (premultiplied, low resolution: it is all soft): warm cream in
        the middle, peach toward the left, a light sky blue toward the right, a little lighter at the top."""
        w, h = 480, 270
        x = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
        y = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
        cream = np.array((255, 249, 240), np.float32) / 255.0
        peach = np.array((255, 222, 196), np.float32) / 255.0
        sky = np.array((206, 230, 252), np.float32) / 255.0
        kl = np.clip(-x, 0.0, 1.0)[..., None] ** 1.3
        kr = np.clip(x, 0.0, 1.0)[..., None] ** 1.3
        col = cream * (1.0 - kl - kr) + peach * kl + sky * kr
        col = col * (1.0 - 0.04 * y[..., None]) + 0.0
        col = np.broadcast_to(col, (h, w, 3))
        r = np.sqrt((x * 0.9) ** 2 + (y * 1.0) ** 2)
        a = (0.97 - 0.22 * np.clip(r - 0.35, 0.0, 1.0)).astype(np.float32)
        out = np.zeros((h, w, 4), np.float32)
        out[..., :3] = np.clip(col, 0.0, 1.0) * a[..., None]
        out[..., 3] = a
        return dict(tex=self._tex(out), rect=(0.0, 0.0, 1.0, 1.0))

    def _backdrop_k(self, t):
        """How much of the pastel backdrop is in at t: it comes in over about a second round t_in; with "auto" only
        as far as the frame is dark where the card stands (measured on the finished picture, before the card)."""
        if self.ec is None or not self.ec["backdrop"]:
            return 0.0
        t0 = self.ec["t_in"]
        k = float(_ss(t0 - 0.6, t0 + 0.4, t)) * (1.0 - float(_ss(self.ec["t_out"] - 0.8, self.ec["t_out"], t)))
        if k <= 0.002 or self.ec["backdrop"] != "auto":
            return k
        x0, y0, x1, y1 = self.ec_layer["box"]
        st = 8
        raw = self.R.f_out.read(viewport=(x0, y0, x1 - x0, y1 - y0), components=3)   # rows: the picture's, top first
        px = np.frombuffer(raw, np.uint8).reshape(y1 - y0, x1 - x0, 3)[::st, ::st].astype(np.float32) / 255.0
        lum = float(np.mean(px @ np.array([0.2126, 0.7152, 0.0722], np.float32)))
        return k * (1.0 - float(_ss(0.42, 0.62, lum)))

    def _date_sub(self, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        _tracked(d, (W / 2.0, self.dl["y"] * H + 170 * s), self.dl["sub"], JO(500, 36 * s), P["col"] + (255,), 8 * s)
        return self._finish(L, 10, 0.5, pal)

    def _build_opening(self):
        L = self._layer(("op", self.op["palette"]), self._opening, self.op["palette"])
        # the dust the letters crumble into: points on the letters, each leaving when the dissolve passes it
        rng = np.random.default_rng(5)
        a = L["a"]
        ys, xs = np.nonzero(a > 0.35)
        n = int(min(36000 * self.s * self.s, len(xs)))
        pick = rng.choice(len(xs), size=n, replace=False, p=a[ys, xs] / a[ys, xs].sum())
        ys, xs = ys[pick], xs[pick]
        x0, y0 = L["box"][:2]
        ow = max(L["a"].shape[1] - 1, 1)
        self.op_pts = dict(x=(xs + x0 + rng.random(n) - 0.5).astype(np.float32),
                           y=(ys + y0 + rng.random(n) - 0.5).astype(np.float32),
                           d=(0.62 * L["noise"][ys, xs] + 0.38 * xs / ow).astype(np.float32),
                           col=L["rgb"][ys, xs].astype(np.float32), r=rng.random((n, 5)).astype(np.float32))
        self.op_layer = L

    def _build_date(self):
        s, W, H = self.s, self.w, self.h
        pal = self.dl["palette"]
        P = PALETTES[pal]
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).text((W / 2.0, self.dl["y"] * H), self.dl["text"], font=CG(600, 250 * s, it=True), fill=255,
                               anchor="mm")
        arr = np.asarray(m, np.float32) / 255.0
        ys, xs = np.nonzero(arr > 0.5)
        rng = np.random.default_rng(3)
        n = int(min(5600 * s * s, len(xs)))
        pick = rng.choice(len(xs), size=n, replace=False)
        ys, xs = ys[pick], xs[pick]
        rad = rng.choice([1.2, 1.6, 2.2, 3.0], size=n, p=[0.45, 0.30, 0.18, 0.07]).astype(np.float32) * s
        x0, x1 = float(xs.min()), float(xs.max())
        self.dl_pts = dict(x=xs.astype(np.float32) + rng.random(n).astype(np.float32) - 0.5,
                           y=ys.astype(np.float32) + rng.random(n).astype(np.float32) - 0.5,
                           xn=((xs - x0) / max(x1 - x0, 1.0)).astype(np.float32), size=2.0 * rad,
                           a=rng.uniform(0.67, 1.0, n).astype(np.float32), r=rng.random((n, 6)).astype(np.float32))
        k = 300                                                # loose sparks that drift off the letters
        self.dl_sparks = dict(x=rng.uniform(W / 2 - 400 * s, W / 2 + 400 * s, k).astype(np.float32),
                              y=(self.dl["y"] * H + rng.uniform(-160, 190, k) * s).astype(np.float32),
                              size=(2.0 * rng.uniform(0.8, 2.0, k) * s).astype(np.float32),
                              a=rng.uniform(0.25, 0.6, k).astype(np.float32), r=rng.random((k, 4)).astype(np.float32))
        self.dl_centre = np.array([W / 2.0, self.dl["y"] * H], np.float32)
        # the place the letters light up, for the text protection
        g = np.asarray(m.filter(ImageFilter.GaussianBlur(16 * s)), np.float32) / 255.0
        prot = np.zeros(arr.shape + (4,), np.float32)
        prot[..., 3] = np.clip(g * 2.5, 0.0, 1.0)
        (prot,), (bx0, by0, bx1, by1) = _crop([prot])
        self.dl_prot = dict(tex=self._tex(prot), rect=(bx0 / W, by0 / H, (bx1 - bx0) / W, (by1 - by0) / H))
        self.dl_sub = self._layer(("dsub", pal), self._date_sub, pal)
        self.dl_fill = None
        if not P["light"]:
            # on a bright sky points alone read as faint glitter: the letters themselves fill in, deep navy, as the
            # points settle, and the points sparkle over them
            F = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(F).text((W / 2.0, self.dl["y"] * H), self.dl["text"], font=CG(600, 250 * s, it=True),
                                   fill=P["col"] + (255,), anchor="mm")
            self.dl_fill = self._finish(F, 14, 0.85, pal)
        # the sub line also bursts: a few hundred points on its letters
        a = self.dl_sub["a"]
        ys, xs = np.nonzero(a > 0.4)
        n2 = int(min(1500 * s * s, len(xs)))
        pick = rng.choice(len(xs), size=n2, replace=False)
        bx, by = self.dl_sub["box"][:2]
        self.dl_subpts = dict(x=(xs[pick] + bx).astype(np.float32), y=(ys[pick] + by).astype(np.float32),
                              r=rng.random((n2, 4)).astype(np.float32))
        self.dl_col = np.asarray(P["dot"], np.float32) / 255.0

    # ------------------------------------------------------------------ timing
    def _op_state(self, t):
        """(alpha, dissolve front or None, progress 0..1) of the opening at t."""
        if self.op is None or t >= self.op["t_end"] + 2.2:
            return 0.0, None, 1.0
        dur = min(self.op["dissolve"], max(self.op["t_end"], 0.2))
        td0 = self.op["t_end"] - dur
        u = (t - td0) / max(dur, 1e-6)
        if u <= 0.0:
            return 1.0, None, 0.0
        e = 0.06
        return 1.0, -e + (1.0 + 2.0 * e) * min(u, 1.2), float(min(u, 1.0))

    def _ec_state(self, t):
        """(alpha, reveal front or None) of the end card at t: it sweeps in from the left out of glints (reveal
        "sweep") or fades in ("fade") over `fade` seconds from t_in, and fades out over 0.8 s before t_out."""
        if self.ec is None or t < self.ec["t_in"] or t >= self.ec["t_out"]:
            return 0.0, None
        u = (t - self.ec["t_in"]) / max(self.ec["fade"], 1e-3)
        out = 1.0 - float(_ss(self.ec["t_out"] - 0.8, self.ec["t_out"], t))
        if self.ec["reveal"] == "sweep":
            e = 0.30
            return out, (None if u >= 1.0 else -e + (1.0 + 2.0 * e) * u)
        return out * float(_ss(0.0, 1.0, u)), None

    def _sig_alpha(self, t):
        out = []
        f = self.sig_fade if self.sig else 0.6
        for a, b, corner, pal, L in self.sig:
            k = float(_ss(a, a + f, t) * (1.0 - _ss(b - f, b, t)))
            if k > 0.002:
                out.append((L, k))
        return out

    def _dl_times(self):
        tf, tb = self.dl["t_form"], self.dl["t_burst"]
        form = float(np.clip((tb - tf) - 1.5, 0.5, 1.4))       # it is whole at least 1.5 s before the burst
        return tf, tb, form

    def _dl_fill_alpha(self, t):
        if self.dl is None or self.dl_fill is None:
            return 0.0
        tf, tb, form = self._dl_times()
        return 0.95 * float(_ss(tf + 0.7 * form, tf + form + 0.3, t) * (1.0 - _ss(tb - 0.02, tb + 0.10, t)))

    def _dl_sub_alpha(self, t):
        if self.dl is None:
            return 0.0
        tf, tb, form = self._dl_times()
        return float(_ss(tf + 0.55 * form, tf + form + 0.25, t) * (1.0 - _ss(tb, tb + 0.18, t)))

    # ------------------------------------------------------------------ drawing
    def _quad(self, prog, vao, L, flip, tex="tex", **uni):
        prog["uFlip"].value = flip
        if "uRect" in prog:
            prog["uRect"].value = tuple(float(v) for v in L["rect"])
        L[tex].use(location=0)
        prog["uTex"].value = 0
        for k, v in uni.items():
            if k in prog:
                prog[k].value = v
        vao.render(self.mgl.TRIANGLE_STRIP)

    def protect(self, t):
        """Dims the scene's light behind the titles (before the bloom): call with the light buffer bound."""
        jobs = []
        a, front, prog = self._op_state(t)
        if a > 0.0 and prog < 1.0:
            jobs.append((self.op_layer, KEEP * (1.0 - prog)))
        for L, k in self._sig_alpha(t):
            jobs.append((L, KEEP * k))
        ea, ef = self._ec_state(t)
        if ea > 0.002:
            jobs.append((self.ec_layer, KEEP * ea * (1.0 if ef is None else float(np.clip(ef + 0.3, 0.0, 1.0)))))
        if self.dl is not None:
            tf, tb, form = self._dl_times()
            k = float(_ss(tf, tf + form, t) * (1.0 - _ss(tb, tb + 0.4, t)))
            if k > 0.002:
                jobs.append((self.dl_prot, 0.75 * k))
            ks = self._dl_sub_alpha(t)
            if ks > 0.002:
                jobs.append((self.dl_sub, 0.85 * ks))
        if not jobs:
            return
        ctx = self.ctx
        self.R.f_L.use()
        ctx.enable(self.mgl.BLEND)
        ctx.blend_func = (self.mgl.ZERO, self.mgl.SRC_COLOR)
        for L, k in jobs:
            self._quad(self.p_prot, self.v_prot, L, 1.0, tex="prot" if "prot" in L else "tex", uK=float(k))
        ctx.blend_func = (self.mgl.ONE, self.mgl.ONE)

    def overlay(self, t):
        """Draws the titles over the finished picture: call after the composite, with nothing else to come."""
        ctx = self.ctx
        mgl = self.mgl
        self.R.f_out.use()
        ctx.enable(mgl.BLEND)
        ctx.blend_func = (mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA)
        drew = False
        a, front, prog = self._op_state(t)
        if a > 0.0 and prog < 1.0:
            L = self.op_layer
            L["t_noise"].use(location=1)
            self.p_ovl["uNoise"].value = 1
            self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=1.0,
                       uDis=(float(front) if front is not None else -1.0, 0.06, 0.38, 0.0))
            drew = True
        for L, k in self._sig_alpha(t):
            self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=float(k), uDis=(-1.0, 0.0, 0.0, 0.0))
            drew = True
        kb = self._backdrop_k(t)
        if kb > 0.002:
            self._quad(self.p_ovl, self.v_ovl, self.ec_back, -1.0, uAlpha=kb, uDis=(-1.0, 0.0, 0.0, 0.0))
            drew = True
        ea, ef = self._ec_state(t)
        if ea > 0.002:
            kv = ea * (1.0 if ef is None else float(_ss(-0.3, 0.5, ef)))
            self._quad(self.p_ovl, self.v_ovl, self.ec_veil, -1.0, uAlpha=kv, uDis=(-1.0, 0.0, 0.0, 0.0))
            L = self.ec_layer
            L["t_noise"].use(location=1)
            self.p_ovl["uNoise"].value = 1
            self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=ea,
                       uDis=(float(ef) if ef is not None else -1.0, 0.30, 0.72, 1.0))
            drew = True
        ks = self._dl_sub_alpha(t)
        if ks > 0.002:
            self._quad(self.p_ovl, self.v_ovl, self.dl_sub, -1.0, uAlpha=ks, uDis=(-1.0, 0.0, 0.0, 0.0))
            drew = True
        kf = self._dl_fill_alpha(t)
        if kf > 0.002:
            self._quad(self.p_ovl, self.v_ovl, self.dl_fill, -1.0, uAlpha=kf, uDis=(-1.0, 0.0, 0.0, 0.0))
            drew = True
        pts = []
        if self.op is not None and front is not None:
            pts += self._op_points(t, front)
        if self.dl is not None:
            pts += self._dl_points(t)
        for batch, additive in pts:
            if batch is None:
                continue
            ctx.blend_func = (mgl.ONE, mgl.ONE) if additive else (mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA)
            self._points(batch)
            drew = True
        ctx.blend_func = (mgl.ONE, mgl.ONE)
        ctx.disable(mgl.BLEND)
        return drew

    def _points(self, b):
        xy, size, col = b
        n = len(size)
        if n == 0:
            return
        data = np.empty((n, 7), np.float32)
        data[:, 0:2] = xy
        data[:, 2] = size
        data[:, 3:7] = col
        raw = data.tobytes()
        if self.pt_buf.size < len(raw):
            self.pt_buf = self.ctx.buffer(reserve=len(raw) * 2)
            self.pt_vao = None
        self.pt_buf.write(raw)
        if self.pt_vao is None:
            self.pt_vao = self.ctx.vertex_array(self.p_pt, [(self.pt_buf, "2f 1f 4f", "aXY", "aSize", "aCol")])
        self.p_pt["uRes"].value = (float(self.w), float(self.h))
        self.p_pt["uFlip"].value = -1.0
        self.ctx.enable(self.mgl.PROGRAM_POINT_SIZE)
        self.pt_vao.render(self.mgl.POINTS, vertices=n)

    def _op_points(self, t, front):
        """The opening's letters crumble into dust that drifts up and to the right and fades."""
        p = self.op_pts
        dur = min(self.op["dissolve"], max(self.op["t_end"], 0.2))
        td0 = self.op["t_end"] - dur
        e = 0.06
        rel = td0 + dur * (p["d"] - 0.5 * e + e) / (1.0 + 2.0 * e)
        age = t - rel
        r = p["r"]
        life = 0.9 + 1.0 * r[:, 0]
        on = (age > 0.0) & (age < life)
        if not on.any():
            return []
        ag, rr = age[on], r[on]
        s = self.s
        vx = (25.0 + 70.0 * rr[:, 1]) * s
        vy = -(30.0 + 90.0 * rr[:, 2]) * s
        x = p["x"][on] + vx * ag + 9.0 * s * np.sin(ag * (2.0 + 3.0 * rr[:, 3]) + rr[:, 4] * 6.28) * ag
        y = p["y"][on] + vy * ag - 22.0 * s * ag * ag
        lf = ag / life[on]
        k = np.exp(-lf * 2.2) * (1.0 - _ss(0.7, 1.0, lf)) * (0.55 + 0.45 * _ss(0.0, 0.08, ag))
        size = (1.6 + 2.2 * rr[:, 3]) * s * (1.0 - 0.4 * lf)
        P = PALETTES[self.op["palette"]]
        col = p["col"][on]
        xy = np.stack([x, y], axis=1)
        if P["light"]:
            glow = np.asarray(P["glow"], np.float32) / 255.0
            return [((xy[::3], size[::3] * 4.5, _rgba(glow, k[::3] * 0.07, False)), True),
                    ((xy, size, _rgba(col, k * 1.35, False)), True)]
        return [((xy, size, _rgba(col, k, True)), False)]

    def _dl_points(self, t):
        """'December 6' in points of light: they fly in and settle in writing order, twinkle, then burst."""
        tf, tb, form = self._dl_times()
        if t < tf or t > tb + 1.8:
            return []
        p = self.dl_pts
        s = self.s
        r = p["r"]
        arrive = tf + form * (0.35 + 0.55 * (0.75 * p["xn"] + 0.25 * r[:, 0]))
        start = arrive - 0.65 * form
        u = np.clip((t - start) / np.maximum(arrive - start, 1e-3), 0.0, 1.0)
        e = 1.0 - (1.0 - u) ** 3
        ang = r[:, 1] * 6.2832
        dist = (260.0 + 520.0 * r[:, 2]) * s
        sx = p["x"] + np.cos(ang) * dist + 120.0 * s
        sy = p["y"] + np.sin(ang) * dist * 0.55 - 160.0 * s
        x = sx + (p["x"] - sx) * e + 18.0 * s * np.sin(e * 3.14159) * np.cos(ang * 3.0)
        y = sy + (p["y"] - sy) * e
        a = p["a"] * _ss(0.0, 0.25, u)
        a = a * (0.86 + 0.14 * np.sin(t * (2.0 + 3.0 * r[:, 3]) + r[:, 4] * 6.28))
        flash = 1.0 + 1.4 * np.exp(-np.maximum(t - arrive, 0.0) / 0.12) * (t > arrive)
        size = p["size"].copy()
        # the burst: every point thrown out from the centre, slowing, fading
        if t >= tb:
            bt = t - tb
            d = np.stack([x, y], axis=1) - self.dl_centre[None, :]
            ln = np.maximum(np.linalg.norm(d, axis=1), 1.0)
            spd = (500.0 + 1300.0 * r[:, 5] ** 1.5) * s
            go = spd * (1.0 - np.exp(-bt * 2.6)) / 2.6
            x = x + d[:, 0] / ln * go
            y = y + d[:, 1] / ln * go + 60.0 * s * bt * bt
            life = 0.6 + 0.9 * r[:, 4]
            a = a * (1.0 - _ss(0.0, 1.0, bt / life)) * (1.0 + 1.8 * np.exp(-bt / 0.10))
            size = size * (1.0 + 0.6 * np.exp(-bt / 0.15))
            flash = 1.0
        a = a * flash
        out = []
        P = PALETTES[self.dl["palette"]]
        xy = np.stack([x, y], axis=1)
        vis = a > 0.004
        xy, size, a = xy[vis], size[vis], a[vis]
        if P["light"]:
            out.append(((xy[::2], size[::2] * 4.5, _rgba(np.asarray(P["glow"], np.float32) / 255.0, a[::2] * 0.16, False)), True))
            out.append(((xy, size, _rgba(self.dl_col, a * 1.2, False)), True))
        else:
            gl = np.asarray(P["glow"], np.float32) / 255.0
            out.append(((xy, size * 3.5, _rgba(gl, a * 0.06, False)), True))
            out.append(((xy, size * 1.3, _rgba(self.dl_col, a, True)), False))
        # loose sparks round the letters while the date is whole
        k = float(_ss(tf + 0.6 * form, tf + form + 0.4, t) * (1.0 - _ss(tb, tb + 0.15, t)))
        if k > 0.01:
            sp = self.dl_sparks
            rr = sp["r"]
            sxy = np.stack([sp["x"] + 14.0 * s * np.sin(t * 0.5 + rr[:, 0] * 6.28),
                            sp["y"] - 10.0 * s * ((t * (0.4 + 0.6 * rr[:, 1]) + rr[:, 2]) % 1.0)], axis=1)
            sa = sp["a"] * k * (0.6 + 0.4 * np.sin(t * 3.0 + rr[:, 3] * 6.28))
            out.append(((sxy, sp["size"], _rgba(self.dl_col, sa, not P["light"])), P["light"]))
        # the sub line bursts with the date
        if t >= tb:
            bt = t - tb
            q = self.dl_subpts
            rr = q["r"]
            d = np.stack([q["x"], q["y"]], axis=1) - self.dl_centre[None, :]
            ln = np.maximum(np.linalg.norm(d, axis=1), 1.0)
            go = (300.0 + 900.0 * rr[:, 0]) * s * (1.0 - np.exp(-bt * 3.0)) / 3.0
            qxy = np.stack([q["x"] + d[:, 0] / ln * go, q["y"] + d[:, 1] / ln * go + 50.0 * s * bt * bt], axis=1)
            qa = (1.0 - _ss(0.0, 1.0, bt / (0.5 + 0.6 * rr[:, 1]))) * 0.9
            qs = (1.6 + 1.6 * rr[:, 2]) * s
            sub_col = np.asarray(P["col"], np.float32) / 255.0
            out.append(((qxy, qs, _rgba(sub_col, qa, not P["light"])), P["light"]))
        return out
