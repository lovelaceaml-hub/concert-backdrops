"""Song 07 clocks. The scene is authored on the REFERENCE clock (the church's recording, measured).

Since 2026-11-23 the stage video follows the Song 11 method: the recording is used as it is, with no time
stretching ("Audio is not time-stretched", Song 11 renewed). The earlier version 2 conformed 0 to 243.5 s
evenly onto an estimated live length of 238.0 s; set LIVE = 238.0 to reproduce that historical mapping.

    live 0 .. LIVE          ->  reference 0 .. REF_MUSIC (identity while LIVE == REF_MUSIC)
    live LIVE .. TOTAL      ->  reference REF_MUSIC .. REF_MUSIC + HOLD (the calm hold, at normal speed)

No em dash or en dash anywhere in this file.
"""
REF_MUSIC = 243.5       # the recording is silent from here (measured)
LIVE = REF_MUSIC        # no time stretching (Song 11 method); version 2 used 238.0
HOLD = 15.0             # calm hold after the music (Anthony, 2026-11-18)
TOTAL = LIVE + HOLD     # 258.5 s, 15510 frames at 60 fps
K = REF_MUSIC / LIVE    # 1.0
FPS = 60


def ref(t_live):
    t = float(t_live)
    return t * K if t <= LIVE else REF_MUSIC + (t - LIVE)


def live(t_ref):
    t = float(t_ref)
    return t / K if t <= REF_MUSIC else LIVE + (t - REF_MUSIC)
