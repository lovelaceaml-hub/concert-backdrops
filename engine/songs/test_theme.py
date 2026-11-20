"""Engine check only (UPGRADE-HOWTO I): the campaign day theme on the song 03 original, cut to 60 seconds.

Navy words with a soft white glow, one coral expression with a gold glow, a coral fragment, a navy end card,
bubbles and leaves on the campaign day sky. Rendered with audio/test/s03-newsong-first-60s.mp3.
"""
import songs.s03_original as _base
import theme
from track import Track

_base.TOTAL = 60.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_T = _base.TOTAL
_base.PHRASES[1]["color"] = theme.CORAL           # Gratitude: coral words with a gold glow
_base.PHRASES[1]["glow"] = theme.GOLD
_base.PHRASES[3].update(form=1e9, hold=1e9, star=1e9)   # Inclusiveness not lit in this check: room for the end card
_base.TITLE = dict(label="Beginning of Peace", lines=["The Words of Mother’s Love"], size=150,
                   form=46.0, hold=1e9, star=1e9)
_base.TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6\nLas Vegas",
                     t0=49.0, t1=52.0)
_base.FRAGMENTS = [dict(text="your love remains", t0=13.0, t1=15.0, out=18.0, dy=-0.16, size=74,
                        color=theme.CORAL_SOFT, glow=theme.GOLD)]
_base.WAVES = [w for w in _base.WAVES if w[0] < _T]
theme.campaign_day(vars(_base), [(0.0, "dawn"), (14.0, "day"), (30.0, "golden"), (42.0, "peach"), (_T, "cream")],
                   total=_T, leaves=0.6)
_base.SUN_INT = Track([(0.0, 0.55), (_T, 0.75)])
_base.SUN_Y = Track([(0.0, 0.40), (_T, 0.46)])
_base.CLOUDS = Track([(0.0, 0.35), (_T, 0.35)])
_base.PETALS = Track([(0.0, 0.0), (_T, 0.0)])
_base.BOTTOM_CALM = 1.0
from songs.s03_original import *  # noqa: E402,F401,F403
