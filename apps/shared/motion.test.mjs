import test from 'node:test';
import assert from 'node:assert/strict';
import {
  compileMusicEvents, createCameraTrack, createNaturalSpline, frameSeconds,
  sampleCameraTrack, sampleMusicEnvelope, sampleNaturalSpline,
  secondaryMotion, smootherstep, titleSettle,
} from './motion.mjs';
import {CAMERA_PRESET_NAMES, cameraPreset, createPhraseEvents, createShotTemplate} from './shot-templates.mjs';

const close = (actual, expected, tolerance = 1e-8) => assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} differs from ${expected}`);
const vecClose = (actual, expected, tolerance) => actual.forEach((value, i) => close(value, expected[i], tolerance));
const points = [[0, 3, 12], [2, 3.5, 10], [4, 4, 8], [7, 3, 5]];
const seconds = [0, 1, 3, 6];
const cameraSpec = {points, seconds, targets: [[0, 1, -2]], easing: 'smootherstep'};

test('natural spline interpolates every irregularly timed waypoint', () => {
  const spline = createNaturalSpline(points, seconds);
  seconds.forEach((time, i) => vecClose(sampleNaturalSpline(spline, time).position, points[i]));
  vecClose(sampleNaturalSpline(spline, -5).position, points[0]);
  vecClose(sampleNaturalSpline(spline, 20).position, points.at(-1));
});

test('natural spline has continuous velocity and acceleration at internal joins', () => {
  const spline = createNaturalSpline(points, seconds);
  for (const time of seconds.slice(1, -1)) {
    const before = sampleNaturalSpline(spline, time - 1e-7);
    const after = sampleNaturalSpline(spline, time + 1e-7);
    vecClose(before.position, after.position, 1e-6);
    vecClose(before.velocity, after.velocity, 1e-6);
    vecClose(before.acceleration, after.acceleration, 1e-6);
  }
});

test('natural boundary condition and straight paths have expected derivatives', () => {
  const spline = createNaturalSpline([[1, 2, 3], [3, 6, 9]], [2, 4]);
  vecClose(sampleNaturalSpline(spline, 3).position, [2, 4, 6]);
  vecClose(sampleNaturalSpline(spline, 3).velocity, [1, 2, 3]);
  vecClose(sampleNaturalSpline(spline, 3).acceleration, [0, 0, 0]);
  const curved = createNaturalSpline(points, seconds);
  vecClose(sampleNaturalSpline(curved, 0).acceleration, [0, 0, 0]);
  vecClose(sampleNaturalSpline(curved, 6).acceleration, [0, 0, 0]);
});

test('whole-shot easing approaches a still pose with zero speed and acceleration', () => {
  const track = createCameraTrack(cameraSpec);
  const h = 1e-4;
  for (const time of [0, 6]) {
    const a = sampleCameraTrack(track, time - h).position;
    const b = sampleCameraTrack(track, time).position;
    const c = sampleCameraTrack(track, time + h).position;
    for (let i = 0; i < 3; i++) {
      close((c[i] - a[i]) / (2 * h), 0, 1e-6);
      close((c[i] - 2 * b[i] + a[i]) / (h * h), 0, 0.001);
    }
  }
});

test('camera poses are identical when requested out of order', () => {
  const track = createCameraTrack(cameraSpec);
  const original = sampleCameraTrack(track, 2.25);
  for (const time of [6, 0, 4.7, 1, 5.5]) sampleCameraTrack(track, time);
  assert.deepEqual(sampleCameraTrack(track, 2.25), original);
});

test('camera fixture matches the Python path implementation', () => {
  const track = createCameraTrack(cameraSpec);
  vecClose(sampleCameraTrack(track, 1.5).position, [1.3103128948381968, 3.319630260978426, 10.689687105161804]);
  vecClose(sampleCameraTrack(track, 3).position, [4, 4, 8]);
  vecClose(sampleCameraTrack(track, 4.5).position, [6.315212771296501, 3.3025714680552483, 5.684787228703499]);
});

test('camera roll produces a unit up vector perpendicular to look direction', () => {
  const track = createCameraTrack({...cameraSpec, roll_degrees: [-3, 3]});
  for (let i = 0; i <= 60; i++) {
    const pose = sampleCameraTrack(track, i / 10);
    const forward = pose.target.map((value, d) => value - pose.position[d]);
    close(Math.hypot(...pose.up), 1);
    close(forward.reduce((sum, value, d) => sum + value * pose.up[d], 0), 0);
  }
});

test('signed camera roll matches Blender local-Z rotation after coordinate conversion', () => {
  for (const degrees of [-10, 10]) {
    const track = createCameraTrack({points: [[0, 0, 10], [0, 0, 10]], targets: [[0, 0, 0]], seconds: [0, 1], roll_degrees: [degrees, degrees]});
    const {up} = sampleCameraTrack(track, 0.5);
    // A proper Y-up to Z-up rotation maps (x, y, z) to (x, -z, y).
    const blenderUp = [up[0], -up[2], up[1]];
    const angle = degrees * Math.PI / 180;
    vecClose(blenderUp, [-Math.sin(angle), 0, Math.cos(angle)]);
  }
});

test('30 fps and 60 fps evaluate the same pose at the same elapsed seconds', () => {
  const track = createCameraTrack(cameraSpec);
  assert.deepEqual(sampleCameraTrack(track, frameSeconds(90, 30, 30)), sampleCameraTrack(track, frameSeconds(180, 60, 60)));
});

test('all named camera presets stay finite and keep a stable horizon', () => {
  for (const name of CAMERA_PRESET_NAMES) {
    const track = createCameraTrack(cameraPreset(name, 8));
    for (let frame = 0; frame <= 480; frame += 5) {
      const pose = sampleCameraTrack(track, frame / 60);
      assert.ok([...pose.position, ...pose.target, ...pose.up].every(Number.isFinite));
    }
    if (name === 'locked') assert.deepEqual(sampleCameraTrack(track, 0).position, sampleCameraTrack(track, 8).position);
  }
});

test('invalid path timing, nonfinite values and unstable look directions fail early', () => {
  assert.throws(() => createNaturalSpline(points, [0, 1, 1, 3]), /strictly increasing/);
  assert.throws(() => createNaturalSpline([[0, 0, 0], [Infinity, 1, 2]], [0, 1]), /finite/);
  assert.throws(() => createCameraTrack({points}), /positive shot duration/);
  assert.throws(() => createCameraTrack({...cameraSpec, targets: [[0, 1, 2], [3, 4, 5]]}), /one target per/);
  assert.throws(() => createCameraTrack({points: [[0, 1, 0], [0, 2, 0]], targets: [[0, 0, 0]]}, 2), /vertical/);
  assert.throws(() => createCameraTrack({...cameraSpec, pacing: 'arc-length'}), /timed waypoint/);
});

test('authored event peaks exactly on its global hit frame with a smooth attack and release', () => {
  const events = compileMusicEvents([{frame: 120, kind: 'accent', amplitude: 0.8, attack_frames: 30, release_frames: 60}], 60);
  close(sampleMusicEnvelope(events, 89), 0);
  close(sampleMusicEnvelope(events, 90), 0);
  close(sampleMusicEnvelope(events, 120), 0.8);
  close(sampleMusicEnvelope(events, 180), 0);
  close(sampleMusicEnvelope(events, 181), 0);
  close(sampleMusicEnvelope(events, 105), 0.4);
  close(sampleMusicEnvelope(events, 150), 0.4);
  close(sampleMusicEnvelope(events, 120, {kinds: ['phrase']}), 0);
});

test('event envelope joins have no velocity or acceleration jumps', () => {
  const events = compileMusicEvents([{frame: 120, kind: 'accent', attack_frames: 30, release_frames: 60}]);
  const h = 0.001;
  for (const frame of [90, 120, 180]) {
    const a = sampleMusicEnvelope(events, frame - h);
    const b = sampleMusicEnvelope(events, frame);
    const c = sampleMusicEnvelope(events, frame + h);
    close((c - a) / (2 * h), 0, 1e-6);
    close((c - 2 * b + a) / (h * h), 0, 1e-5);
  }
});

test('overlapping music envelopes stay bounded with a smooth saturation knee', () => {
  const events = compileMusicEvents([{frame: 120, kind: 'accent'}, {frame: 125, kind: 'phrase'}]);
  for (let frame = 0; frame < 300; frame += 0.25) {
    const value = sampleMusicEnvelope(events, frame, {cap: 1});
    assert.ok(value >= 0 && value <= 1);
  }
  const uncapped = sampleMusicEnvelope(events, 122);
  assert.ok(uncapped > 1);
  close(sampleMusicEnvelope(events, 122, {cap: 1}), 1);
});

test('music defaults scale with fps and invalid events cannot silently animate', () => {
  const a = compileMusicEvents([{frame: 120, kind: 'accent'}], 60)[0];
  const b = compileMusicEvents([{frame: 60, kind: 'accent'}], 30)[0];
  close(a.attack_frames, 15); close(a.release_frames, 72);
  close(b.attack_frames, 8); close(b.release_frames, 36);
  assert.throws(() => compileMusicEvents([{frame: 5, kind: 'accent', attack_frames: 0}]), /positive/);
  assert.throws(() => compileMusicEvents([{frame: NaN, kind: 'accent'}]), /Invalid music event/);
});

test('secondary motion has a fixed amplitude bound and stable seed separation', () => {
  for (let time = -2; time < 30; time += 0.17) assert.ok(Math.abs(secondaryMotion(time, 2026, 'left-hand', 0.2)) <= 0.2);
  const original = secondaryMotion(4.6, 2026, 'left-hand', 0.2);
  secondaryMotion(9, 2026, 'left-hand', 0.2);
  close(secondaryMotion(4.6, 2026, 'left-hand', 0.2), original);
  assert.notEqual(secondaryMotion(4.6, 2026, 'right-hand', 0.2), original);
  assert.notEqual(secondaryMotion(4.6, 2027, 'left-hand', 0.2), original);
});

test('title settle is bounded and holds its final pose without overshoot', () => {
  close(smootherstep(-1), 0); close(smootherstep(2), 1);
  assert.deepEqual(titleSettle(0), {progress: 0, offset: 18, opacity: 0.25});
  assert.deepEqual(titleSettle(1.2), {progress: 1, offset: 0, opacity: 1});
  assert.deepEqual(titleSettle(10), titleSettle(1.2));
  for (let time = 0; time <= 2; time += 0.01) {
    const pose = titleSettle(time);
    assert.ok(pose.offset >= 0 && pose.offset <= 18 && pose.opacity >= 0.25 && pose.opacity <= 1);
  }
});

test('shot and phrase templates keep explicit global frame anchors', () => {
  const shot = createShotTemplate('procession', {id: 'entrance', start_frame: 120, duration_frames: 480, fps: 60});
  assert.equal(shot.start_frame, 120); assert.equal(shot.end_frame_exclusive, 600);
  assert.deepEqual(shot.params.camera_path.seconds, [0, 8 / 3, 16 / 3, 8]);
  const events = createPhraseEvents({start_frame: 180, peak_frame: 300, end_frame_exclusive: 540, fps: 60});
  close(sampleMusicEnvelope(events, 180), 0);
  close(sampleMusicEnvelope(events, 300), 1);
  close(sampleMusicEnvelope(events, 540), 0);
  assert.throws(() => createPhraseEvents({start_frame: 180, peak_frame: 100, end_frame_exclusive: 540}), /ordered/);
});
