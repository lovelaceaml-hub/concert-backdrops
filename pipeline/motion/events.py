"""Musical event envelopes and deterministic closed-form secondary motion."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .math3d import finite_number, smootherstep


def event_envelope(frame, events, *, fps=60.0, kind=None, cap=None):
    """C2 attack/release, peaking exactly at an authored fractional hit frame.

    attack_frames and release_frames are lengths, not seconds. Defaults are
    0.25 seconds of attack and 1.2 seconds of release at the supplied fps. A cap
    uses a smooth saturation knee from cap/2 to cap. It changes large amplitudes;
    leave cap=None when exact additive event amplitude is required.
    """
    frame = finite_number(frame, "frame")
    fps = finite_number(fps, "fps")
    if fps <= 0:
        raise ValueError("fps must be positive")
    total = 0.0
    for event in events:
        if kind is not None and event.get("kind") != kind:
            continue
        hit = finite_number(event["frame"], "event.frame")
        attack = finite_number(event.get("attack_frames", max(1, math.floor(fps * 0.25 + 0.5))), "attack_frames")
        release = finite_number(event.get("release_frames", max(1, math.floor(fps * 1.2 + 0.5))), "release_frames")
        amplitude = finite_number(event.get("amplitude", 1.0), "amplitude")
        if attack <= 0 or release <= 0 or amplitude < 0:
            raise ValueError("event attack/release must be positive and amplitude nonnegative")
        if hit - attack <= frame <= hit:
            total += amplitude * smootherstep((frame - hit + attack) / attack)
        elif hit < frame <= hit + release:
            total += amplitude * (1.0 - smootherstep((frame - hit) / release))
    if cap is None:
        return total
    cap = finite_number(cap, "cap")
    if cap <= 0:
        raise ValueError("cap must be positive")
    if total <= cap * 0.5:
        return total
    if total >= cap:
        return cap
    u = (total - cap * 0.5) / (cap * 0.5)
    knee = u + 4.0 * u ** 3 - 7.0 * u ** 4 + 3.0 * u ** 5
    return cap * 0.5 * (1.0 + knee)


@dataclass(frozen=True)
class SpringSample:
    value: float
    velocity: float


class DampedSpring:
    """Solve x'' + 2*zeta*w*x' + w*w*(x-target) = 0 from fixed cues.

    Cues are (seconds, target) changes, in strictly increasing order. Evaluation
    replays their closed-form segments, never advances mutable render state.
    Position and velocity remain continuous at a target change; acceleration
    changes there. Use the C2 event envelope instead when that change is visible.
    """

    def __init__(self, cues=(), *, frequency_hz=1.5, damping_ratio=0.75, initial=0.0, start_seconds=0.0):
        self.frequency_hz = finite_number(frequency_hz, "frequency_hz")
        self.damping_ratio = finite_number(damping_ratio, "damping_ratio")
        self.initial = finite_number(initial, "initial")
        self.start_seconds = finite_number(start_seconds, "start_seconds")
        if self.frequency_hz <= 0 or self.damping_ratio < 0:
            raise ValueError("spring frequency must be positive and damping nonnegative")
        self.cues = tuple((finite_number(t, "cue time"), finite_number(v, "cue target")) for t, v in cues)
        if any(t < self.start_seconds for t, _ in self.cues) or any(b[0] <= a[0] for a, b in zip(self.cues, self.cues[1:])):
            raise ValueError("spring cue times must increase and follow start_seconds")

    def _advance(self, x, v, target, seconds):
        w, z = math.tau * self.frequency_hz, self.damping_ratio
        displacement = x - target
        if z < 1.0 - 1e-7:
            alpha = z * w
            wd = w * math.sqrt(1.0 - z * z)
            a, b = displacement, (v + alpha * displacement) / wd
            c, s, decay = math.cos(wd * seconds), math.sin(wd * seconds), math.exp(-alpha * seconds)
            y = decay * (a * c + b * s)
            velocity = decay * ((-alpha * a + wd * b) * c + (-alpha * b - wd * a) * s)
        elif z <= 1.0 + 1e-7:
            a, b = displacement, v + w * displacement
            decay = math.exp(-w * seconds)
            y = (a + b * seconds) * decay
            velocity = (b - w * (a + b * seconds)) * decay
        else:
            r1, r2 = -w * (z - math.sqrt(z * z - 1.0)), -w * (z + math.sqrt(z * z - 1.0))
            a = (v - r2 * displacement) / (r1 - r2)
            b = displacement - a
            e1, e2 = math.exp(r1 * seconds), math.exp(r2 * seconds)
            y, velocity = a * e1 + b * e2, a * r1 * e1 + b * r2 * e2
        return x if seconds == 0 else target + y, v if seconds == 0 else velocity

    def sample(self, seconds) -> SpringSample:
        t = finite_number(seconds, "sample time")
        if t <= self.start_seconds:
            return SpringSample(self.initial, 0.0)
        x, v, target, previous = self.initial, 0.0, self.initial, self.start_seconds
        for cue_time, cue_target in self.cues:
            if cue_time > t:
                break
            x, v = self._advance(x, v, target, cue_time - previous)
            previous, target = cue_time, cue_target
        x, v = self._advance(x, v, target, t - previous)
        return SpringSample(x, v)
