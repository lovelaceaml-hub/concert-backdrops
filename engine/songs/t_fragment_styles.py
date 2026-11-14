"""Stills test only: the demo with the two other fragment styles (write, petals) in place of its own fragments."""
import arch as _arch
import songs.demo_upgrade as _demo
from songs.demo_upgrade import *  # noqa: F401,F403

_demo.star_state, _demo.link_state = _arch.make(_demo)   # the demo's params() looks these up in its own module

FRAGMENTS = [
    dict(text="opened her heart", t0=5.0, t1=8.0, out=10.5, dy=0.10, size=92, style="write"),
    dict(text="the pain you held inside", t0=22.5, t1=26.0, out=28.5, dy=0.0, size=88, style="petals",
         colors=("#ffb3c6", "#ffe6dc")),
]
