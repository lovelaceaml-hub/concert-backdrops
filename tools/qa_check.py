"""Automatic quality check for one song's render (draft, video, share copy or stills).

It reads the song file (timings, text, figures) and uses the engine's own text layout, so it knows where every
word sits and when it is fully formed. Then it measures the frames:

  dark behind text   luminance in rings round every text block against the sky further out (veil, halo, band)
  legibility         contrast of the letters against the light just round them
  reading time       each expression fully formed for at least 6 s (from the song file timings)
  end card           three lines, held for at least 4 s
  calm bottom third  motion energy in the bottom third against the rest (frame differences)
  static figures     change inside each figure's box between frames: a figure that moves as a rigid image is flagged
  dashes             no em or en dash in the song file or its status file
  length             the video is as long as the song file says

Writes qa-report.md and qa.json to --out. With --fail-on high it exits 1 when a HIGH issue is found.

Usage (from the repository root):
  python tools/qa_check.py --song s08_favor_from_god --video out/draft.mp4 --out qa/
  python tools/qa_check.py --song s08_favor_from_god --stills out/name-stills --out out/name-stills
  python tools/qa_check.py --song s08_favor_from_god --static-only --out qa/
Needs numpy, scipy, pillow, the engine fonts (tools/setup_fonts.py) and ffmpeg for a video.
"""
import argparse
import glob
import json
import math
import os
import re
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "engine")

# ---------------------------------------------------------------- thresholds (tuned on v4 runs of songs 04 and 07)
EXPR_SOLID_MIN = 6.0        # s fully formed, PHASE2.md item 4
FRAG_SOLID_MIN = 3.0
GAP_MIN = 0.5               # clean gap after a dissolve ends before the next text starts
END_HOLD_MIN = 4.0
FORM_EXTRA = 0.75           # the right edge of the words is fully formed FORM_DUR + 0.75 s after form
DISSOLVE = 1.6
DARK_HIGH, DARK_MED = 0.62, 0.78          # ring luminance / sky luminance further out
BAND_HIGH, BAND_MED = 0.70, 0.84          # rows of the text / rows above and below
CONTRAST_HIGH, CONTRAST_MED = 2.2, 3.0    # (letters + 0.05) / (background + 0.05)
CALM_HIGH, CALM_MED = 1.6, 1.15           # bottom third motion / motion in the rest
CALM_FLOOR = 0.0035                       # mean frame difference (0..1) below which the bottom counts as calm anyway
RIGID_INTERNAL = 0.10                     # internal change / figure brightness below this is a rigid image
MOVE_PX = 0.35                            # figure speed (px per frame at 640x360) that counts as moving
RIGID_HIGH_S, FROZEN_MED_S = 1.0, 4.0     # seconds of rigid moving / of a fully frozen figure


# ---------------------------------------------------------------- small helpers
def lin(rgb8):
    c = rgb8.astype(np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722


def faded(S, t):
    """True while the picture is fading in or out (FADE under 0.97)."""
    f = getattr(S, "FADE", None)
    try:
        return callable(f) and float(f(t)) < 0.97
    except Exception:
        return False


def fmt_t(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def ffprobe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else float("nan")


def ffprobe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip().split(",")
    a, b = out[2].split("/")
    return int(out[0]), int(out[1]), float(a) / float(b)


def grab(video, t, w, h, gray=False):
    """One frame at time t, scaled to w x h (top row first)."""
    fmt, ch = ("gray", 1) if gray else ("rgb24", 3)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", video, "-frames:v", "1",
                          "-vf", f"scale={w}:{h}:flags=area", "-f", "rawvideo", "-pix_fmt", fmt, "-"],
                         capture_output=True).stdout
    if len(raw) < w * h * ch:
        return None
    a = np.frombuffer(raw[: w * h * ch], np.uint8)
    return a.reshape(h, w) if gray else a.reshape(h, w, 3)


def decode(video, w, h, fps=None, t0=None, dur=None):
    """All frames (gray uint8, N x h x w) of a stretch of the video."""
    cmd = ["ffmpeg", "-v", "error"]
    if t0 is not None:
        cmd += ["-ss", f"{max(t0, 0):.3f}"]
    cmd += ["-i", video]
    if dur is not None:
        cmd += ["-t", f"{dur:.3f}"]
    vf = f"scale={w}:{h}:flags=area"
    if fps:
        vf = f"fps={fps}," + vf
    cmd += ["-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (w * h)
    return np.frombuffer(raw[: n * w * h], np.uint8).reshape(n, h, w)


# ---------------------------------------------------------------- the song
def load_song(name):
    os.environ["SONG"] = name
    os.environ.setdefault("FEATURES", os.path.join(ROOT, "work", name, "features.npz"))
    if ENGINE not in sys.path:
        sys.path.insert(0, ENGINE)
    import song as S
    return S


def text_blocks(S):
    """Every text block the song shows: name, kind, times and its letter mask at 1920x1080 (top row first)."""
    import text as T
    blocks = []
    fd = float(getattr(S, "FORM_DUR", 3.0))
    total = float(S.NFRAMES) / S.FPS
    for p in S.PHRASES:
        if p["form"] >= 1e8:
            continue
        tex, _, b = T.render(p["label"], p["lines"], p["size"], y_center=p.get("y"))
        blocks.append(dict(name=p["label"], kind="expression", text=" / ".join(p["lines"]), appear=p["form"],
                           solid0=p["form"] + fd + FORM_EXTRA, solid1=p["hold"], gone=p["hold"] + DISSOLVE,
                           mask=tex[::-1, :, 0]))
    ty = T.title_y()
    if S.TITLE["form"] < 1e8:
        tex, _, b = T.render(S.TITLE["label"], S.TITLE["lines"], S.TITLE["size"], font_path=T.F_TITLE, y_center=ty)
        hold = S.TITLE.get("hold", 1e9)
        blocks.append(dict(name="End card title", kind="title", text=" / ".join(S.TITLE["lines"]),
                           appear=S.TITLE["form"], solid0=S.TITLE["form"] + fd + FORM_EXTRA,
                           solid1=min(hold, total), gone=min(hold + DISSOLVE, total), mask=tex[::-1, :, 0]))
    tg = S.TAGLINE
    if tg["t0"] < total:
        ttex, _ = T.render_tagline(tg["text"], ty)
        blocks.append(dict(name="End card lines", kind="tagline", text=tg["text"].replace("\n", " / "),
                           appear=tg["t0"], solid0=tg["t1"], solid1=total, gone=total, mask=ttex[::-1, :, 0]))
    for k, fr in enumerate(getattr(S, "FRAGMENTS", [])):
        ftex, _ = T.render_fragment(fr["text"], fr.get("dy", 0.0), fr.get("size", 74))
        styled = fr.get("style", "sparks") != "sparks"
        blocks.append(dict(name=f"Fragment {k + 1}", kind="fragment", text=fr["text"], appear=fr["t0"],
                           solid0=fr["t1"], solid1=fr["out"], gone=fr["out"] + (2.6 if styled else DISSOLVE),
                           mask=ftex[::-1, :, 0]))
    return blocks


def credit_layer(S):
    """The song title card and its small resting copy in the corner: (sharp texture, bbox) or None."""
    import text as T
    try:
        ctex, bbox = T.render_credit(S.CREDIT["song"], S.CREDIT["concert"])
    except Exception:
        return None
    return ctex[::-1, :, 0].astype(np.float32) / 255.0, bbox


def credit_mask(S, cl, t, w, h):
    """Coverage (0..1, h x w) of the title card or corner credit at time t, and its strength."""
    from scipy import ndimage as ndi
    if cl is None:
        return None, 0.0
    sharp, bbox = cl
    cr, c0 = S.credit_state(t, bbox)
    if cr[3] < 0.05:
        return None, float(cr[3])
    X, Y = np.meshgrid((np.arange(w) + 0.5) / w, 1.0 - (np.arange(h) + 0.5) / h)
    cu = (X - cr[0]) / cr[2] + c0[0]
    cv = (Y - cr[1]) / cr[2] + c0[1]
    m = ndi.map_coordinates(sharp, [(1.0 - cv) * sharp.shape[0] - 0.5, cu * sharp.shape[1] - 0.5], order=1,
                            mode="constant", cval=0.0)
    return m, float(cr[3])


def shrink(mask8, w, h):
    from PIL import Image
    return np.asarray(Image.fromarray(mask8).resize((w, h), Image.BOX)).astype(np.float32) / 255.0


# ---------------------------------------------------------------- 1. text: dark behind it, and legibility
def measure_text(lum, cov, others, h):
    """lum: linear luminance (h x w); cov: this block's letter coverage; others: coverage of other text on screen.
    Distances are measured in 1080p pixels."""
    from scipy import ndimage as ndi
    k = 1080.0 / h
    any_text = np.maximum(cov, others)
    d = ndi.distance_transform_edt(any_text < 0.12) * k
    d_self = ndi.distance_transform_edt(cov < 0.12) * k
    near_self = d_self < 260
    # the sky changes a lot from top to bottom (night sky, glowing horizon, lake), so compare the ring round the
    # letters with the sky further out in the same rows: strips about 40 px high, then the median over strips
    near = (d >= 30) & (d < 130) & near_self
    far = (d >= 140) & (d < 260) & near_self
    sh = max(int(round(40 / k)), 2)
    ratios, wts, med_n, med_f = [], [], [], []
    for r0 in range(0, lum.shape[0], sh):
        n_ = near[r0:r0 + sh]
        f_ = far[r0:r0 + sh]
        if n_.sum() < 12 or f_.sum() < 12:
            continue
        a_, b_ = float(np.median(lum[r0:r0 + sh][n_])), float(np.median(lum[r0:r0 + sh][f_]))
        ratios.append((a_ + 0.002) / (b_ + 0.002))
        wts.append(float(n_.sum()))
        med_n.append(a_)
        med_f.append(b_)
    if ratios:
        o = np.argsort(ratios)
        cw = np.cumsum(np.asarray(wts)[o]) / sum(wts)
        dip = float(np.asarray(ratios)[o][np.searchsorted(cw, 0.5)])
        ring, sky = float(np.median(med_n)), float(np.median(med_f))
    else:
        dip, ring, sky = float("nan"), float("nan"), float("nan")
    med = [ring, sky]
    # a band: the rows of the text against rows of the same height just above and below, across the width
    rows = np.nonzero(cov.max(axis=1) > 0.3)[0]
    band = float("nan")
    if rows.size:
        r0, r1 = rows.min(), rows.max() + 1
        hh = r1 - r0
        far = d > 130
        def rowmed(a, b):
            a, b = max(a, 0), min(b, lum.shape[0])
            if b - a < 2:
                return float("nan")
            sel = far[a:b]
            return float(np.median(lum[a:b][sel])) if sel.sum() > 30 else float("nan")
        mid = rowmed(r0, r1)
        up, dn = rowmed(r0 - hh, r0), rowmed(r1, r1 + hh)
        # darker than the rows on both sides: a smooth sky gradient never is
        ref = np.nanmin([up, dn]) if not (math.isnan(up) and math.isnan(dn)) else float("nan")
        if not math.isnan(ref) and not math.isnan(mid):
            band = mid / max(ref, 1e-4)
    # legibility: the letters against the light round them (bright end of the near ring)
    core = cov > 0.6
    if core.sum() < 20:
        core = cov > 0.4
    lt = float(np.median(lum[core])) if core.sum() else float("nan")
    bgsel = (d >= 35) & (d < 95) & near_self
    lb = float(np.percentile(lum[bgsel], 90)) if bgsel.sum() > 30 else float("nan")
    contrast = (lt + 0.05) / (lb + 0.05)
    return dict(dip=dip, band=band, contrast=contrast, letters=lt, background=lb, sky=sky,
                rings=[round(v, 4) for v in med])


def text_checks(S, blocks, cl, get_frame, times_for, w, h, issues, log):
    shr = {}
    for b in blocks:
        shr[b["name"]] = shrink(b["mask"], w, h)
    rows = []
    for b in blocks:
        ts = times_for(b)
        if not ts:
            continue
        worst = None
        for t in ts:
            lum = get_frame(t)
            if lum is None:
                continue
            cov = shr[b["name"]]
            others = np.zeros_like(cov)
            for o in blocks:
                if o is not b and o["appear"] <= t < o["gone"]:
                    others = np.maximum(others, shr[o["name"]])
            cm, ca = credit_mask(S, cl, t, w, h)
            if cm is not None:
                others = np.maximum(others, cm)
            m = measure_text(lum, cov, others, h)
            m["t"] = round(t, 2)
            rows.append(dict(block=b["name"], kind=b["kind"], **{k: (round(v, 3) if isinstance(v, float) else v)
                                                                for k, v in m.items()}))
            if worst is None or (m["dip"] < worst["dip"]):
                worst = m
            sev = None
            if m["dip"] < DARK_HIGH or m["band"] < BAND_HIGH:
                sev = "HIGH"
            elif m["dip"] < DARK_MED or m["band"] < BAND_MED:
                sev = "MEDIUM"
            if sev:
                what = []
                if m["dip"] < DARK_MED:
                    what.append(f"the sky just round the letters is {100 * (1 - m['dip']):.0f}% darker than the sky "
                                f"further out (a dark halo or veil)")
                if m["band"] < BAND_MED:
                    what.append(f"the rows behind the words are {100 * (1 - m['band']):.0f}% darker than the rows "
                                f"above and below (a dark band)")
                issues.append(dict(severity=sev, check="Dark behind text", at=m["t"], block=b["name"],
                                   detail="; ".join(what)))
            sevl = None
            if m["contrast"] < CONTRAST_HIGH:
                sevl = "HIGH"
            elif m["contrast"] < CONTRAST_MED:
                sevl = "MEDIUM"
            if sevl:
                issues.append(dict(severity=sevl, check="Legibility", at=m["t"], block=b["name"],
                                   detail=f"the letters are only {m['contrast']:.1f} times brighter than the light "
                                          f"round them (want {CONTRAST_MED:.0f} or more)"))
        if worst:
            log.append(f"{b['name']}: ring/sky {worst['dip']:.2f}, band {worst['band']:.2f}, "
                       f"contrast {worst['contrast']:.1f}")
    # the title card and the corner credit (engine design: its own soft shade, so at most MEDIUM)
    if cl is not None:
        c = S.CREDIT
        for t, label in ((0.5 * (c["t_full"] + c["t_move"]), "Title card"),
                         (c["t_rest"] + 1.0, "Corner credit")):
            if not times_for(dict(solid0=t - 0.01, solid1=t + 0.01, kind="credit")):
                continue
            lum = get_frame(t)
            cm, ca = credit_mask(S, cl, t, w, h)
            if lum is None or cm is None:
                continue
            others = np.zeros_like(cm)
            for o in blocks:
                if o["appear"] <= t < o["gone"]:
                    others = np.maximum(others, shr[o["name"]])
            m = measure_text(lum, cm, others, h)
            m["t"] = round(t, 2)
            rows.append(dict(block=label, kind="credit", **{k: (round(v, 3) if isinstance(v, float) else v)
                                                           for k, v in m.items()}))
            log.append(f"{label}: ring/sky {m['dip']:.2f}, band {m['band']:.2f}, contrast {m['contrast']:.1f}")
            if m["dip"] < DARK_MED:
                issues.append(dict(severity="MEDIUM", check="Dark behind text", at=m["t"], block=label,
                                   detail=f"the sky round the {label.lower()} is {100 * (1 - m['dip']):.0f}% darker "
                                          f"than further out"))
            if m["contrast"] < CONTRAST_MED:
                issues.append(dict(severity="MEDIUM", check="Legibility", at=m["t"], block=label,
                                   detail=f"the {label.lower()} is only {m['contrast']:.1f} times brighter than "
                                          f"the light round it"))
    return rows


# ---------------------------------------------------------------- 2. timings from the song file
def timing_checks(S, blocks, issues, log):
    total = float(S.NFRAMES) / S.FPS
    for b in blocks:
        solid = b["solid1"] - b["solid0"]
        if b["kind"] == "expression":
            log.append(f"{b['name']}: fully formed {fmt_t(b['solid0'])} to {fmt_t(b['solid1'])}, {solid:.1f} s")
            if solid < EXPR_SOLID_MIN:
                issues.append(dict(severity="HIGH", check="Reading time", at=round(b["solid0"], 2), block=b["name"],
                                   detail=f"fully formed for only {solid:.1f} s (need {EXPR_SOLID_MIN:.0f} s): "
                                          f"set hold to at least form + 9.75 = {b['appear'] + 9.75:.2f}"))
        elif b["kind"] == "fragment":
            log.append(f"{b['name']} ({b['text']}): solid {solid:.1f} s")
            if solid < FRAG_SOLID_MIN:
                issues.append(dict(severity="MEDIUM", check="Reading time", at=round(b["solid0"], 2), block=b["name"],
                                   detail=f"fragment solid for only {solid:.1f} s (need {FRAG_SOLID_MIN:.0f} s)"))
    # nothing over an expression, and a clean gap between texts
    seq = sorted([b for b in blocks if b["kind"] in ("expression", "fragment", "title")], key=lambda b: b["appear"])
    for i, a in enumerate(seq):
        for b in seq[i + 1:]:
            if b["appear"] >= a["gone"] + GAP_MIN:
                continue
            if b["appear"] < a["gone"] and {a["kind"], b["kind"]} != {"title"}:
                both = a["kind"] == "expression" or b["kind"] == "expression"
                issues.append(dict(severity="MEDIUM" if both else "LOW", check="Reading time",
                                   at=round(b["appear"], 2), block=f"{a['name']} + {b['name']}",
                                   detail=f"{b['name']} starts at {fmt_t(b['appear'])} while {a['name']} is still on "
                                          f"screen (until {fmt_t(a['gone'])})"))
            elif b["appear"] >= a["gone"]:
                issues.append(dict(severity="LOW", check="Reading time", at=round(b["appear"], 2),
                                   block=f"{a['name']} then {b['name']}",
                                   detail=f"only {b['appear'] - a['gone']:.1f} s between {a['name']} leaving and "
                                          f"{b['name']} starting (want {GAP_MIN} s)"))
    # end card
    tg = S.TAGLINE
    nlines = len(tg["text"].split("\n"))
    title = [b for b in blocks if b["kind"] == "title"]
    tagb = [b for b in blocks if b["kind"] == "tagline"]
    if nlines != 3:
        issues.append(dict(severity="HIGH", check="End card", at=round(tg["t0"], 2), block="End card lines",
                           detail=f"the end card has {nlines} line(s) under the title; it needs three (peace line, "
                                  f"date and time, place), PHASE2.md item 7"))
    if title and tagb:
        start = max(title[0]["solid0"], tagb[0]["solid0"])
        end = total
        fade = getattr(S, "FADE", None)
        if callable(fade):
            for t in np.arange(start, total, 0.05):
                if fade(t) < 0.97:
                    end = float(t)
                    break
        hold = end - start
        log.append(f"End card: {nlines} lines, whole from {fmt_t(start)} to {fmt_t(end)}, held {hold:.1f} s")
        if hold < END_HOLD_MIN:
            issues.append(dict(severity="HIGH", check="End card", at=round(start, 2), block="End card",
                               detail=f"the whole end card is held for only {hold:.1f} s (need {END_HOLD_MIN:.0f} s)"))
    else:
        issues.append(dict(severity="HIGH", check="End card", at=None, block="End card",
                           detail="no end card (title and lines) inside the video"))


def dash_checks(S, song_name, extra, issues, log):
    files = [os.path.join(ENGINE, "songs", song_name + ".py")]
    m = re.match(r"s(\d\d)", song_name)
    if m:
        st = os.path.join(ROOT, "project-docs", "status", m.group(1) + ".md")
        if os.path.exists(st):
            files.append(st)
    files += extra
    n = 0
    for f in files:
        try:
            lines = open(f, encoding="utf-8").read().split("\n")
        except OSError:
            continue
        n += 1
        for i, line in enumerate(lines, 1):
            if "—" in line or "–" in line:
                kind = "em dash" if "—" in line else "en dash"
                issues.append(dict(severity="HIGH", check="Dashes", at=None, block=os.path.relpath(f, ROOT),
                                   detail=f"line {i} has an {kind}: {line.strip()[:90]}"))
    log.append(f"checked {n} file(s) for em and en dashes")


# ---------------------------------------------------------------- 3. figures
def fig_value(m, key, default, t):
    v = m.get(key, default)
    if callable(v):
        return float(v(t))
    if isinstance(v, (tuple, list)) and len(v) == 2:
        a, b = m.get("move", (m["t0"], m["t1"]))
        u = min(max((t - a) / max(b - a, 1e-3), 0.0), 1.0)
        e = m.get("ease", "smooth")
        u = {"linear": u, "in": u * u, "out": 1 - (1 - u) ** 2}.get(e, u * u * (3 - 2 * u))
        return float(v[0]) + (float(v[1]) - float(v[0])) * u
    return float(v)


def fig_rect(S, m, aspect, t):
    """The figure's box (x, y from the bottom, width, height in screen fractions), as engine/upgrade.py draws it."""
    x, y = fig_value(m, "x", 0.5, t), fig_value(m, "y", 0.18, t)
    hgt = fig_value(m, "height", 0.34, t) * (1.0 + 0.006 * math.sin(t * 1.1 + x * 9.0))
    wid = hgt * aspect / S.ASPECT
    bob = float(m.get("bob", 0.0))
    if bob > 0.0:
        dt = 0.05
        vx = (fig_value(m, "x", 0.5, t + dt) - fig_value(m, "x", 0.5, t - dt)) / (2 * dt)
        speed = min(abs(vx) / 0.02, 1.0)
        step = 0.10 * hgt
        y += bob * 0.010 * hgt * speed * abs(math.sin(math.pi * x / max(step, 1e-3)))
        hgt *= 1.0 + bob * 0.004 * speed * math.sin(2 * math.pi * x / max(step, 1e-3))
    return (x - wid / 2.0, y, wid, hgt)


def figure_list(S):
    from PIL import Image
    out = []
    for i, m in enumerate(getattr(S, "FIGURES", []) or []):
        try:
            p = m["poses"][0]
            p = p if os.path.isabs(p) else os.path.join(ROOT, p)
            W0, H0 = Image.open(p).size
            aspect = W0 / H0
        except Exception:
            aspect = 0.45
        name = m.get("name") or os.path.splitext(os.path.basename(str(m.get("poses", ["figure"])[0])))[0]
        out.append(dict(i=i, meta=m, aspect=aspect, name=f"Figure {i + 1} ({name})",
                        on0=m["t0"] + m.get("gather", 3.0) * 1.05, on1=m["t1"]))
    return out


def box_px(r, w, h, pad=0.10):
    x, y, bw, bh = r
    x0, x1 = (x - pad * bw) * w, (x + bw * (1 + pad)) * w
    y0, y1 = (1 - (y + bh * (1 + pad))) * h, (1 - (y - pad * bh)) * h
    return int(max(math.floor(x0), 0)), int(max(math.floor(y0), 0)), int(min(math.ceil(x1), w)), int(min(math.ceil(y1), h))


def figure_checks(S, figs, video, vfps, issues, log, w=640, h=360):
    from PIL import Image
    rows = []
    for f in figs:
        a, b = f["on0"], f["on1"]
        if b - a < 0.4:
            continue
        # up to 6 stretches of 1.2 s spread over the time the figure is whole
        n = max(1, min(6, int((b - a) / 1.5)))
        starts = [a + (b - a - 1.2) * k / max(n - 1, 1) for k in range(n)] if b - a > 1.2 else [a]
        rigid_s = frozen_s = moving_s = 0.0
        internals, speeds = [], []
        for s0 in starts:
            fr = decode(video, w, h, t0=s0, dur=min(1.2, b - s0)).astype(np.float32) / 255.0
            for k in range(len(fr) - 1):
                t = s0 + k / vfps
                r0, r1 = fig_rect(S, f["meta"], f["aspect"], t), fig_rect(S, f["meta"], f["aspect"], t + 1 / vfps)
                x0, y0, x1, y1 = box_px(r0, w, h)
                X0, Y0, X1, Y1 = box_px(r1, w, h)
                if x1 - x0 < 4 or y1 - y0 < 6 or X1 - X0 < 4 or Y1 - Y0 < 6:
                    continue
                c0 = fr[k][y0:y1, x0:x1]
                c1 = np.asarray(Image.fromarray(fr[k + 1][Y0:Y1, X0:X1]).resize((x1 - x0, y1 - y0), Image.BILINEAR))
                same = fr[k + 1][y0:y1, x0:x1]
                border = np.concatenate([c0[0], c0[-1], c0[:, 0], c0[:, -1]])
                bg = float(np.median(border))
                pk = float(np.percentile(c0, 99))
                sel = (c0 - bg) > max(0.20 * (pk - bg), 6 / 255.0)
                if sel.sum() < 10:
                    continue
                sig = float(np.mean(c0[sel] - bg))
                internal = float(np.mean(np.abs(c0 - c1)[sel])) / max(sig, 1e-4)
                fixed = float(np.mean(np.abs(c0 - same)[sel])) / max(sig, 1e-4)
                cx0, cx1 = (r0[0] + r0[2] / 2) * w, (r1[0] + r1[2] / 2) * w
                cy0, cy1 = (r0[1] + r0[3] / 2) * h, (r1[1] + r1[3] / 2) * h
                speed = math.hypot(cx1 - cx0, cy1 - cy0)
                internals.append(internal)
                speeds.append(speed)
                dt = 1 / vfps
                if speed > MOVE_PX:
                    moving_s += dt
                    if internal < RIGID_INTERNAL:
                        rigid_s += dt
                elif internal < RIGID_INTERNAL and fixed < RIGID_INTERNAL:
                    frozen_s += dt
        if not internals:
            continue
        mi = float(np.median(internals))
        rows.append(dict(figure=f["name"], whole=[round(a, 2), round(b, 2)], internal_median=round(mi, 3),
                         speed_px=round(float(np.median(speeds)), 2), moving_s=round(moving_s, 2),
                         rigid_s=round(rigid_s, 2), frozen_s=round(frozen_s, 2), pairs=len(internals)))
        log.append(f"{f['name']}: internal change {mi:.3f} (median), moving {moving_s:.1f} s of which rigid "
                   f"{rigid_s:.1f} s, frozen in place {frozen_s:.1f} s ({len(internals)} frame pairs sampled)")
        span = sum(min(1.2, b - s0) for s0 in starts)
        if rigid_s >= min(RIGID_HIGH_S, 0.5 * span) and rigid_s >= 0.5 * moving_s:
            issues.append(dict(severity="HIGH", check="Static figures", at=round(a, 2), block=f["name"],
                               detail=f"moves across the screen as one rigid picture: inside its box almost nothing "
                                      f"changes from frame to frame (change {mi:.2f}, want {RIGID_INTERNAL} or more) "
                                      f"in {rigid_s:.1f} of {moving_s:.1f} s of movement sampled"))
        elif frozen_s >= min(FROZEN_MED_S, 0.6 * span):
            issues.append(dict(severity="MEDIUM", check="Static figures", at=round(a, 2), block=f["name"],
                               detail=f"stands frozen like a still picture for {frozen_s:.1f} s of the "
                                      f"{span:.1f} s sampled"))
    return rows


# ---------------------------------------------------------------- 4. calm bottom third
def calm_checks(S, figs, video, issues, log, w=320, h=180, fps=10):
    fr = decode(video, w, h, fps=fps).astype(np.float32) / 255.0
    if len(fr) < 3:
        return []
    diff = np.abs(np.diff(fr, axis=0))
    cut = int(round(h * (1 - 0.335)))
    rows, win = [], 2.0
    per = int(win * fps)
    for k in range(0, len(diff), per):
        seg = diff[k:k + per]
        t0 = k / fps
        t1 = t0 + len(seg) / fps
        mask = np.ones((h, w), bool)
        for f in figs:   # people of light are allowed to move in the lower part; judge the rest of the scene
            if f["meta"]["t0"] < t1 and f["meta"]["t1"] + 3.5 > t0:
                for tt in np.arange(t0, t1, 0.5):
                    x0, y0, x1, y1 = box_px(fig_rect(S, f["meta"], f["aspect"], tt), w, h, pad=0.25)
                    mask[y0:y1, x0:x1] = False
        e = seg.mean(axis=0)
        bot = float(e[cut:][mask[cut:]].mean()) if mask[cut:].any() else 0.0
        top = float(e[:cut][mask[:cut]].mean()) if mask[:cut].any() else 0.0
        ratio = bot / max(top, 1e-5)
        rows.append(dict(t0=round(t0, 1), t1=round(t1, 1), bottom=round(bot, 5), rest=round(top, 5),
                         ratio=round(ratio, 2)))
    bad_hi = [r for r in rows if r["ratio"] > CALM_HIGH and r["bottom"] > CALM_FLOOR]
    bad_md = [r for r in rows if CALM_MED < r["ratio"] <= CALM_HIGH and r["bottom"] > CALM_FLOOR]
    tot_b = float(np.mean([r["bottom"] for r in rows]))
    tot_r = float(np.mean([r["rest"] for r in rows]))
    log.append(f"bottom third moves {tot_b / max(tot_r, 1e-5):.2f} times as much as the rest over the whole video "
               f"(want under {CALM_MED}); busiest 2 s: {max(r['ratio'] for r in rows):.2f}")

    def spans(rs):
        out = []
        for r in rs:
            if out and abs(out[-1][1] - r["t0"]) < 1e-6:
                out[-1][1] = r["t1"]
                out[-1][2] = max(out[-1][2], r["ratio"])
            else:
                out.append([r["t0"], r["t1"], r["ratio"]])
        return out
    for sev, rs in (("HIGH", bad_hi), ("MEDIUM", bad_md)):
        for a, b, rt in spans(rs):
            issues.append(dict(severity=sev, check="Calm bottom third", at=a, block=f"{fmt_t(a)} to {fmt_t(b)}",
                               detail=f"the bottom third moves {rt:.1f} times as much as the rest of the picture "
                                      f"(want under {CALM_MED})"))
    return rows


# ---------------------------------------------------------------- report
SEV_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def write_report(out, meta, issues, sections, data):
    os.makedirs(out, exist_ok=True)
    issues.sort(key=lambda i: (SEV_ORDER[i["severity"]], i["at"] if i["at"] is not None else -1))
    nh = sum(i["severity"] == "HIGH" for i in issues)
    nm = sum(i["severity"] == "MEDIUM" for i in issues)
    nl = sum(i["severity"] == "LOW" for i in issues)
    verdict = "FAIL" if nh else ("CHECK" if nm else "PASS")
    L = [f"# Quality check: {meta['song']}", "",
         f"**{verdict}**: {nh} high, {nm} medium, {nl} low.", "",
         f"Checked: {meta['source']}. Took {meta['seconds']:.0f} s.", ""]
    if issues:
        L += ["| Level | Check | When | Where | What |", "|---|---|---|---|---|"]
        for i in issues:
            when = fmt_t(i["at"]) if i["at"] is not None else ""
            L.append(f"| {i['severity']} | {i['check']} | {when} | {i['block']} | {i['detail']} |")
        L.append("")
    else:
        L += ["No problems found.", ""]
    L += ["## Measurements", ""]
    for title, lines in sections:
        if lines:
            L += [f"**{title}**", ""] + [f"- {x}" for x in lines] + [""]
    L += ["## What the checks mean", "",
          f"- Dark behind text: median sky brightness in rings 30 to 130 px round the letters (1080p pixels) against "
          f"the sky 140 to 240 px out. Under {DARK_MED} is a visible dark halo or veil, under {DARK_HIGH} a strong one. "
          f"Also the rows of the words against rows above and below (a band): under {BAND_MED} / {BAND_HIGH}.",
          f"- Legibility: (letters + 0.05) / (brightest tenth of the light round them + 0.05), in linear light. "
          f"Under {CONTRAST_MED} is weak, under {CONTRAST_HIGH} hard to read.",
          f"- Reading time: expressions fully formed (form + FORM_DUR + 0.75 s) until hold, at least "
          f"{EXPR_SOLID_MIN:.0f} s; fragments {FRAG_SOLID_MIN:.0f} s; no fragment over an expression; "
          f"{GAP_MIN} s gap.",
          f"- End card: three lines under the title, whole for at least {END_HOLD_MIN:.0f} s before the fade.",
          f"- Calm bottom third: mean frame difference in the bottom third against the rest, per 2 s, people of light "
          f"left out. Over {CALM_MED} is busy, over {CALM_HIGH} very busy.",
          f"- Static figures: frames inside each figure's box, lined up with where the figure has moved to. Change "
          f"under {RIGID_INTERNAL} of the figure's brightness while it moves means it slides as one rigid picture.",
          ""]
    open(os.path.join(out, "qa-report.md"), "w", encoding="utf-8").write("\n".join(L))
    data.update(meta=meta, verdict=verdict, counts=dict(high=nh, medium=nm, low=nl), issues=issues)
    open(os.path.join(out, "qa.json"), "w", encoding="utf-8").write(json.dumps(data, indent=1, default=float))
    return verdict, nh, nm, "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--song", required=True)
    ap.add_argument("--video", default="")
    ap.add_argument("--stills", default="", help="folder of stills named tSSSS.SS.png")
    ap.add_argument("--static-only", action="store_true", help="only the checks that need no frames")
    ap.add_argument("--out", default="qa")
    ap.add_argument("--files", nargs="*", default=[], help="more files to check for dashes")
    ap.add_argument("--fail-on", default="none", choices=["none", "high"])
    ap.add_argument("--name", default="")
    a = ap.parse_args()
    t_start = time.time()
    S = load_song(a.song)
    issues, data, sections = [], {}, []
    log_t, log_d = [], []
    blocks = text_blocks(S)
    timing_checks(S, blocks, issues, log_t)
    dash_checks(S, a.song, a.files, issues, log_d)
    sections += [("Reading time and end card (from the song file)", log_t), ("Dashes", log_d)]
    total = float(S.NFRAMES) / S.FPS
    source = "song file only"
    figs = figure_list(S)
    cl = credit_layer(S)
    if a.video:
        source = os.path.basename(a.video)
        vw, vh, vfps = ffprobe_size(a.video)
        dur = ffprobe_duration(a.video)
        log_l = [f"video {dur:.2f} s at {vw}x{vh}, {vfps:g} fps; the song file says {total:.2f} s"]
        if not abs(dur - total) < max(0.15, 1.5 / vfps):
            issues.append(dict(severity="HIGH", check="Length", at=None, block=source,
                               detail=f"the video is {dur:.2f} s but the song file says {total:.2f} s"))
        sections.append(("Length", log_l))
        w, h = (vw, vh) if vh <= 540 else (960, 540)
        cache = {}

        def get_frame(t):
            if t not in cache:
                f = grab(a.video, t, w, h)
                cache[t] = lin(f) if f is not None else None
            return cache[t]

        def times_for(b):
            s0, s1 = b["solid0"], min(b["solid1"], dur - 0.05)
            while s1 > s0 and faded(S, s1):
                s1 -= 0.1
            if s1 - s0 < 0.1:
                return []
            if b.get("kind") == "credit":
                return [s0]
            if s1 - s0 < 1.0:
                return [0.5 * (s0 + s1)]
            return [t for t in (s0 + 0.25, 0.5 * (s0 + s1), s1 - 0.25) if not faded(S, t)]
        log_x = []
        data["text"] = text_checks(S, blocks, cl, get_frame, times_for, w, h, issues, log_x)
        sections.append(("Dark behind text and legibility (worst moment per block)", log_x))
        log_c = []
        data["calm"] = calm_checks(S, figs, a.video, issues, log_c)
        sections.append(("Calm bottom third", log_c))
        log_f = []
        data["figures"] = figure_checks(S, figs, a.video, vfps, issues, log_f)
        if not figs:
            log_f.append("no people of light in this song")
        sections.append(("People of light", log_f))
    elif a.stills:
        from PIL import Image
        files = sorted(glob.glob(os.path.join(a.stills, "t*.png")))
        stills = {}
        for f in files:
            mt = re.match(r"t(\d+(?:\.\d+)?)\.png$", os.path.basename(f))
            if mt:
                stills[float(mt.group(1))] = f
        source = f"{len(stills)} stills in {os.path.basename(os.path.normpath(a.stills))}"
        if stills:
            im0 = Image.open(next(iter(stills.values())))
            vw, vh = im0.size
            w, h = (vw, vh) if vh <= 540 else (960, 540)

            def get_frame(t):
                return lin(np.asarray(Image.open(stills[t]).convert("RGB").resize((w, h), Image.BOX)))

            def times_for(b):
                return [t for t in stills if b["solid0"] <= t <= b["solid1"] and not faded(S, t)]
            log_x = []
            data["text"] = text_checks(S, blocks, cl, get_frame, times_for, w, h, issues, log_x)
            covered = {r["block"] for r in data["text"]}
            missed = [b["name"] for b in blocks if b["name"] not in covered]
            if missed:
                log_x.append("no still falls where these are fully formed: " + ", ".join(missed))
            sections.append(("Dark behind text and legibility (worst moment per block)", log_x))
    meta = dict(song=a.song, name=a.name, source=source, seconds=time.time() - t_start)
    verdict, nh, nm, md = write_report(a.out, meta, issues, sections, data)
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a", encoding="utf-8") as fh:
            fh.write(md + "\n")
    if os.environ.get("GITHUB_ACTIONS"):
        for i in issues:
            if i["severity"] in ("HIGH", "MEDIUM"):
                kind = "error" if i["severity"] == "HIGH" else "warning"
                when = f" at {fmt_t(i['at'])}" if i["at"] is not None else ""
                print(f"::{kind} title=QA {i['check']}::{i['block']}{when}: {i['detail']}")
    print(md)
    print(f"QA {verdict}: {nh} high, {nm} medium, in {time.time() - t_start:.0f} s")
    if a.fail_on == "high" and nh:
        sys.exit(1)


if __name__ == "__main__":
    main()
