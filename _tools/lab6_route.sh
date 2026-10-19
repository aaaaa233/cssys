#!/bin/bash
# 看清楚"加速器的取数流量到底走了哪条路"
# XBar 的 pktCount_<源端口>_<目的端口> 会把每条通路上的包数分开记，
# 用它可以直接回答"这些请求最后落到谁身上"。
cd /mnt/smartssd/wlx/cssys || exit 1
SEL='^system\.(l2bus|membus)\.transDist::(ReadReq|ReadResp)|^system\.l2cache\.(overallHits|overallMisses|demandHits|demandMisses|overallMshrMisses)::total|^system\.mem_ctrl\.(readReqs|dram\.bytesRead::total)|^system\.accel\.(lineReads|bytesRead|jobCycles|stallCycles)'
for p in "$@"; do
  echo "===== $p ====="
  awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab6_where_pe/$p/stats.txt \
  | grep -E "$SEL" | awk '{printf "%-52s %s\n", $1, $2}'
  echo "  ---- 每条通路上的包数 (非零) ----"
  awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab6_where_pe/$p/stats.txt \
  | grep -E '^system\.(l2bus|membus)\.pktCount_' \
  | awk '$2+0 > 0 {printf "  %-72s %s\n", $1, $2}'
done
