"""Opt-in delivery quality, independent of any song or graphics context."""
from __future__ import annotations

from copy import copy
from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

Focus = tuple[float, float, float] | Callable[[float], tuple[float, float, float] | None]


@dataclass(frozen=True)
class QualityOptions:
    """Renderer quality controls. Defaults preserve the existing shader and frame path.

    grain: True keeps the original synthetic output grain; False removes it.
    bloom_scale: Final bloom multiplier, default 1.0.
    sun_scale: World sun intensity multiplier, default 1.0.
    rays_scale: World sun-ray multiplier, default 1.0.
    sun_glow_scale: World sun halo multiplier, default 1.0.
    grade_when: Optional time predicate limiting light scaling and aperture_cap.
    subject_focus: World point or time function returning a point (None skips a shot).
        Default None preserves authored focus, without guessing a song's subject.
    subject_aperture: Lens opening in metres for subject shots; None preserves it.
    aperture_cap: Maximum opening for graded shots; None preserves it.
    temporal_samples: Positive integer overriding P3D motion_samples; None inherits it.
    shutter: Frame fraction overriding P3D motion_blur; None inherits it.
    cut_safe: False keeps legacy blur; True disables all blur when a shutter spans a cut.
    cuts: Extra authored cut times, combined with camera rig cuts, default empty.
    """

    grain: bool = True
    bloom_scale: float = 1.0
    sun_scale: float = 1.0
    rays_scale: float = 1.0
    sun_glow_scale: float = 1.0
    grade_when: Callable[[float], bool] | None = None
    subject_focus: Focus | None = None
    subject_aperture: float | None = None
    aperture_cap: float | None = None
    temporal_samples: int | None = None
    shutter: float | None = None
    cut_safe: bool = False
    cuts: tuple[float, ...] = ()

    def __post_init__(self):
        for name in ("grain", "cut_safe"):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be a bool")
        for name in ("bloom_scale", "sun_scale", "rays_scale", "sun_glow_scale",
                     "subject_aperture", "aperture_cap", "shutter"):
            value = getattr(self, name)
            if (value is None and name.endswith("_scale")) or (
                    value is not None and (isinstance(value, bool) or not math.isfinite(value) or value < 0)):
                raise ValueError(f"{name} must be finite and nonnegative")
        n = self.temporal_samples
        if n is not None and (isinstance(n, bool) or not isinstance(n, int) or n < 1):
            raise ValueError("temporal_samples must be a positive integer or None")
        if self.grade_when is not None and not callable(self.grade_when):
            raise ValueError("grade_when must be a time predicate")
        if self.subject_focus is not None and not callable(self.subject_focus):
            self._point(self.subject_focus)
        cuts = tuple(float(t) for t in self.cuts)
        if not all(math.isfinite(t) for t in cuts):
            raise ValueError("cuts must be finite times")
        object.__setattr__(self, "cuts", cuts)

    @classmethod
    def clarity(cls, *, subject_focus: Focus | None = None,
                grade_when: Callable[[float], bool] | None = None,
                cuts: tuple[float, ...] = ()):
        """Song 11 clarity values, with caller-supplied subject and stage selection.

        Grain off, sun/rays 0.65, halo/bloom 0.75, subject aperture 0.012 m,
        other graded shots capped at 0.008 m, two samples, 0.35-frame cut-safe shutter.
        No selector means light grading applies throughout. Subject shots take
        precedence over the aperture cap, as in the approved conductor treatment.
        """
        return cls(grain=False, bloom_scale=0.75, sun_scale=0.65, rays_scale=0.65,
                   sun_glow_scale=0.75, grade_when=grade_when, subject_focus=subject_focus,
                   subject_aperture=0.012, aperture_cap=0.008, temporal_samples=2,
                   shutter=0.35, cut_safe=True, cuts=cuts)

    @staticmethod
    def _point(value):
        p = np.asarray(value, np.float64)
        if p.shape != (3,) or not np.isfinite(p).all():
            raise ValueError("subject_focus must return a finite world point or None")
        return p

    def graded(self, t):
        """Whether light scaling and the non-subject aperture cap apply at t."""
        return self.grade_when is None or bool(self.grade_when(t))

    def world(self, t, state):
        """Scale a fresh world state without changing its source or cached state."""
        scales = (("sun_int", self.sun_scale), ("rays", self.rays_scale),
                  ("sun_glow", self.sun_glow_scale))
        if not self.graded(t) or all(scale == 1.0 for _, scale in scales):
            return state
        result = dict(state)
        for key, scale in scales:
            if scale != 1.0 and key in result:
                result[key] *= scale
        return result

    def parameters(self, t, parameters):
        """Apply final bloom scaling after the song and P3D have adjusted parameters."""
        if self.bloom_scale != 1.0 and self.graded(t):
            parameters["bloom_gain"] = parameters.get("bloom_gain", 1.0) * self.bloom_scale
        return parameters

    def camera(self, t, cam):
        """Focus along the view depth, preserving composition and the authored camera."""
        point = self.subject_focus(t) if callable(self.subject_focus) else self.subject_focus
        focus, aperture = cam.focus, cam.aperture
        if point is not None:
            p = self._point(point)
            direction = np.asarray(cam.target) - np.asarray(cam.pos)
            direction = direction / max(float(np.linalg.norm(direction)), 1e-6)
            focus = max(float(np.dot(p - cam.pos, direction)), 0.02)
            if self.subject_aperture is not None:
                aperture = self.subject_aperture
        elif self.aperture_cap is not None and self.graded(t):
            aperture = min(aperture, self.aperture_cap)
        if focus == cam.focus and aperture == cam.aperture:
            return cam
        result = copy(cam)
        result.focus, result.aperture = focus, aperture
        return result

    def shutter_at(self, t, fps, shutter, rig_cuts=()):
        """Effective shutter, zero on the new-shot side of a cut inside its interval."""
        if self.cut_safe and shutter > 0:
            if any(0 <= t - cut < shutter / fps for cut in (*rig_cuts, *self.cuts)):
                return 0.0
        return shutter
