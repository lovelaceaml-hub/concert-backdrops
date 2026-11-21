"""Song 05, version 2: the one place where stage time and reference time meet.

Stage time t: seconds of the stage video (60 fps). The music part is exactly the live length, 159.0 s
(DESIGN-SYSTEM section 4), then a 15 s calm hold: 174.0 s, 10440 frames.
Reference time r: seconds of the organisers' recording (153.152 s), on which the scene, the people and the
words are authored. The live arrangement is longer by 5.85 s (more than 1 s), and nothing tells which sections
the choir and orchestra take slower, so every section is scaled by the same factor K: t = K * r. Hits stay in
the same proportional places. This is an estimate until a rehearsal recording exists.
No em dash or en dash anywhere in this file.
"""
REF_LENGTH = 153.152
LIVE = 159.0
HOLD = 15.0
FPS = 60
K = LIVE / REF_LENGTH
TOTAL = LIVE + HOLD                      # 174.0 s of stage video
NFRAMES = int(round(TOTAL * FPS))        # 10440
TOTAL_REF = TOTAL / K                    # the scene runs this long in reference time


def ref(t):
    """Reference time for stage time t."""
    return t / K


def stage(r):
    """Stage time for reference time r."""
    return r * K
