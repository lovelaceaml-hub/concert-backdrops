"""Contact sheet of song 10's version 2 stage video at its landmarks, labelled with stage video times (JPEG, under
3 MB). The frames come from the finished stage file, so the sheet shows exactly what was delivered.

    python tools/s10_full2/contact_sheet.py "out/s10_full2/10 Our Mother Saves the World - Backdrop v2 - stage 1080p60.mp4" out.jpg

No em dash or en dash anywhere in this file.
"""
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

LANDMARKS = [
    (0.0, "frame 0: opening lockup"), (8.0, "end of opening"), (12.0, "signature, the night"),
    (36.5, "the lamp lifted"), (45.0, "Heavenly Mother, the lamp"), (53.5, "rescue thread"),
    (62.0, "Greeting"), (78.5, "Consideration"), (96.0, "Inclusiveness"), (108.6, "Greeting relit, wide"),
    (122.6, "Encouragement"), (141.0, "peace: gold web"), (175.0, "the water road"),
    (197.5, "Gratitude"), (205.0, "final chord, all nine"), (225.9, "the hold, last frame"),
]
W, H, COLS = 480, 270, 4


def grab(video, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1',
                          '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         check=True, capture_output=True).stdout
    return Image.frombytes('RGB', (W, H), raw)


def main():
    video, out = sys.argv[1], sys.argv[2]
    rows = (len(LANDMARKS) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * W, rows * (H + 26)), (12, 14, 30))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('fonts/jost-latin-500-normal.ttf', 17)
    except OSError:
        font = ImageFont.load_default()
    for i, (t, label) in enumerate(LANDMARKS):
        x, y = (i % COLS) * W, (i // COLS) * (H + 26)
        sheet.paste(grab(video, t), (x, y))
        m, s = divmod(t, 60)
        d.text((x + 8, y + H + 3), f'{int(m)}:{s:05.2f}  {label}', fill=(246, 211, 139), font=font)
    sheet.save(out, quality=85)


if __name__ == '__main__':
    main()
