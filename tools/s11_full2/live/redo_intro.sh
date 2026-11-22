#!/bin/bash
# After this machine's first parts (0-12) finish, re-render the church parts of the intro (2-8) with the emblem.
H=/home/user/concert-backdrops/work/s11_full2/h7
until [ -f $H/c10.mp4 ] && [ -f $H/c11.mp4 ] && [ -f $H/c12.mp4 ]; do sleep 15; done
mkdir -p $H/old
for c in 02 03 04 05 06 07 08; do mv $H/c$c.mp4 $H/old/ 2>/dev/null; rmdir $H/locks/c$c 2>/dev/null; rm -rf $H/locks/c$c; done
cd /home/user/wt-render
for i in 1 2 3 4; do nohup python3 tools/s11_full2/render_chunks.py --order 2-8 --parts $H --scale 0.5 --fps 30 > $H/r$i.log 2>&1 & sleep 1; done
echo started
