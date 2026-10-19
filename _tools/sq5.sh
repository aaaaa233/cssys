#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
for v in qnn qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c; do
  f=out/sweeps/lab5b_${v}/p000/stats.txt
  [ -f "$f" ] || { echo "$v MISSING $f"; continue; }
  awk -v V="$v" '/Begin Simulation Statistics/{n++}
    n==2 && /^system.cpu.commit.branchMispredicts /{mp=$2}
    n==2 && /^system.cpu.commit.commitSquashedInsts /{sq=$2}
    n==2 && /^system.cpu.commitStats0.numInsts /{ins=$2}
    n==2 && /^system.cpu.numCycles /{cyc=$2}
    END{printf "%-14s mispred=%s squashed=%s insts=%s cycles=%s\n", V, mp, sq, ins, cyc}' $f
done
echo SQDONE
