#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
for v in qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4; do
  echo "==== $v"
  awk '/Begin Simulation Statistics/{n++} n==2' \
      out/sweeps/lab5_$v/p000_width-4/stats.txt \
    | grep -E 'cpu\.(numCycles|fetch\.(cycles|rateDist::mean|icacheStallCycles|Insts|Branches|nisnDist::mean|squashCycles|blockedCycles|MiscStallCycles|PendingTrapStallCycles|TlbCycles))|cpu\.fetchStats|rename\.(blockCycles|serializeStallCycles)|iew\.(dispatchStallCycles)|commit\.(commitSquashedInsts)' \
    | head -30
done
