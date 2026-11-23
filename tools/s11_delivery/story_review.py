"""Extract compact encoded-film sheets around every edit and across the story.

This prepares evidence for human/model visual inspection; it does not turn
image extraction into an automatic creative-quality or modesty verdict.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]


def samples():
    tree = ast.parse((ROOT / "tools/s11_full2/s11_full2.py").read_text())
    edit = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EDIT"
                                                for t in node.targets):
            edit = ast.literal_eval(node.value)
            break
    if not edit or len(edit) != 70:
        raise ValueError("Review the source edit before generating new delivery sheets.")
    starts = [74.70 if abs(row[0] - 74.56) < 1e-7 else row[0] for row in edit]
    selected = {}
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else 260.0
        frame = round((start + .1) * 60)
        for delta, role in ((-1, "before cut"), (1, "after cut")):
            if 0 <= frame + delta < 16500:
                selected[frame + delta] = f"{index:02d} {role}"
        mid = round(((start + end) / 2 + .1) * 60)
        selected[mid] = f"{index:02d} shot middle"
    for second in (0, 12, 28, 45, 58, 70, 86, 99, 105.7, 118.8, 121.433333,
                   123.2, 140, 155, 167, 186, 205, 221, 240, 250, 254.2,
                   259.9, 260.0, 267.0, 274.983333):
        selected[round(second * 60)] = "selected composition"
    return [dict(frame=f, video_seconds=f / 60, source_seconds=max(0, f / 60 - .1),
                 purpose=selected[f]) for f in sorted(selected)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = samples()
    args.out.mkdir(parents=True, exist_ok=True)
    frames = args.out / "frames"
    if frames.exists():
        raise ValueError("Existing review frames are preserved; select a new directory.")
    frames.mkdir()
    selection = "+".join(f"eq(n\\,{row['frame']})" for row in rows)
    subprocess.run(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(args.video),
                    "-vf", "select=" + selection + ",scale=400:225:flags=lanczos",
                    "-fps_mode", "vfr", "-an", str(frames / "frame-%04d.png")], check=True)
    files = sorted(frames.glob("frame-*.png"))
    if len(files) != len(rows):
        raise ValueError("Extracted review inventory differs from the requested frame inventory.")
    per_sheet, columns, cell_width, cell_height = 24, 4, 400, 251
    for first in range(0, len(rows), per_sheet):
        group = rows[first:first + per_sheet]
        sheet = Image.new("RGB", (columns * cell_width,
                                  ((len(group) + columns - 1) // columns) * cell_height), (12, 15, 23))
        draw = ImageDraw.Draw(sheet)
        for offset, row in enumerate(group):
            x, y = offset % columns * cell_width, offset // columns * cell_height
            with Image.open(files[first + offset]) as frame:
                sheet.paste(frame.convert("RGB"), (x, y))
            draw.text((x + 5, y + 229), f"{row['video_seconds']:7.3f}s | {row['purpose']}", fill="white")
            row["extracted_file"] = str(files[first + offset].relative_to(args.out))
        sheet.save(args.out / f"story-sheet-{first // per_sheet + 1:02d}.jpg", quality=94)
    record = dict(schema="s11-story-review-extraction-v1", video=args.video.name,
                  frames=len(rows), full_film_seconds=275, rows=rows,
                  visual_verdict="Pending actual inspection of the extracted sheets.")
    (args.out / "inventory.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"frames": len(rows), "sheets": (len(rows) + per_sheet - 1) // per_sheet,
                      "out": str(args.out)}))


if __name__ == "__main__":
    main()
