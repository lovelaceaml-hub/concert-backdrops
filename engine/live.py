"""Live cue mode (I10): plays a song file in real time, fullscreen, on a venue computer with a graphics card.

An operator steps through the song's cues by hand, so the picture follows the live performance:

    space or right arrow   next cue
    left arrow             previous cue
    1 to 9, 0              cue 1 to 9, 0 is cue 10
    b                      fade to black, and back
    Esc                    quit

Every jump is a smooth crossfade (--xfade seconds, default 2). A cue with a loop end holds: when the picture
reaches the loop end it crossfades back to the cue's start (over the song's LOOP_XFADE, default 6 seconds)
and keeps doing so until the operator moves on. A cue without a loop end simply plays on through the song and
holds the last frame at the very end.

The cues come from the song file:

    CUES = [("Opening", 0.0, None), ("Verse 1 hold", 12.0, 40.0), ("Chorus", 40.0, None), ...]

A song without CUES gets one cue that plays from the start (a LOOP_SECONDS song: one cue that loops forever).

Start it with (see engine/UPGRADE-HOWTO.md, section I10):

    python engine/live.py s03_original --audio audio/promo/s03.mp3

There is no sound: the musicians play live. The audio file is only measured once (the song's lights, rings
and skyline follow it), and the measurement is kept in work/<song>/features.npz for next time.
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def parse_cues(S):
    """The song's cues as a list of (name, start, loop end or None), checked."""
    raw = getattr(S, "CUES", None)
    if not raw:
        loop = getattr(S, "LOOP_SECONDS", None)
        raw = [("Loop", 0.0, float(loop))] if loop else [("Start", 0.0, None)]
    total = float(getattr(S, "TOTAL", 1e9))
    cues = []
    for k, c in enumerate(raw):
        if not (isinstance(c, (list, tuple)) and len(c) == 3):
            raise SystemExit(f"CUES[{k}] must be (name, start seconds, loop end seconds or None), got {c!r}")
        name, t0, t1 = str(c[0]), float(c[1]), (None if c[2] is None else float(c[2]))
        if not 0.0 <= t0 < total:
            raise SystemExit(f"cue {k + 1} ({name}) starts at {t0}, outside the song (0 to {total})")
        if t1 is not None and not (t0 + 1.0 <= t1 <= total + 1e-6):
            raise SystemExit(f"cue {k + 1} ({name}) loops back at {t1}: it must be at least 1 s after its start "
                             f"{t0} and inside the song (up to {total})")
        cues.append((name, t0, t1))
    return cues


def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


class Player:
    """Which song times to draw now: the current stream, and the one it is fading from (pure logic, no GL)."""

    def __init__(self, cues, total, fps, xfade=2.0, loop_xfade=6.0):
        self.cues, self.total, self.fps = cues, total, fps
        self.xfade, self.loop_xfade = xfade, loop_xfade
        self.idx = 0
        self.cur = (cues[0][1], 0.0)   # (song time at the stream's start, clock time at its start)
        self.old = None                # (stream, fade start clock, fade length)

    def song_time(self, stream, now):
        return min(stream[0] + (now - stream[1]), self.total - 1.0 / self.fps)

    def go(self, idx, now, dur=None):
        if not 0 <= idx < len(self.cues):
            return False
        self.old = (self.cur, now, self.xfade if dur is None else dur)
        self.idx = idx
        self.cur = (self.cues[idx][1], now)
        return True

    def tick(self, now):
        """Returns [(song time, weight), ...] to draw and mix now."""
        name, t0, t1 = self.cues[self.idx]
        t = self.song_time(self.cur, now)
        if t1 is not None and self.old is None:
            xf = min(self.loop_xfade, (t1 - t0) / 2.0)
            if t >= t1 - xf:   # hold: fade from the loop's end back into its start
                self.old = (self.cur, now, xf)
                self.cur = (t0, now)
                t = t0
        if self.old is None:
            return [(t, 1.0)]
        stream, f0, dur = self.old
        k = smooth((now - f0) / max(dur, 1e-3))
        if k >= 1.0:
            self.old = None
            return [(t, 1.0)]
        return [(self.song_time(stream, now), 1.0 - k), (t, k)]


BLIT_VS = """
#version 330
in vec2 aPos; out vec2 vUV;
void main(){ vUV = aPos*0.5+0.5; gl_Position = vec4(aPos, 0.0, 1.0); }
"""
BLIT_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uA, uB; uniform float uK, uLevel;
void main(){
  vec2 uv = vec2(vUV.x, 1.0-vUV.y);   // the engine's frames are stored top row first
  o = vec4(mix(texture(uA, uv).rgb, texture(uB, uv).rgb, uK)*uLevel, 1.0);
}
"""


def ensure_features(song, audio):
    feat = os.path.join(ROOT, "work", song, "features.npz")
    os.environ.setdefault("FEATURES", feat)
    if os.path.exists(os.environ["FEATURES"]) or not audio:
        return
    os.makedirs(os.path.dirname(feat), exist_ok=True)
    wav = os.path.join(os.path.dirname(feat), "audio.wav")
    print("measuring the music once:", audio, flush=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio, "-ac", "1", "-ar", "22050", wav], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, "analyze.py"), wav, feat], check=True, stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser(description="Play a song file live, fullscreen, cue by cue.")
    ap.add_argument("song", help="song file in engine/songs, without .py (for example s03_original)")
    ap.add_argument("--audio", default="", help="the song's audio, measured once if work/<song>/features.npz is missing")
    ap.add_argument("--xfade", type=float, default=2.0, help="seconds of crossfade when the operator jumps (default 2)")
    ap.add_argument("--res", default="1080p", choices=["1080p", "4k"], help="size the engine draws at (default 1080p)")
    ap.add_argument("--display", type=int, default=0, help="which screen to fill (0 is the main one)")
    ap.add_argument("--windowed", action="store_true", help="a window instead of fullscreen, for a rehearsal")
    a = ap.parse_args()

    os.environ["SONG"] = a.song
    os.environ["OUT_RES"] = a.res   # the words are drawn at this size too
    os.environ["LIBGL_ALWAYS_SOFTWARE"] = "0"   # use the graphics card (the cloud render forces software)
    ensure_features(a.song, a.audio)
    sys.path.insert(0, HERE)

    import pygame
    import moderngl
    import numpy as np

    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
    flags = pygame.OPENGL | pygame.DOUBLEBUF | (0 if a.windowed else pygame.FULLSCREEN)
    size = (1280, 720) if a.windowed else (0, 0)
    pygame.display.set_mode(size, flags, display=a.display, vsync=1)
    pygame.mouse.set_visible(a.windowed)
    sw, sh = pygame.display.get_window_size()
    ctx = moderngl.create_context()

    import song as S
    import render
    cues = parse_cues(S)
    scale = 2 if a.res == "4k" else 1
    R = render.Renderer(S.W * scale, S.H * scale, ctx=ctx)
    w, h = R.w, R.h

    def target():
        t = ctx.texture((w, h), 3, dtype="f1")
        t.filter = (moderngl.LINEAR, moderngl.LINEAR)
        return t, ctx.framebuffer([t])

    tA, fA = target()
    tB, fB = target()
    blit = ctx.program(vertex_shader=BLIT_VS, fragment_shader=BLIT_FS)
    quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
    vblit = ctx.vertex_array(blit, [(quad, "2f", "aPos")])
    # fit the picture to the screen, black bars if the screen's shape differs
    k = min(sw / w, sh / h)
    vw, vh = int(w * k), int(h * k)
    view = ((sw - vw) // 2, (sh - vh) // 2, vw, vh)

    player = Player(cues, float(S.TOTAL), S.FPS, a.xfade, float(getattr(S, "LOOP_XFADE", 6.0)))
    level, black = 1.0, False
    keys = {pygame.K_1 + i: i for i in range(9)}
    keys[pygame.K_0] = 9

    def show_cue():
        name, t0, t1 = cues[player.idx]
        txt = f"cue {player.idx + 1}/{len(cues)}: {name} (from {t0:.1f} s" + (f", holds until next cue)" if t1 else ")")
        print(txt, flush=True)
        pygame.display.set_caption(f"{a.song}  {txt}")

    show_cue()
    clock0 = time.perf_counter()
    prev = 0.0
    n = 0
    running = True
    while running:
        now = time.perf_counter() - clock0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key in (pygame.K_SPACE, pygame.K_RIGHT, pygame.K_PAGEDOWN):
                    if player.go(player.idx + 1, now):
                        show_cue()
                elif ev.key in (pygame.K_LEFT, pygame.K_PAGEUP):
                    if player.go(player.idx - 1, now):
                        show_cue()
                elif ev.key in keys:
                    if player.go(keys[ev.key], now):
                        show_cue()
                elif ev.key == pygame.K_b:
                    black = not black
        draw = player.tick(now)
        for (t, _w), fb in zip(draw, (fA, fB)):
            R.frame(t, n)
            ctx.copy_framebuffer(fb, R.f_out)
        dt, prev = now - prev, now
        level += ((0.0 if black else 1.0) - level) * min(dt / 0.6, 1.0)
        ctx.screen.use()
        ctx.disable(moderngl.BLEND)
        ctx.screen.viewport = (0, 0, sw, sh)
        ctx.screen.clear(0.0, 0.0, 0.0, 1.0)
        ctx.screen.viewport = view
        tA.use(location=0)
        (tB if len(draw) > 1 else tA).use(location=1)
        blit["uA"].value, blit["uB"].value = 0, 1
        blit["uK"].value = float(draw[1][1]) if len(draw) > 1 else 0.0
        blit["uLevel"].value = float(level)
        vblit.render(moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        n += 1
        if n % 300 == 0:
            print(f"{n / (time.perf_counter() - clock0):.1f} frames per second", flush=True)
    pygame.quit()


if __name__ == "__main__":
    main()
