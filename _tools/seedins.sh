#!/bin/bash
# Are instruction counts invariant under the seed? (no re-simulation needed)
for v in qnn qnn_dotp8 qnn_dotp8x4 qnn_dotp8x4c; do
  for tag in 8 80x01352505 80x00001234 80xdeadbeef; do
    d=/tmp/sd_${v}_${tag}
    [ -d "$d" ] || continue
    line=$(awk '/Begin Simulation Statistics/{n++}
                n==2 && /^simInsts /{print $2}' $d/stats.txt)
    printf '%-14s %-14s simInsts=%s\n' "$v" "$tag" "$line"
  done
done
echo INSDONE
