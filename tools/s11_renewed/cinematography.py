"""A new camera cut of Song 11, installed only in the rendering process.

The musical clock, scene identities and phrase times remain the source film's.
Selected views are newly composed: an approach over water, a readable ascent
beside the church, progressively higher views of Zion, an ensemble rather than
instrument-level lens, and complete clothed conductor silhouettes. The camera
is steady enough for the performance and architecture to supply the movement.

Call install(song) before constructing the Renderer, then rebuild the song's
phrase objects and cut bursts. No historical source file is modified.
"""
from __future__ import annotations

from types import MethodType

import numpy as np


VERSION = "s11-renewed-camera-v1"


def _one(shots, start):
    matches = [shot for shot in shots if abs(shot["t0"] - start) < 1e-7]
    if len(matches) != 1:
        raise ValueError(f"Expected one Song 11 shot at {start}, found {len(matches)}.")
    return matches[0]


def _retime(shot, start, end):
    """Retain a path's spatial shape while changing its joint edit boundary."""
    old_start, old_end = shot["t0"], shot["t1"]
    shot["keys"] = [
        (start + (time - old_start) / (old_end - old_start) * (end - start), pos, target)
        for time, pos, target in shot["keys"]
    ]
    shot["t0"], shot["t1"] = start, end


def _correct_recorded_cut(song):
    """Correct the documented early camera cut, without moving its phrase cues."""
    before = _one(song.SHOTS, 70.54)
    after = _one(song.SHOTS, 74.56)
    core = _one(song.CORE_SHOTS, 70.54)
    church = _one(song.S_CHURCH.SHOTS, 74.56)
    if not (before["kind"] == core["kind"] == "globe"
            and abs(before["t1"] - 74.56) < 1e-7
            and abs(core["t1"] - 74.56) < 1e-7
            and abs(after["t1"] - 75.2) < 1e-7
            and abs(church["t1"] - 75.2) < 1e-7):
        raise ValueError("The recorded 74.56-second joint no longer matches the source.")
    entries = [i for i, entry in enumerate(song.EDIT)
               if abs(entry[0] - 74.56) < 1e-7 and entry[1] == "church"]
    if len(entries) != 1:
        raise ValueError("The core edit does not contain the expected church boundary.")
    index = entries[0]
    song.EDIT[index] = (74.70, *song.EDIT[index][1:])
    song.EDIT_T[:] = [entry[0] for entry in song.EDIT] + [song.TOTAL + 1.0]
    song.BLOCKS[index - 1]["t1"] = 74.70
    song.BLOCKS[index]["t0"] = 74.70
    for shot in (before, core):
        _retime(shot, 70.54, 74.70)
    for shot in (after, church):
        _retime(shot, 74.70, 75.2)
        shot["blend"] = 0.0   # a clear cut, without a spatial blend through the Earth
        shot["roll"] = 0.0
    song.S_CHURCH._B[:] = [
        (74.70 if abs(start - 74.56) < 1e-7 else start, end, note)
        for start, end, note in song.S_CHURCH._B
    ]
    song._SHOT_T0[:] = [shot["t0"] for shot in song.SHOTS]
    song.CUTS[:] = [shot["t0"] for shot in song.SHOTS[1:]]


def _author(song, start, frames, *, fov, purpose, aperture=0.0,
            roll=(0.0, 0.0), focus="target", pace="glide"):
    shot = _one(song.SHOTS, start)
    shot.update(
        keys=[(shot["t0"] + u * (shot["t1"] - shot["t0"]),
               np.asarray(pos, dtype=np.float64), np.asarray(target, dtype=np.float64))
              for u, pos, target in frames],
        fov=float(fov), aperture=float(aperture), roll=roll, focus=focus,
        pace=pace, blend=0.0, renewed_purpose=purpose,
    )
    shot.pop("clipped", None)


def _arc(song, start, a0, a1, r0, r1, h0, h1, look0, look1, *, fov, purpose):
    """An authored arc around Zion, with its front and church retained in view."""
    frames = []
    for u in np.linspace(0.0, 1.0, 5):
        a = np.radians(a0 + (a1 - a0) * u)
        r = r0 + (r1 - r0) * u
        pos = song.ZC + np.array([r * np.sin(a), h0 + (h1 - h0) * u, r * np.cos(a)])
        target = song.ZC + (1.0 - u) * np.asarray(look0) + u * np.asarray(look1)
        frames.append((u, pos, target))
    _author(song, start, frames, fov=fov, purpose=purpose, roll=(-1.0, 1.0))


def _glide(start, end, accents):
    """Bounded camera acceleration with a small broad surge on major accents."""
    times = np.linspace(start, end, 100)
    u = (times - start) / (end - start)
    velocity = 0.32 + 0.68 * np.sin(np.pi * u) ** 2
    for hit in accents:
        if start < hit < end:
            velocity += 0.12 * np.exp(-0.5 * ((times - hit) / 0.4) ** 2)
    progress = np.r_[0.0, np.cumsum(0.5 * (velocity[1:] + velocity[:-1]) * np.diff(times))]
    progress /= progress[-1]
    return lambda t: float(np.interp(t, times, progress))


def _restrained_roll(value):
    if callable(value):
        return lambda t: float(np.clip(0.24 * value(t), -3.0, 3.0))
    if isinstance(value, (tuple, list)):
        return tuple(float(np.clip(0.24 * angle, -3.0, 3.0)) for angle in value)
    return float(np.clip(0.24 * value, -3.0, 3.0))


def install(song):
    """Install the new compositions and return a small, source-readable receipt."""
    if getattr(song, "_renewed_camera_version", None) == VERSION:
        return song._renewed_camera_receipt
    _correct_recorded_cut(song)
    y, fz = float(song.SUMMIT), float(song.FACADE_Z)
    v = lambda x, h, z: np.array([x, h, z], dtype=np.float64)
    stage = lambda x, h, z: v(x, y + h, fz + z)
    hero = lambda x, h, z: song.S_DANCE.COND_C + v(x, h, z)
    zion = lambda x, h, z: song.ZC + v(x, h, z)

    # One continuous approach: nearby water first, then the inhabited terraces,
    # then the church. The rising path clears every terrace instead of weaving
    # left and right through the avenue. Its first point meets the title shot.
    _author(song, 11.9, [
        (0.0, v(2, 8.6, 800), v(0, 175, -420)),
        (0.25, v(22, 10, 380), v(0, 125, -420)),
        (0.50, v(30, 25, -35), stage(0, 35, -13)),
        (0.72, v(28, 58, -180), stage(0, 31, -13)),
        (1.0, stage(18, 7, 62), stage(0, 30, -13)),
    ], fov=54, purpose="Water foreground opens into an inhabited architectural arrival", pace="linear")
    _author(song, 31.11, [
        (0.0, stage(-75, 10, 88), stage(0, 25, -10)),
        (0.5, stage(-68, 35, 78), stage(0, 34, -12)),
        (1.0, stage(-48, 65, 72), stage(0, 45, -14)),
    ], fov=48, purpose="A single rising three-quarter view reveals glass, canopy and tower")

    # The three scales of Zion develop from the crown to the inhabited lower
    # terraces, then to a broader second climb and a final summit gathering.
    # Keep the entire crown below the two-line glory phrase. A higher aim gives
    # the words clear starry sky, while a wider, more distant arc still retains
    # the church below the circlet instead of cropping it out of the frame.
    _arc(song, 53.78, 31, 19, 480, 440, 240, 210, (0, 268, -12), (0, 270, -8),
         fov=54, purpose="Crown and church stay beneath the glory phrase in an elevated three-quarter view")
    _arc(song, 64.2, -44, -14, 430, 330, 38, 105, (0, 32, 0), (0, 58, 0),
         fov=52, purpose="Terraces fill during a steady diagonal ascent")
    _author(song, 86.7, [
        (0.0, zion(-70, 12, 1120), zion(0, 53, 0)),
        (0.5, zion(-52, 14, 840), zion(0, 56, 0)),
        (1.0, zion(-28, 22, 550), zion(0, 60, 0)),
    ], fov=54, purpose="Rings pass in the water foreground while Zion remains the destination")
    _arc(song, 90.72, -34, 18, 490, 280, 52, 124, (0, 38, 0), (0, 75, 0),
         fov=52, purpose="First climb reveals people and successive terraces without a fast spin")
    _author(song, 103.6, [
        (0.0, zion(60, 98, 205), zion(8, 28, 220)),
        (1.0, zion(52, 84, 246), zion(6, 22, 242)),
    ], fov=50, purpose="A measured descent beside the waterfall keeps its scale readable")
    _arc(song, 165.16, 26, 18, 430, 680, 24, 28, (0, 100, -8), (0, 106, -8),
         fov=50, purpose="Shockwave travels over water; the city stays below the upper phrase")
    _arc(song, 171.48, -28, 24, 500, 320, 90, 190, (0, 42, 0), (0, 72, 0),
         fov=52, purpose="Second climb rises higher to reveal the larger gathering")

    # A concert lens: gold instruments, blue people and the choir read as one
    # coordinated ensemble. These paths remain outside the performers' rows.
    stage_plans = [
        (26.33, [(-13, 3.7, 40), (-9, 4.0, 36), (-5, 4.6, 32)],
         [(-2, 2.6, 17), (-1, 2.8, 15), (0, 3.0, 12)], 48,
         "Reveal the strings with lateral parallax into the choir"),
        (82.08, [(-8, 3.8, 38), (-7, 6.0, 41), (-4, 9.0, 46)],
         [(0, 3.4, 14), (0, 4.2, 13), (0, 5.2, 11)], 52,
         "First musical release opens steadily across the complete stage"),
        (105.14, [(9, 3.6, 32), (8, 4.0, 31), (6.7, 4.6, 30)],
         [(2.5, 3.2, 17), (2, 3.2, 16), (1.5, 3.2, 15)], 44,
         "Brass and strings keep instrument and performer in the same frame"),
        (162.86, [(9, 4.5, 39), (7, 6.5, 41), (5, 9, 44)],
         [(0, 3.5, 14), (0, 4.2, 12), (0, 5.2, 11)], 52,
         "Second musical release answers the first from the other side"),
        (183.0, [(10, 4.2, 32), (9, 4.7, 31), (8, 5.2, 30)],
         [(3.5, 3.1, 17), (3, 3.3, 16), (2.5, 3.5, 15)], 44,
         "A calm oblique brass view shows coordinated playing"),
        (238.8, [(-9, 4.4, 42), (-6.5, 5.0, 39), (-4, 5.5, 36)],
         [(0, 4.2, 9), (0, 4.3, 8), (0, 4.4, 7)], 48,
         "Return home through the orchestra while keeping the choir whole"),
        (249.43, [(-4, 5.5, 32), (-2, 8.0, 37), (0, 11.0, 44)],
         [(0, 4.0, 7), (0, 5.5, 7), (0, 8.0, 6)], 52,
         "Final release rises above the ensemble without a spinning reversal"),
    ]
    for start, positions, targets, fov, purpose in stage_plans:
        _author(song, start, [(u, stage(*p), stage(*q))
                             for u, p, q in zip((0.0, 0.5, 1.0), positions, targets)],
                fov=fov, purpose=purpose, aperture=0.006)

    # The conductor is a complete person in a coat, not a cropped body detail.
    # Camera height stays above the waist; the feet, raised hands and baton
    # remain in the frame. The heart view leaves the phrase its own open sky.
    hero_plans = [
        (97.7, (4.1, 1.45, 6.8), (3.8, 1.50, 6.4), (0, 1.20, -0.2), (0, 1.26, -0.2), 42,
         "Whole conductor initiates the rising ribbons against Zion"),
        (117.0, (-4.2, 1.50, 6.2), (-3.6, 1.55, 5.8), (-0.1, 1.15, 0), (-0.1, 1.20, 0), 40,
         "A quiet full-figure arc lets the breath and coat settle"),
        (121.32, (4.5, 1.70, 7.4), (3.7, 1.75, 6.8), (-0.2, 1.25, -0.4), (-0.2, 1.30, -0.4), 44,
         "The strings cue reads through arms, stance and the complete baton"),
        (185.92, (3.8, 1.65, -8.8), (3.5, 1.70, -8.5), (2.4, 2.10, 1.2), (2.3, 2.15, 1.2), 46,
         "Conductor remains to the right of the words beneath the drawn heart"),
        (247.5, (-3.5, 1.50, -7.0), (-3.2, 1.55, -6.7), (0, 1.22, 0), (0, 1.40, 0), 42,
         "Fermata holds the full silhouette before the final release"),
    ]
    hero_focus = hero(0, 1.35, 0)
    for start, p0, p1, q0, q1, fov, purpose in hero_plans:
        _author(song, start, [(0.0, hero(*p0), hero(*q0)), (1.0, hero(*p1), hero(*q1))],
                fov=fov, purpose=purpose, aperture=0.009, focus=hero_focus)

    _author(song, 201.73, [
        (0.0, v(-95, 14, 180), zion(8, y + 18, -35)),
        (0.5, v(-80, 32, 140), zion(12, y + 22, -35)),
        (1.0, v(-60, 56, 90), zion(16, y + 25, -35)),
    ], fov=52, purpose="Sunrise opens above a dark water foreground and distinct skyline")
    sky = song.S_CODA.SKY_C
    sky_frames = []
    for u in np.linspace(0.0, 1.0, 5):
        angle = np.radians(48.0 - 34.0 * u)
        radius = 31.0 - 4.0 * u
        sky_frames.append((u, sky + v(radius * np.sin(angle), 9.0 + u, radius * np.cos(angle)),
                           sky + v(0, 1.2, 1.0)))
    _author(song, 205.98, sky_frames, fov=48,
            purpose="Cloud orchestra is revealed in one unbroken shallow arc")
    _author(song, 211.6, [
        (0.0, stage(-70, 110, 270), stage(0, 44, 10)),
        (0.5, stage(-55, 96, 230), stage(0, 43, 10)),
        (1.0, stage(-35, 80, 190), stage(0, 42, 10)),
    ], fov=52, purpose="The final summit gathering resolves the rising Zion progression")

    # Rebuild the moves in the existing rig so P3D, word helpers and every scene
    # keep the same camera object. Retain linear tracking of the procession.
    camera = song.CAMERA
    moves = []
    for shot in song.SHOTS:
        original_pace = shot.get("pace", "music")
        pace = (_glide(shot["t0"], shot["t1"], song.SLAMS)
                if original_pace in ("music", "glide") else
                None if original_pace in (None, "linear") else original_pace)
        roll = shot.get("roll", 0.0)
        if "renewed_purpose" not in shot:
            roll = _restrained_roll(roll)
        aperture = shot.get("aperture", 0.0)
        if shot["kind"] == "stage":
            aperture = min(float(aperture), 0.008)
        move = song.fly(shot["keys"], blend=float(shot.get("blend", 0.0)),
                        fov=shot["fov"], aperture=aperture,
                        focus=shot.get("focus", "target"), roll=roll, pace=pace)
        if shot.get("clipped"):
            move.t0, move.t1 = shot["t0"], shot["t1"]
        moves.append(move)
    camera.moves = moves
    camera.handheld = 0.015
    camera.shake = lambda t: 0.055 * song.hit_pulse(t, song.SLAMS, rise=0.04, fall=0.22)
    camera._table = None

    def state(self, t, aspect=16.0 / 9.0):
        # Use the base rig to remove the original per-beat lens pumping. A broad,
        # small emphasis remains at the three structural musical releases.
        value = song.Rig.state(self, t, aspect)
        accent = max(np.exp(-0.5 * ((t - hit - 0.08) / 0.33) ** 2) for hit in song.SLAMS)
        value.fov *= 1.0 - 0.015 * float(accent)
        return value

    camera.state = MethodType(state, camera)
    receipt = dict(version=VERSION, shots=len(song.SHOTS),
                   redesigned=[dict(start=shot["t0"], end=shot["t1"],
                                    purpose=shot["renewed_purpose"])
                               for shot in song.SHOTS if "renewed_purpose" in shot],
                   corrected_cut=dict(previous=74.56, current=74.70, phrase_times_unchanged=True),
                   camera_object_preserved=True, picture_delay_applied_here=False)
    song._renewed_camera_version = VERSION
    song._renewed_camera_receipt = receipt
    return receipt
