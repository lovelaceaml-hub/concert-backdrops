"""Song 07 v2 clocks. The scene is authored on the REFERENCE clock (the church's recording, measured);
the stage video runs on the LIVE clock (238.0 s of music, then a 15 s calm hold).

    live 0 .. 238.0      ->  reference 0 .. 243.5 (evenly: every section and hit keeps its proportional place)
    live 238.0 .. 253.0  ->  reference 243.5 .. 258.5 (the calm hold, at normal speed)

No em dash or en dash anywhere in this file.
"""
LIVE = 238.0            # live length of the music (DESIGN-SYSTEM 4)
HOLD = 15.0             # calm hold after the music (Anthony, 2026-11-18)
TOTAL = LIVE + HOLD     # 253.0 s, 15180 frames at 60 fps
REF_MUSIC = 243.5       # the recording is silent from here (measured)
K = REF_MUSIC / LIVE    # 1.023109
FPS = 60


def ref(t_live):
    t = float(t_live)
    return t * K if t <= LIVE else REF_MUSIC + (t - LIVE)


def live(t_ref):
    t = float(t_ref)
    return t / K if t <= REF_MUSIC else LIVE + (t - REF_MUSIC)
