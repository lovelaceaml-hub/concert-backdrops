import {Composition} from 'remotion';
import {FinishingComposition} from './Composition';
import {DEMO} from './timeline';

export const Root=()=> <Composition id="ConcertFilm" component={FinishingComposition} width={DEMO.width} height={DEMO.height} fps={DEMO.fps} durationInFrames={DEMO.durationInFrames} defaultProps={DEMO} calculateMetadata={({props})=>({width:props.width,height:props.height,fps:props.fps,durationInFrames:props.durationInFrames})}/>;
