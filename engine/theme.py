"""Theme colours for the campaign look (UPGRADE-HOWTO section H3).

Anthony's blend of the luminous original world with the campaign poster: cream and white light, soft sky blue,
warm yellow and peach, coral pink and navy accents, fresh green leaves and iridescent soap bubbles, and never a
dark patch behind text.

A song file uses it in one line, after TOTAL and before params() runs (the engine reads the settings at render
time, so this simply replaces the song's sky Tracks and sets the theme keys):

    import theme
    theme.campaign_day(globals(), [(0.0, "dawn"), (12.0, "day"), (40.0, "golden"), (TOTAL, "cream")])

Every colour here is the colour you SEE on screen: display() turns it into the engine's linear light, undoing the
filmic curve, so a sky key "#cfe8fa" really shows as that blue (before glow, clouds and the arch are added).
"""
import numpy as np

from track import Track

# campaign colours (display hex)
NAVY = "#1f2a6b"
NAVY_BRIGHT = "#12358f"
CORAL = "#f0566a"
CORAL_SOFT = "#d9606a"
GOLD = "#ffd27a"
CREAM = "#fff6e6"
WHITE_GLOW = "#fff8ec"
LEAF_GREEN = "#9fe07a"
LEAF_GOLD = "#ffe08a"
SKY_BLUE = "#8ecdf4"
PEACH = "#ffd2b4"

# sky palettes (top of sky, middle, horizon, glow of the sun), as seen on screen
PAL = {
    "dawn":   ("#9cc8ec", "#f7d9cc", "#ffe4c4", "#fff0d2"),   # soft blue above, peach and warm cream low down
    "day":    ("#86c6f0", "#cfe8fa", "#fff4e4", "#fffaee"),   # clear sky blue to a cream horizon
    "golden": ("#a8cdee", "#ffe2cc", "#ffd9a4", "#ffe9b8"),   # warm yellow and peach light
    "peach":  ("#b4d4f0", "#ffd9cf", "#ffcdb0", "#fff0dc"),   # peach with a pink touch
    "cream":  ("#cbe4f6", "#fff3e6", "#fffaf2", "#ffffff"),   # almost white: the luminous end
}


def _tone(x):
    x = np.maximum(x, 0.0)
    return (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)


def display(hexs, exposure=1.0):
    """The linear light the engine needs so the final picture shows this colour (inverse of the filmic curve)."""
    h = hexs.lstrip("#")
    y = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0
    y = np.clip(y ** 2.2, 0.0, 0.975)
    a, b, c = 2.43 * y - 2.51, 0.59 * y - 0.03, 0.14 * y
    x = (-b - np.sqrt(np.maximum(b * b - 4.0 * a * c, 0.0))) / (2.0 * a)
    return x / exposure


def sky_tracks(keys, pal=None):
    """SKY_TOP, SKY_MID, SKY_HOR, GLOW Tracks from [(t, palette name or (top, mid, hor, glow) hexes), ...]."""
    pal = dict(PAL, **(pal or {}))

    def entry(p, k):
        return display((pal[p] if isinstance(p, str) else p)[k])

    # the sky shader adds the sun glow on top, so the base colours sit a little lower than the target
    out = []
    for k, scale in ((0, 0.92), (1, 0.86), (2, 0.78), (3, 0.42)):
        out.append(Track([(t, entry(p, k) * scale) for t, p in keys]))
    return tuple(out)


def campaign_day(g, keys=None, total=None, text="navy", bubbles=0.55, leaves=0.35):
    """Sets the campaign day look on a song module's globals (g = globals()). Only keys the song has not set
    AFTER this call change; set your own values after calling it to override any of them.

    keys: the sky palette over time, [(t, name), ...] with names from PAL (default: dawn to day to cream).
    text: "navy" (navy words, soft white glow), "coral" (coral words, gold glow) or None (keep light words).
    bubbles, leaves: constant amounts for BUBBLES and LEAVES (0 leaves that layer off).
    """
    total = total if total is not None else g.get("TOTAL", 60.0)
    keys = keys or [(0.0, "dawn"), (total * 0.25, "day"), (total * 0.7, "golden"), (total, "cream")]
    g["SKY_TOP"], g["SKY_MID"], g["SKY_HOR"], g["GLOW"] = sky_tracks(keys)
    g["SKY_THEME"] = "campaign_day"
    g["TEXT_SHADOW"] = 0.0                 # no dark veil behind any text
    g["STARS"] = Track([(0.0, 0.10), (total, 0.10)])     # stars only as faint glints
    g["MILKY"] = Track([(0.0, 0.0), (total, 0.0)])
    g["AURORA"] = Track([(0.0, 0.0), (total, 0.0)])
    g["RAIN"] = Track([(0.0, 0.0), (total, 0.0)])
    g["MOTE_COLORS"] = (WHITE_GLOW, GOLD)
    g["PETAL_COLORS"] = (CORAL, PEACH)
    g["AURORA_WARM"] = (PEACH, GOLD)
    if bubbles:
        g["BUBBLES"] = Track([(0.0, 0.0), (2.0, float(bubbles)), (total, float(bubbles))])
    if leaves:
        g["LEAVES"] = Track([(0.0, 0.0), (3.0, float(leaves)), (total, float(leaves))])
        g["LEAVES_COLORS"] = (LEAF_GREEN, LEAF_GOLD)
    if text:
        ink, glow = (NAVY, WHITE_GLOW) if text == "navy" else (CORAL, GOLD)
        g["GLOW_COLOR"] = glow
        for m in list(g.get("PHRASES", [])) + [g.get("TITLE"), g.get("TAGLINE"), g.get("CREDIT")] + list(
                g.get("FRAGMENTS", [])):
            if isinstance(m, dict):
                m.setdefault("color", ink)
    return g
