#!/bin/bash
# Exit when a part finishes in h5 or after 120 s, then rebuild the status document.
H=/home/user/concert-backdrops/work/s11_full2/h8
a=$(ls $H | grep -c '^c[0-9][0-9]\.mp4$'); t=0
while [ $t -lt 120 ]; do sleep 10; t=$((t+10)); b=$(ls $H | grep -c '^c[0-9][0-9]\.mp4$'); [ "$b" != "$a" ] && break; done
python3 $(dirname $0)/status_gen.py
