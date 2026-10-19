#!/bin/bash
# 把一次运行的 ROI 统计块里和实验六有关的项挑出来（第 2 个统计块 = ROI）
for d in "$@"; do
  echo "===== $d ====="
  awk '/Begin Simulation Statistics/{n++} n==2' $d/stats.txt \
  | grep -E '^(simTicks|system.cpu.numCycles|system.cpu.committedInsts|system.accel.(jobs|macs|bytesRead|lineReads|jobCycles|busyCycles|stallCycles|bytesPerCycle|macsPerCycle|macsPerByte)|system.l2cache.overallHits::total|system.l2cache.overallMisses::total|system.l2cache.demandHits::total|system.l2cache.demandMisses::total|system.mem_ctrl.dram.bwTotal::total)' \
  | awk '{printf "%-46s %s\n", $1, $2}'
done
