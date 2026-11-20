import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {deliveryFfmpegArgs, REC709_FILTER} from './delivery.mjs';

test('video mux keeps an encoded YUV stream unchanged', () => {
  const args = ['-i', 'encoded.mp4', '-c:v', 'copy', '-an', 'output.mp4'];
  assert.deepEqual(deliveryFfmpegArgs({type: 'stitcher', args}), args);
});

test('unexpected encoder or filter layout fails before silent mis-conversion', () => {
  assert.throws(() => deliveryFfmpegArgs({args: ['-c:v', 'h264_videotoolbox', 'output.mp4']}), /software libx264/);
  assert.throws(() => deliveryFfmpegArgs({args: ['-c:v', 'libx264', 'output.mp4']}), /Unexpected Remotion filter/);
});

const ffmpegReady = spawnSync('ffmpeg', ['-version'], {encoding: 'utf8'}).status === 0 && spawnSync('ffprobe', ['-version'], {encoding: 'utf8'}).status === 0;

test('browser delivery converts actual RGB pixels and produces Rec.709 High profile metadata', {skip: !ffmpegReady}, async () => {
  const directory = await mkdtemp(path.join(tmpdir(), 'browser-color-check-'));
  try {
    // A neutral RGB128 source has a known sRGB transfer value. PPM is a
    // convenient exact test input; production uses the browser's lossless PNGs.
    const ppm = Buffer.concat([Buffer.from('P6\n32 32\n255\n'), Buffer.alloc(32 * 32 * 3, 128)]);
    const output = path.join(directory, 'sample.mp4');
    const args = deliveryFfmpegArgs({type: 'pre-stitcher', args: [
      '-v', 'error', '-threads', '1', '-filter_threads', '1', '-r', '5', '-f', 'image2pipe', '-vcodec', 'ppm', '-i', '-',
      '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', '-vf', 'zscale=matrix=709:matrixin=709:range=limited',
      '-colorspace:v', 'bt709', '-color_primaries:v', 'bt709', '-color_trc:v', 'bt709', '-color_range', 'tv', '-an', '-y', output,
    ]});
    assert.ok(args.includes(REC709_FILTER));
    const encoded = spawnSync('ffmpeg', args, {input: Buffer.concat([ppm, ppm]), maxBuffer: 2 ** 20});
    assert.equal(encoded.status, 0, encoded.stderr?.toString());
    const probe = spawnSync('ffprobe', ['-v', 'error', '-show_streams', '-count_frames', '-of', 'json', output], {encoding: 'utf8'});
    assert.equal(probe.status, 0, probe.stderr);
    const streams = JSON.parse(probe.stdout).streams;
    assert.equal(streams.length, 1);
    const video = streams[0];
    for (const [key, value] of Object.entries({codec_name: 'h264', profile: 'High', pix_fmt: 'yuv420p', color_space: 'bt709', color_transfer: 'bt709', color_primaries: 'bt709', color_range: 'tv', width: 32, height: 32, nb_read_frames: '2', avg_frame_rate: '5/1'})) assert.equal(video[key], value, key);
    const decoded = spawnSync('ffmpeg', ['-v', 'error', '-i', output, '-frames:v', '1', '-pix_fmt', 'yuv420p', '-f', 'rawvideo', '-'], {maxBuffer: 2 ** 20});
    assert.equal(decoded.status, 0, decoded.stderr?.toString());
    const luma = decoded.stdout.subarray(0, 32 * 32).reduce((sum, value) => sum + value, 0) / (32 * 32);
    // Display-referred sRGB maps to BT.1886 display gamma 2.4, as used by
    // zimg's default Rec.709 transform. A camera OETF is a different intent.
    const linear = ((128 / 255 + 0.055) / 1.055) ** 2.4;
    const expectedLuma = 16 + 219 * linear ** (1 / 2.4);
    // Merely retagging or matrix-converting without transfer gives about Y126.
    assert.ok(Math.abs(luma - expectedLuma) < 2, `Unexpected luma ${luma}; check transfer conversion`);
  } finally {
    await rm(directory, {recursive: true, force: true});
  }
});
