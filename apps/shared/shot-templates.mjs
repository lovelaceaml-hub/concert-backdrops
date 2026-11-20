import {compileMusicEvents} from './motion.mjs';

// Original pavilion study only. Coordinates are Three.js metres, Y up.
const CAMERAS = {
  orbit: {points: [[1.8, 5.1, 14.9], [3.6, 5.15, 14.4], [5.3, 5.1, 13.7], [6.8, 5, 12.8]]},
  'push-in': {points: [[1.9, 5.2, 16], [1.85, 5.05, 14.9], [1.7, 4.85, 13.8], [1.55, 4.65, 12.7]]},
  'fly-through': {points: [[7.8, 4.9, 15], [7.4, 4.6, 11], [7, 4.15, 7], [6.6, 3.8, 3]]},
  locked: {points: [[1.8, 5.1, 14.9], [1.8, 5.1, 14.9]]},
};

export const CAMERA_PRESET_NAMES = Object.freeze(Object.keys(CAMERAS));

export function cameraPreset(name, durationSeconds) {
  const preset = CAMERAS[name];
  if (!preset) throw new Error(`Unknown camera preset: ${name}`);
  if (!Number.isFinite(durationSeconds) || durationSeconds <= 0) throw new Error('Camera preset duration must be positive');
  return {
    points: preset.points.map((point) => [...point]),
    targets: [[0, 2.2, -1.3]],
    seconds: preset.points.map((_, i) => i * durationSeconds / (preset.points.length - 1)),
    easing: 'smootherstep',
    roll_degrees: [0, 0],
  };
}

export const SHOT_TEMPLATES = Object.freeze({
  reveal: {name: 'Gentle architectural reveal', camera: 'push-in', motion_amount: 0.8, music_amount: 0.12},
  procession: {name: 'Flow past the pavilion', camera: 'fly-through', motion_amount: 1, music_amount: 0.18},
  resolve: {name: 'Quiet musical resolution', camera: 'orbit', motion_amount: 0.65, music_amount: 0.08},
});

export function createShotTemplate(name, {id = name, start_frame = 0, duration_frames, fps = 60} = {}) {
  const template = SHOT_TEMPLATES[name];
  if (!template) throw new Error(`Unknown shot template: ${name}`);
  if (!Number.isInteger(start_frame) || start_frame < 0 || !Number.isInteger(duration_frames) || duration_frames < 2 || !Number.isFinite(fps) || fps <= 0) throw new Error('Shot template needs valid frame bounds and fps');
  return {
    id, name: template.name, renderer: 'threejs', start_frame,
    end_frame_exclusive: start_frame + duration_frames,
    scene: 'apps/scene-preview/src/scenes/Heavenly.tsx',
    params: {
      camera: template.camera,
      camera_path: cameraPreset(template.camera, duration_frames / fps),
      bloom: true, motion_amount: template.motion_amount, music_amount: template.music_amount,
    },
  };
}

// All three anchors are supplied by the editor. This never guesses a music beat.
export function createPhraseEvents({start_frame, peak_frame, end_frame_exclusive, fps = 60, amplitude = 1}) {
  if (![start_frame, peak_frame, end_frame_exclusive].every(Number.isInteger) || start_frame < 0 || !(start_frame < peak_frame && peak_frame < end_frame_exclusive)) throw new Error('Phrase start, peak and end must be ordered timeline frames');
  return compileMusicEvents([{
    frame: peak_frame, kind: 'phrase', amplitude,
    attack_frames: peak_frame - start_frame,
    release_frames: end_frame_exclusive - peak_frame,
  }], fps);
}
