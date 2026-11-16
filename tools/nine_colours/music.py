"""Preserve Film 10 music, adding only the requested two-second quiet lead-in."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]

def main():
    out=ROOT/'work/nine_colours/score.wav'
    out.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'audio/promo/concert-medley.mp3'),
        '-af','adelay=2000:all=1,apad,atrim=duration=62','-ar','48000','-ac','2',
        '-c:a','pcm_s24le',str(out)],check=True)
    print(out)

if __name__=='__main__':
    main()
