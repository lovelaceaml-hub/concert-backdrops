export type RenderJob = {
  project_id: string;
  shot: {id: string; name: string; renderer: string; start_frame: number; end_frame_exclusive: number; scene: string; params?: Record<string, unknown>};
  video: {width: number; height: number; fps: number};
  seed: number;
  frames: number[];
  out_dir: string;
  samples?: number;
  style?: Record<string, unknown>;
  timing?: Record<string, unknown>;
};
export type RendererInfo = {vendor: string; renderer: string; webglVersion: string; software: boolean; frame: number; seed: number; fps: number};
declare global {
  interface Window {
    __RENDER_JOB__?: RenderJob;
    __SCENE_READY__?: boolean;
    renderFrame?: (frame: number) => Promise<RendererInfo>;
  }
}
