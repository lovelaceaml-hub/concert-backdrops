#!/bin/bash
# Render stills (LIVE seconds) in parallel across the CPU cores.  No em dash or en dash in this file.
#   tools/s07_full2/stills.sh <outdir> <scale> t1,t2,t3,...
out=$1; scale=$2; IFS=',' read -ra T <<< "$3"
n=$(nproc); here=$(dirname "$0")
for ((k=0; k<n; k++)); do
  sel=(); for ((i=k; i<${#T[@]}; i+=n)); do sel+=("${T[$i]}"); done
  [ ${#sel[@]} -eq 0 ] && continue
  (IFS=','; python "$here/render.py" --stills "${sel[*]}" --scale "$scale" --outdir "$out" 2>&1 | grep -E "CPU|Error|error" ) &
done
wait
