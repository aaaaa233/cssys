#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
printf "%-22s %14s %16s %14s\n" 二进制 fetch.cacheLines icacheStallCycles 总周期
for b in qnn qnn_noroi qnn_noalign qnn_noalign_noroi; do
  f=out/t2c/$b/stats.txt
  cl=$(grep -E '^system.cpu.fetch.cacheLines ' "$f" | awk '{s+=$2} END{print s}')
  st=$(grep -E '^system.cpu.fetchStats0.icacheStallCycles ' "$f" | awk '{s+=$2} END{print s}')
  cy=$(grep -E '^system.cpu.numCycles ' "$f" | awk '{s+=$2} END{print s}')
  printf "%-22s %14s %16s %14s\n" "$b" "$cl" "$st" "$cy"
done
echo T2CFETCHDONE
