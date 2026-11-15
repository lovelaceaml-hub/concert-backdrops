"""Engine test only (UPGRADE-HOWTO J): the original song 03 timeline with a different text animation on each
expression, the title, the end card lines and one fragment. Render stills with audio/test/silent-60s.mp3."""
import songs.s03_original as _base

for _p, _a in zip(_base.PHRASES, ["ink", "bloom", "rise", "ribbon", "constellation", "petal", "snow", "wave",
                                  "bloom"]):
    _p["anim"] = _a
_base.TITLE["anim"] = "constellation"
_base.TAGLINE["anim"] = "ink"
_base.FRAGMENTS = [dict(text="a quiet word of light", t0=100.0, t1=103.0, out=110.0, dy=-0.02, size=84,
                        anim="petal")]
_base.BOTTOM_CALM = 1.0
from songs.s03_original import *  # noqa: E402,F401,F403
