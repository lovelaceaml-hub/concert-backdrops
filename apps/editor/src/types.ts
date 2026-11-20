export type Clip={src:string;start_frame:number;end_frame_exclusive:number};
export type Caption={text:string;start_frame:number;end_frame_exclusive:number};
export type FinishProps={title:string;width:number;height:number;fps:number;durationInFrames:number;clips:Clip[];audio_src?:string;captions?:Caption[];show_title?:boolean};
