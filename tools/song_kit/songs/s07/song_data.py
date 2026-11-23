"""Song 07 "May No One Ever Feel Lonely" on the song kit (design: project-docs/designs/07 May No One Ever Feel
Lonely.md, "No Light Left Alone"). The recording is the catalog's chosen one (church upload, Drive file
1wL9dyLETDn3q9ECkIXKrDb3UIt_eAgEA, 246.5 s, silent from about 243.5 s), used unstretched as for Song 11.
Times are recording seconds. The design's sections were measured from loudness; line times are the design's
estimates, to be locked to the measured hits (TIMING below) before the full render.
No em dash or en dash anywhere in this file.
"""
TITLE = "May No One Ever Feel Lonely"
CATALOG_ID = "s07"
AUDIO_SHA256 = "2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a"
LIVE = 244.0                    # the music (silent by 4:04)
HOLD = 15.0                     # the calm hold for the hand-off to song 08
MUSIC_END = 243.5
LAST_CHORD = 236.0              # the song settles; no end card mid-concert (END_CARD False)
END_CARD = False
OPENING_END = 12.0
INTRO_FULL = 13.5               # the arrangement fills in (measured)
SETS = ["s07_world"]

# measured sections (design section 3): fill-in 13.5; lifts 53 to 77, 111 to 136, 174 to 224 (loudest 209 to 223);
# hush 137 to 147; ending 224 to 244
HIT = dict(fill=13.5, lift1=53.0, lift2=111.0, hush=137.0, verse3=148.0, lift3=174.0, peak=209.0, settle=224.0)
SLAMS = [53.0, 111.0, 174.0]
KEY_MOMENTS = [(53.0, 2.0), (62.5, 1.6), (74.5, 1.6), (111.0, 2.4), (148.0, 2.0), (174.0, 2.4), (209.0, 3.0),
               (221.0, 3.0)]
LEVELS = [(0.0, 0.10), (13.5, 0.30), (25.0, 0.25), (37.0, 0.30), (53.0, 0.70), (78.0, 0.30), (80.0, 0.40),
          (111.0, 0.75), (137.0, 0.08), (148.0, 0.40), (174.0, 0.80), (209.0, 1.0), (224.0, 0.45), (236.0, 0.15),
          (244.0, 0.05)]
GLORY = [(0.0, 0.18), (13.5, 0.25), (53.0, 0.40), (78.0, 0.35), (111.0, 0.55), (137.0, 0.45), (148.0, 0.55),
         (174.0, 0.75), (209.0, 1.0), (224.0, 0.85), (244.0, 0.6), (259.0, 0.55)]
CONSTELLATIONS = []             # Song 7 keeps the sky for the first stars and the arch
LANTERN_SPANS = [(111.0, 137.0), (188.0, 236.0)]
BAR_GLOWS = [(53.0, 77.0, 2.0), (174.0, 224.0, 2.0)]
BRIGHT_FROM = 1e9

# the edit: who owns each stretch ("world" is s07_world.py; "love" the kit's close shots of the acts)
EDIT = [
    (0.0, "world", "blue dusk: down the long path, the lone traveler walks"),
    (13.5, "world", "the passers-by; the traveler sits on the bench"),
    (25.0, "world", "Mother's wish: footprints of light along the path"),
    (37.0, "world", "the refrain: the village answers; one passer-by turns back"),
    (50.5, "world", "the helper reaches the bench"),
    (53.0, "love", "GREETING: a slight bow, kneeling to eye level"),
    (63.0, "world", "the first peace ring across the lake"),
    (65.0, "love", "CONSIDERATION: the bundle lifted, the hand offered"),
    (75.0, "world", "the second peace ring; they walk on together"),
    (80.0, "world", "verse 2: mist rises; lost lights drift on the water"),
    (96.0, "world", "Mother seen from behind, holding her lamp up"),
    (111.0, "world", "the river of lanterns from the air"),
    (124.0, "world", "the lost are reached; reunions on the shore"),
    (137.0, "world", "the hush: a perfect mirror, everyone still"),
    (148.0, "world", "verse 3: the clouds part on the kingdom"),
    (161.0, "world", "heavenly dawn; heads turn upward"),
    (174.0, "world", "joined hands: one river of light"),
    (187.0, "world", "the bridge of light; Mother leads the way"),
    (201.0, "world", "the procession crosses into the sky"),
    (224.0, "world", "the gate; the last two look back"),
    (236.0, "world", "the hold: deep navy night, the lake still"),
]

# Mother's wishes (pearl italic) and the singer's line (gold): the lyric fragments of design section 8
PHRASES = [
    (["“on the path to heaven”"], (26.0, 27.4, 34.6, 36.2), False, "light", "rise"),
    (["our Mother’s earnest wish"], (38.0, 39.4, 46.0, 47.6), False, "people", "rise"),
    (["“please return”"], (80.6, 82.0, 89.0, 90.6), False, "fly", "rise"),
    (["“the eternal kingdom”"], (148.6, 150.2, 158.2, 160.0), False, "light", "rise"),
    (["my heavenly home"], (209.4, 211.0, 219.0, 221.0), True, "people", "rise"),
]
PHRASE_GLOW = ["gold", "gold", "sky", "lavender", "gold"]

ARCH = dict(lit_start=[3, 4, 5, 6, 7, 8, 9])      # star 1 lit for the first time here; star 8 relit
EXPRESSIONS = [
    dict(label="Greeting", t_in=53.2, read0=54.6, read1=61.0, t_out=62.5, act=None, at=(6.0, -36.3), facing=0.0,
         answer="peace_ring", frac=0.34),
    dict(label="Consideration", t_in=65.4, read0=66.8, read1=73.0, t_out=74.5, act=None, at=(6.0, -36.3),
         facing=0.0, answer="peace_ring", frac=0.40),
]

SIG_TEXT = [(40.0, 48.0), (84.0, 92.0), (126.0, 134.0), (166.0, 174.0), (228.0, 236.0)]

# Song 7's look (DESIGN-SYSTEM table and design section 5): blue dusk on a long path home: twilight blue, coral
# and lantern gold, the first stars and mist; silver-blue mist in verse 2; a clear dark blue hush; a heavenly
# rose and pearl dawn in verse 3; lantern gold over a twilight lake at the climax; deep navy night (#0B1530)
LOOKS = dict(
    dusk=dict(base="dusk", hills=0.0, stars=0.45, milky=0.2, clouds=0.15, haze=0.3, haze_color="#1a2448",
              mist=0.30, mist_color="#3a4c80", sky_top="#0d1b42", sky_mid="#26407a", sky_hor="#d8946e",
              water="#04060e", ripple=0.25, dust=0.9, bokeh=0.9, rays=0.3, sun_glow=0.3, sun_disc=3.0),
    twilight=dict(base="dusk", hills=0.0, stars=0.7, milky=0.35, clouds=0.15, haze=0.3, haze_color="#14204a",
                  mist=0.28, mist_color="#2e4078", sky_top="#0a1638", sky_mid="#20386f", sky_hor="#b98089",
                  water="#03050c", ripple=0.25, dust=0.9, bokeh=0.9, rays=0.25, sun_glow=0.25, sun_disc=3.0),
    mist=dict(base="night", hills=0.0, stars=0.6, milky=0.3, clouds=0.12, haze=0.45, haze_color="#2a3460",
              mist=0.55, mist_color="#8a9ac8", sky_top="#081230", sky_mid="#1c2c60", sky_hor="#6a7aa8",
              water="#03050c", ripple=0.2, dust=0.9, bokeh=0.9, rays=0.15),
    hush=dict(base="night", hills=0.0, stars=1.0, milky=0.6, clouds=0.0, haze=0.12, haze_color="#0e1838",
              mist=0.0, sky_top="#040a1e", sky_mid="#0c1840", sky_hor="#2a3a70", water="#01020a", ripple=0.0,
              dust=0.5, bokeh=0.5, rays=0.0),
    dawn=dict(base="sunrise", hills=0.0, stars=0.3, clouds=0.3, haze=0.35, haze_color="#6a4a78", mist=0.15,
              mist_color="#8a6a8a", sky_top="#121c58", sky_mid="#6e4c90", sky_hor="#f0a088", sun_color="#ffd8b0",
              water="#080a20", ripple=0.25, sun_glow=0.3, sun_disc=3.5, dust=0.9, bokeh=0.9, rays=0.45,
              exposure=0.86),
    gold=dict(base="dusk", hills=0.0, stars=0.5, clouds=0.25, haze=0.3, haze_color="#2a2448", mist=0.2,
              mist_color="#5a4a78", sky_top="#0a1640", sky_mid="#2a3a7a", sky_hor="#e8a868", water="#04060e",
              ripple=0.25, dust=0.9, bokeh=0.9, rays=0.55, sun_glow=0.4, sun_disc=4.0, exposure=0.9),
    navy=dict(base="night", hills=0.0, stars=0.95, milky=0.5, clouds=0.0, haze=0.15, haze_color="#0b1530",
              mist=0.05, mist_color="#1a2a58", sky_top="#0b1530", sky_mid="#10204a", sky_hor="#2a3a6a",
              water="#02030a", ripple=0.0, dust=0.6, bokeh=0.6, rays=0.0),
)
LOOK_KEYS = [(0.0, "dusk", 0.0), (25.0, "twilight", 10.0), (80.0, "mist", 6.0), (137.0, "hush", 3.0),
             (148.0, "dawn", 8.0), (174.0, "gold", 6.0), (224.0, "gold", 0.0), (232.0, "navy", 8.0)]
SUN = dict(el=[(0.0, -1.0), (80.0, -4.0), (148.0, -3.0), (174.0, 1.5), (224.0, 2.0), (240.0, -8.0)], az=180.0,
           int=[(0.0, 0.35), (80.0, 0.12), (137.0, 0.0), (148.0, 0.35), (174.0, 0.55), (230.0, 0.4), (240.0, 0.0)],
           rays=[(0.0, 0.2), (80.0, 0.1), (137.0, 0.0), (148.0, 0.4), (209.0, 0.6), (232.0, 0.0)])
HOME = (0.0, 0.0, -420.0)
HILLS = ("#0a1230", "#3a4a80")
HOLD_VIEW = ((0.0, 2.2, 14.0), (0.0, 4.0, -400.0))
