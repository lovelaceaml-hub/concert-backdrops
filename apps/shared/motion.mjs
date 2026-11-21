// Pure frame-time math shared by Three.js and Remotion. No frame history or clocks.
const finite = (value, name) => {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`);
  return value;
};
const vector = (value, name) => {
  if (!Array.isArray(value) || value.length !== 3) throw new Error(`${name} must be an XYZ vector`);
  return value.map((component) => finite(component, name));
};
const mix = (a, b, u) => a + (b - a) * u;
const magnitude = (v) => Math.hypot(...v);
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const normalize = (v) => {
  const length = magnitude(v);
  if (length < 1e-8) throw new Error('Camera position, target and up must define a stable direction');
  return v.map((value) => value / length);
};

export const clamp01 = (value) => Math.min(1, Math.max(0, value));

// Value, velocity and acceleration join a constant at both ends.
export function smootherstep(value) {
  const u = clamp01(finite(value, 'progress'));
  return u * u * u * (u * (u * 6 - 15) + 10);
}

export function frameSeconds(frame, fps, startFrame = 0) {
  finite(frame, 'frame'); finite(startFrame, 'startFrame');
  if (!Number.isFinite(fps) || fps <= 0) throw new Error('fps must be positive');
  return (frame - startFrame) / fps;
}

export function shotProgress(frame, startFrame, endFrameExclusive) {
  finite(frame, 'frame'); finite(startFrame, 'startFrame'); finite(endFrameExclusive, 'endFrameExclusive');
  if (endFrameExclusive <= startFrame) throw new Error('Shot end must follow its start');
  return clamp01((frame - startFrame) / (endFrameExclusive - startFrame));
}

// Natural interpolating cubic: each waypoint is on the curve. Adjacent segments
// share value, velocity and acceleration. The supplied seconds are knot times.
export function createNaturalSpline(points, seconds) {
  if (!Array.isArray(points) || points.length < 2 || points.length > 256) throw new Error('A spline needs 2 to 256 points');
  const p = points.map((point, i) => vector(point, `points[${i}]`));
  if (!Array.isArray(seconds) || seconds.length !== p.length) throw new Error('seconds must match points');
  const times = seconds.map((time, i) => finite(time, `seconds[${i}]`));
  if (times.some((time, i) => i > 0 && time <= times[i - 1])) throw new Error('seconds must be strictly increasing');
  const n = p.length;
  const second = Array.from({length: n}, () => [0, 0, 0]);
  if (n > 2) {
    const upper = new Array(n - 2).fill(0);
    const rhs = Array.from({length: n - 2}, () => [0, 0, 0]);
    for (let i = 1; i < n - 1; i++) {
      const before = times[i] - times[i - 1];
      const after = times[i + 1] - times[i];
      const divisor = 2 * (before + after) - (i > 1 ? before * upper[i - 2] : 0);
      upper[i - 1] = after / divisor;
      for (let d = 0; d < 3; d++) {
        const slopeChange = 6 * ((p[i + 1][d] - p[i][d]) / after - (p[i][d] - p[i - 1][d]) / before);
        rhs[i - 1][d] = (slopeChange - (i > 1 ? before * rhs[i - 2][d] : 0)) / divisor;
      }
    }
    for (let i = n - 2; i > 0; i--) {
      for (let d = 0; d < 3; d++) second[i][d] = rhs[i - 1][d] - upper[i - 1] * second[i + 1][d];
    }
  }
  return {points: p, seconds: times, second};
}

export function sampleNaturalSpline(spline, seconds) {
  const t = Math.min(spline.seconds.at(-1), Math.max(spline.seconds[0], finite(seconds, 'seconds')));
  let left = 0;
  let right = spline.seconds.length - 1;
  while (right - left > 1) {
    const middle = Math.floor((left + right) / 2);
    if (spline.seconds[middle] <= t) left = middle;
    else right = middle;
  }
  const h = spline.seconds[right] - spline.seconds[left];
  const b = (t - spline.seconds[left]) / h;
  const a = 1 - b;
  const position = [0, 1, 2].map((d) =>
    a * spline.points[left][d] + b * spline.points[right][d] + h * h / 6 *
    ((a * a * a - a) * spline.second[left][d] + (b * b * b - b) * spline.second[right][d]));
  const velocity = [0, 1, 2].map((d) =>
    (spline.points[right][d] - spline.points[left][d]) / h + h / 6 *
    ((1 - 3 * a * a) * spline.second[left][d] + (3 * b * b - 1) * spline.second[right][d]));
  const acceleration = [0, 1, 2].map((d) => a * spline.second[left][d] + b * spline.second[right][d]);
  return {position, velocity, acceleration};
}

export function createCameraTrack(spec, durationSeconds) {
  if (!spec || typeof spec !== 'object') throw new Error('camera_path must be an object');
  if (!Array.isArray(spec.points) || spec.points.length < 2) throw new Error('camera_path.points needs at least two points');
  let times = spec.seconds;
  if (times === undefined) {
    if (!Number.isFinite(durationSeconds) || durationSeconds <= 0) throw new Error('Omitted camera seconds require a positive shot duration');
    times = spec.points.map((_, i) => i * durationSeconds / (spec.points.length - 1));
  }
  const position = createNaturalSpline(spec.points, times);
  const targets = spec.targets ?? [[0, 2.2, -1.3]];
  if (!Array.isArray(targets) || (targets.length !== 1 && targets.length !== spec.points.length)) throw new Error('targets needs one fixed target or one target per camera point');
  const target = targets.length === 1 ? vector(targets[0], 'target') : createNaturalSpline(targets, times);
  const easing = spec.easing ?? 'smootherstep';
  if (!['linear', 'smootherstep'].includes(easing)) throw new Error('Camera easing must be linear or smootherstep');
  if (spec.pacing !== undefined && spec.pacing !== 'waypoints') throw new Error('Only timed waypoint pacing is supported');
  const roll = spec.roll_degrees ?? [0, 0];
  if (!Array.isArray(roll) || roll.length !== 2) throw new Error('roll_degrees needs a start and an end value');
  const track = {position, target, easing, roll: roll.map((value) => finite(value, 'roll_degrees'))};
  // Catch unsuitable targets early without introducing a switching up vector.
  for (let i = 0; i <= 128; i++) sampleCameraTrack(track, mix(times[0], times.at(-1), i / 128));
  return track;
}

export function sampleCameraTrack(track, seconds) {
  const first = track.position.seconds[0];
  const last = track.position.seconds.at(-1);
  const progress = clamp01((finite(seconds, 'seconds') - first) / (last - first));
  const eased = track.easing === 'smootherstep' ? smootherstep(progress) : progress;
  const knotTime = mix(first, last, eased);
  const position = sampleNaturalSpline(track.position, knotTime).position;
  const target = Array.isArray(track.target) ? [...track.target] : sampleNaturalSpline(track.target, knotTime).position;
  const forward = normalize(target.map((component, i) => component - position[i]));
  if (Math.abs(forward[1]) > 0.999) throw new Error('Camera path approaches a vertical look direction; move its target to keep a stable horizon');
  const right = normalize(cross(forward, [0, 1, 0]));
  const up = normalize(cross(right, forward));
  const rollDegrees = mix(track.roll[0], track.roll[1], eased);
  const roll = rollDegrees * Math.PI / 180;
  return {
    position, target,
    up: up.map((component, i) => component * Math.cos(roll) - right[i] * Math.sin(roll)),
    roll_degrees: rollDegrees, progress,
  };
}

export function compileMusicEvents(events = [], fps = 60) {
  if (!Array.isArray(events)) throw new Error('timing.events must be an array');
  if (!Number.isFinite(fps) || fps <= 0) throw new Error('fps must be positive');
  return events.map((event, i) => {
    if (!event || !Number.isInteger(event.frame) || event.frame < 0 || typeof event.kind !== 'string' || !event.kind) throw new Error(`Invalid music event ${i}`);
    const amplitude = finite(event.amplitude ?? 1, 'event amplitude');
    const attack = finite(event.attack_frames ?? Math.max(1, Math.round(fps * 0.25)), 'attack_frames');
    const release = finite(event.release_frames ?? Math.max(1, Math.round(fps * 1.2)), 'release_frames');
    if (amplitude < 0 || attack <= 0 || release <= 0) throw new Error('Event amplitude must be nonnegative and envelope durations must be positive');
    return {...event, amplitude, attack_frames: attack, release_frames: release};
  });
}

// Authored hit is the envelope peak. The attack anticipates it; release settles.
// Multiple cues are bounded without clipping derivative continuity at a hard cap.
export function sampleMusicEnvelope(events, frame, {kinds, cap} = {}) {
  finite(frame, 'frame');
  if (cap !== undefined && (!Number.isFinite(cap) || cap <= 0)) throw new Error('Envelope cap must be positive');
  let sum = 0;
  for (const event of events) {
    if (kinds && !kinds.includes(event.kind)) continue;
    const delta = frame - event.frame;
    if (delta < -event.attack_frames || delta > event.release_frames) continue;
    const envelope = delta <= 0 ? smootherstep(1 + delta / event.attack_frames) : 1 - smootherstep(delta / event.release_frames);
    sum += event.amplitude * envelope;
  }
  if (cap === undefined || sum <= cap / 2) return sum;
  if (sum >= cap) return cap;
  const u = (sum - cap / 2) / (cap / 2);
  return cap / 2 + cap / 2 * (u + 4 * u ** 3 - 7 * u ** 4 + 3 * u ** 5);
}

function phaseFor(seed, channel) {
  let value = (seed >>> 0) ^ 0x9e3779b9;
  for (const char of String(channel)) value = Math.imul(value ^ char.charCodeAt(0), 0x85ebca6b) >>> 0;
  return value / 4294967296 * Math.PI * 2;
}

// Two slow, independently phased layers. Amplitude is in the caller's units.
export function secondaryMotion(seconds, seed, channel, amplitude = 1) {
  finite(seconds, 'seconds'); finite(seed, 'seed'); finite(amplitude, 'amplitude');
  const phase = phaseFor(seed, channel);
  return amplitude * (0.7 * Math.sin(seconds * 0.52 + phase) + 0.3 * Math.sin(seconds * 0.89 + phase * 1.7));
}

// Arrival uses a complete eased interval, so title speed and acceleration never
// jump at the hold. This does not invent spring state or overshoot small text.
export function titleSettle(seconds, {delay = 0, duration = 1.2, distance = 18} = {}) {
  finite(seconds, 'seconds'); finite(delay, 'delay'); finite(distance, 'distance');
  if (!Number.isFinite(duration) || duration <= 0) throw new Error('Settle duration must be positive');
  const progress = smootherstep((seconds - delay) / duration);
  return {progress, offset: distance * (1 - progress), opacity: 0.25 + 0.75 * progress};
}
