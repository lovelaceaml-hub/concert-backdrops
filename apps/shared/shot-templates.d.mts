import type {CameraPathSpec, CompiledMusicEvent} from './motion.mjs';
export type CameraPresetName = 'orbit' | 'push-in' | 'fly-through' | 'locked';
export type ShotTemplateName = 'reveal' | 'procession' | 'resolve';
export const CAMERA_PRESET_NAMES: readonly CameraPresetName[];
export const SHOT_TEMPLATES: Readonly<Record<ShotTemplateName, {name: string; camera: CameraPresetName; motion_amount: number; music_amount: number}>>;
export function cameraPreset(name: CameraPresetName, durationSeconds: number): CameraPathSpec;
export function createShotTemplate(name: ShotTemplateName, options: {id?: string; start_frame?: number; duration_frames: number; fps?: number}): {id: string; name: string; renderer: string; start_frame: number; end_frame_exclusive: number; scene: string; params: {camera: CameraPresetName; camera_path: CameraPathSpec; bloom: boolean; motion_amount: number; music_amount: number}};
export function createPhraseEvents(options: {start_frame: number; peak_frame: number; end_frame_exclusive: number; fps?: number; amplitude?: number}): CompiledMusicEvent[];
