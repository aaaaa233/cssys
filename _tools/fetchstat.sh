#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
for d in p000_cacheline-16_l1d-mshrs-4 p003_cacheline-32_l1d-mshrs-4 p006_cacheline-64_l1d-mshrs-4; do
  f=out/sweeps/lab2_line_mshr/$d/stats.txt
  echo "== $d"
  awk '/Begin Simulation Statistics/{n++} n==2' "$f" \
    | grep -E 'fetch\.cacheLines|numFetchedInsts|icacheStallCycles|fetch\.rate|blockedCycles|cpu\.numCycles ' \
    | head -10
done
echo FETCHSTATDONE
