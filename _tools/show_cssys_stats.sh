#!/bin/bash
# 把 CssysRP 在 L1 和 L2 上的统计量原样打出来，做参考解答用
cd /mnt/smartssd/wlx/cssys || exit 1
echo '=== L1D (cssys, 64kB/4way, ROI=第二段) ==='
awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab3_mine/p001_l1d-repl-cssys/stats.txt \
  | grep -E 'dcache.replacement_policy'
echo '=== L1D 原始计数器 ==='
awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab3_mine/p001_l1d-repl-cssys/stats.txt \
  | grep -E 'dcache.(overallHits|overallMisses|overallMshrMisses|overallAccesses)::total'
echo '=== 总周期 ==='
awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab3_mine/p001_l1d-repl-cssys/stats.txt \
  | grep -E '^(simTicks|system.cpu.numCycles) '
echo L1DONE
echo '=== L2 (cssys, 64kB/4way) ==='
awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab3_mine_l2/p000_l2-repl-cssys/stats.txt \
  | grep -E 'l2cache.replacement_policy'
echo '=== L2 原始计数器 ==='
awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab3_mine_l2/p000_l2-repl-cssys/stats.txt \
  | grep -E 'l2cache.(overallHits|overallMisses|overallMshrMisses|overallAccesses)::total'
awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab3_mine_l2/p000_l2-repl-cssys/stats.txt \
  | grep -E '^(simTicks|system.cpu.numCycles) '
echo L2DONE
