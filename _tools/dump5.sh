#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
R="python3 framework/report.py"
echo "===== MAIN ====="
for v in qnn qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c; do
  D=out/sweeps/lab5_$v/p000/stats.txt
  ST=$(awk '/Begin Simulation Statistics/{n++} n==2' $D \
       | awk '/fetchStats0.icacheStallCycles/{print $2}')
  printf "%-14s" "$v"
  $R results/lab5_$v.csv insts cycles ipc l1d_mshr_misses rob_full_events \
     iq_full_events lq_full_events squash_ratio l1d_mlp | tail -1 \
    | awk -v s="$ST" '{printf " %s %s %s %s %s %s %s %s %s icst=%s\n",$2,$3,$4,$5,$6,$7,$8,$9,$10,s}'
done
echo "===== LAT ====="
for v in qnn_dotp8 qnn_dotp8x2 qnn_dotp8x4c; do
  echo "--- $v ---"
  $R results/lab5_lat_$v.csv cycles ipc
done
echo DONE5
