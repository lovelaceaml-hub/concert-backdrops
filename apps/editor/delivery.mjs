// Browser PNGs are full-range sRGB. Convert their transfer function and matrix
// before encoding display-referred SDR Rec.709 with BT.1886 gamma 2.4;
// metadata tags alone do not perform conversion.
export const REC709_FILTER = 'format=gbrp16le,zscale=matrixin=gbr:transferin=iec61966-2-1:primariesin=bt709:rangein=full:matrix=bt709:transfer=bt709:primaries=bt709:range=limited:dither=error_diffusion,format=yuv420p';

export function deliveryFfmpegArgs({args}) {
  const result = [...args];
  const codecIndex = result.indexOf('-c:v');
  if (codecIndex < 0) throw new Error('Expected an explicit Remotion video codec');
  // The final mux may stream-copy the video encoded by the pre-stitcher.
  // Reapplying the RGB conversion to that YUV stream would be incorrect.
  if (result[codecIndex + 1] === 'copy') return result;
  if (result[codecIndex + 1] !== 'libx264') throw new Error('The browser finisher requires software libx264');
  const filterIndex = result.indexOf('-vf');
  if (filterIndex < 0 || result.indexOf('-vf', filterIndex + 1) >= 0 || result.includes('-filter_complex')) throw new Error('Unexpected Remotion filter graph; review delivery color conversion before rendering');
  result[filterIndex + 1] = REC709_FILTER;
  const profileIndex = result.indexOf('-profile:v');
  if (profileIndex >= 0) result[profileIndex + 1] = 'high';
  else result.splice(result.length - 1, 0, '-profile:v', 'high');
  return result;
}
