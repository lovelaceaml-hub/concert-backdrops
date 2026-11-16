"""Technical inspection of the independent The Light That Reaches You exports."""
import json
from pathlib import Path
import subprocess
import sys
import numpy as np


def run(args):
    return subprocess.check_output(args)


def inspect(path):
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams',
                           '-show_format', '-of', 'json', str(path)]))
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    sound = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    pts = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_frames', '-show_entries',
                          'frame=best_effort_timestamp_time', '-of', 'json', str(path)]))
    times = np.array([float(f['best_effort_timestamp_time']) for f in pts['frames']])
    raw = run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(path),
               '-vf', 'scale=160:90', '-pix_fmt', 'gray', '-an',
               '-f', 'rawvideo', '-threads', '1', '-'])
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160)
    delta = np.abs(np.diff(frames.astype(np.int16), axis=0)).mean(axis=(1, 2))
    duplicates = np.flatnonzero(delta == 0)
    hash_text = run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(path),
                     '-map', '0:v:0', '-an', '-f', 'framemd5', '-']).decode()
    hashes = [line.rsplit(',', 1)[-1].strip() for line in hash_text.splitlines()
              if line and not line.startswith('#')]
    exact_duplicate_pairs = sum(a == b for a, b in zip(hashes, hashes[1:]))
    exact_longest = exact_current = 0
    for a, b in zip(hashes, hashes[1:]):
        exact_current = exact_current + 1 if a == b else 0
        exact_longest = max(exact_longest, exact_current)
    longest = current = 0
    for d in delta:
        current = current + 1 if d == 0 else 0
        longest = max(longest, current)
    audio = np.frombuffer(run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(path),
                               '-vn', '-ar', '48000', '-ac', '2',
                               '-f', 'f32le', '-']), np.float32).reshape(-1, 2)
    def db(v):
        return round(float(20 * np.log10(max(float(v), 1e-12))), 3)
    tail = audio[-12000:]
    hop=12000
    rms=np.sqrt(np.mean(audio[:len(audio)//hop*hop].reshape(-1,hop,2)**2,axis=(1,2)))
    envelope=20*np.log10(np.maximum(rms,1e-12))
    audio_joins=[]
    for t in [2+4*(240/112)*i for i in range(1,7)]:
        a,b=int((t-1.1)*4),int((t+1.1)*4)
        audio_joins.append(dict(time=t,largest_quarter_second_jump_db=float(np.max(abs(np.diff(envelope[a:b]))))))
    # Difference and second-difference statistics identify intervals for visual
    # review; they cannot establish whether a gesture looks natural.
    signed=np.diff(frames.astype(np.int16),axis=0)
    jitter=np.abs(np.diff(signed,axis=0)).mean(axis=(1,2))
    motion=[]
    for first in range(0,len(delta),30):
        motion.append(dict(time=first/60,mean_delta=float(delta[first:first+30].mean()),
                           mean_jitter=float(jitter[first:min(first+30,len(jitter))].mean())))
    busiest=sorted(motion,key=lambda row:row['mean_jitter'],reverse=True)[:12]
    joins = []
    for frame in range(465, 3720, 465):
        if frame >= len(frames):
            continue
        local = np.r_[delta[frame-11:frame-1], delta[frame:frame+10]]
        median = float(np.median(local))
        joins.append(dict(frame=frame, seconds=frame/60,
                          mean_absolute_delta=float(delta[frame-1]),
                          surrounding_median_delta=median,
                          ratio_to_surroundings=float(delta[frame-1]/max(median, 1e-9))))
    result = dict(file=str(path), size_bytes=path.stat().st_size,
                  resolution=[video['width'], video['height']],
                  avg_frame_rate=video['avg_frame_rate'], frames=len(times),
                  video_duration=video.get('duration'), audio_duration=sound.get('duration'),
                  audio_channels=sound.get('channels'), audio_sample_rate=sound.get('sample_rate'),
                  first_pts=float(times[0]), last_pts=float(times[-1]),
                  largest_pts_step_error_seconds=float(np.max(np.abs(np.diff(times)-1/60))),
                  exact_duplicate_pairs=exact_duplicate_pairs,
                  longest_exact_duplicate_run_frames=exact_longest,
                  low_resolution_exact_duplicate_pairs=int(len(duplicates)),
                  longest_low_resolution_duplicate_run_frames=int(longest),
                  mean_delta_55_to_62=float(delta[3300:].mean()),
                  minimum_delta_55_to_62=float(delta[3300:].min()),
                  audio_peak_dbfs=db(np.abs(audio).max()),
                  audio_first_1_9_seconds_peak_dbfs=db(np.abs(audio[:91200]).max()),
                  audio_final_quarter_second_rms_dbfs=db(np.sqrt(np.mean(tail**2))),
                  audio_final_second_rms_dbfs=db(np.sqrt(np.mean(audio[-48000:]**2))),
                  audio_joins=audio_joins,
                  half_second_motion=motion,
                  busiest_motion_intervals=busiest,
                  render_part_join_deltas=joins,
                  minimum_mean_luminance=float(frames.mean(axis=(1, 2)).min()),
                  maximum_mean_luminance=float(frames.mean(axis=(1, 2)).max()))
    result['checks_pass'] = (len(times) == 3720 and video['avg_frame_rate'] == '60/1'
                            and result['largest_pts_step_error_seconds'] < .000002
                            and abs(float(video['duration']) - 62) < .01
                            and abs(float(sound['duration']) - 62) < .05
                            and len(audio) >= 62*48000
                            and exact_longest < 90 and result['audio_peak_dbfs'] < 0
                            and result['audio_final_second_rms_dbfs'] < -45
                            and result['audio_first_1_9_seconds_peak_dbfs'] < -90
                            and all(j['largest_quarter_second_jump_db'] <= 3 for j in audio_joins))
    return result


if __name__ == '__main__':
    results = [inspect(Path(p)) for p in sys.argv[1:]]
    print(json.dumps(results, indent=2))
    sys.exit(0 if all(r['checks_pass'] for r in results) else 1)
