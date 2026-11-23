"""Song kit stage test: the kit_demo song (about 40 s on the repository's Song 7 promo excerpt,
audio/promo/s07.mp3) with the stage set (modules/kit_stage.py: Song 11's choir and orchestra) standing on the
mirror sea. Three stage blocks show its three main framings (wide from the front, the arc along the choir, over
the conductor's shoulder). The expressions' acts still run but stay off camera. A technical test, not a design.
No em dash or en dash anywhere in this file.
"""
TITLE = "Song kit stage test"
CATALOG_ID = "s07"
LIVE = 36.0
HOLD = 4.0
MUSIC_END = 35.9
LAST_CHORD = 35.0
OPENING_END = 7.0
INTRO_FULL = 7.0
SETS = ["demo_world", "kit_stage"]

HIT = dict(lift=9.2, wish=19.6, help=24.5)
SLAMS = []
KEY_MOMENTS = [(17.5, 1.6), (32.0, 1.6)]
LEVELS = [(0.0, 0.2), (7.0, 0.35), (17.0, 0.6), (24.0, 0.5), (33.0, 0.3)]
GLORY = [(0.0, 0.25), (17.5, 0.5), (32.0, 0.7), (40.0, 0.6)]
CONSTELLATIONS = [3.0, 5.0, 7.0, 9.2, 12.0, 15.0, 19.6, 24.5, 30.0]
LANTERN_SPANS = [(20.0, 34.0)]

EDIT = [
    (0.0, "world", "the opening over the dusk sea"),
    (9.2, "stage", "the choir and orchestra on the sea, wide from the front"),
    (16.0, "stage", "along the choir's front row as it breathes in"),
    (19.6, "world", "the glide over the water"),
    (24.5, "stage", "over the conductor's shoulder; the heroes raise their arms"),
    (33.5, "world", "the wide view, the end card"),
]

PHRASES = [(["May no one ever feel lonely"], (19.8, 20.8, 23.4, 24.2), False, "light", "rise")]

ARCH = dict(lit_start=[3, 4, 5, 6, 7, 8, 9])
EXPRESSIONS = [
    dict(label="Greeting", t_in=10.2, read0=11.6, read1=16.2, t_out=17.5, act="greeting", at=(0.0, -30.0),
         facing=0.0, answer="peace_ring", frac=0.36),
    dict(label="Consideration", t_in=25.0, read0=26.4, read1=30.8, t_out=32.0, act="consideration",
         at=(0.0, -30.0), facing=0.0, frac=0.40),
]

SIG_TEXT = [(20.0, 28.0)]

# Song 7's look (DESIGN-SYSTEM): a blue dusk turning to a deep navy night
LOOKS = dict(
    dusk=dict(base="dusk", hills=0.0, stars=0.6, milky=0.3, clouds=0.18, haze=0.3, haze_color="#1a2448",
              mist=0.28, mist_color="#3a4c80", sky_top="#0d1b42", sky_mid="#26407a", sky_hor="#d8946e",
              water="#04060e", ripple=0.25, dust=0.9, bokeh=0.9, rays=0.35, sun_glow=0.3, sun_disc=3.5),
    night=dict(base="night", hills=0.0, stars=0.9, milky=0.5, clouds=0.12, haze=0.3, haze_color="#101838",
               mist=0.25, mist_color="#1e2a58", sky_top="#050a1e", sky_mid="#0f1b42", sky_hor="#7a6a90",
               water="#02030a", ripple=0.25, dust=0.9, bokeh=0.9, rays=0.2),
)
LOOK_KEYS = [(0.0, "dusk", 0.0), (24.5, "night", 6.0)]
SUN = dict(el=[(0.0, -1.5), (40.0, -5.0)], az=180.0, int=[(0.0, 0.35), (40.0, 0.15)], rays=[(0.0, 0.25), (40.0, 0.1)])
HOLD_VIEW = ((0.0, 3.0, 20.0), (0.0, 3.0, -200.0))

# the stage (modules/kit_stage.py): on the mirror sea beyond the place of the acts (they are at z = -30)
STAGE = dict(
    at=(0.0, 0.0, -110.0),
    wake=1.0,
    choir_in=8.0,
    breath_in=(14.0, 17.5),
    glow_hits=[17.5, 32.0, LAST_CHORD],
    bursts=[24.5],
    hero_acts=[("raise", 24.5, 24.5, 29.0)],
    perform=[(0.0, 8.0, "Orchestra"), (8.0, 36.0, "Choir and orchestra"), (36.0, 40.0, "Silence")],
)
