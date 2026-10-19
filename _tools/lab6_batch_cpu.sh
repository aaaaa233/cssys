#!/bin/bash
# 任务 5 第 6 问：batch 越大 cycles 反而回升，回升的是 CPU 那一半还是加速器那一半？
# 把 ROI 统计块里 CPU 侧的几个数拉出来，看是"指令变多"还是"IPC 变低"。
cd /mnt/smartssd/wlx/cssys || exit 1
S=out/sweeps/lab6_m4_batch
echo "point                     insts     cycles   jobCyc    T_cpu   l1d_acc   l1d_miss  l1d_mpki  l2_acc   l2_miss"
for d in "$S"/*/; do
  f="$d/stats.txt"
  [ -f "$f" ] || continue
  # ROI = 第二个统计块
  roi=$(awk '/Begin Simulation Statistics/{n++} n==2' "$f")
  g() { echo "$roi" | grep -E "^$1 " | head -1 | awk '{print $2}'; }
  ins=$(g 'system.cpu.commitStats0.numInsts')
  [ -z "$ins" ] && ins=$(g 'system.cpu.commit.committedInsts')
  cyc=$(g 'system.cpu.numCycles')
  job=$(g 'system.accel.jobCycles')
  la=$(g 'system.cpu.dcache.overallAccesses::total')
  lm=$(g 'system.cpu.dcache.overallMisses::total')
  l2a=$(g 'system.l2cache.overallAccesses::total')
  l2m=$(g 'system.l2cache.overallMisses::total')
  tcpu=$(( ${cyc:-0} - ${job:-0} ))
  mpki=$(echo "$lm $ins" | awk '{if($2>0) printf "%.2f", $1*1000/$2; else print "-"}')
  printf '%-22s %8s %10s %8s %8s %9s %10s %9s %8s %8s\n' \
     "$(basename $d)" "$ins" "$cyc" "$job" "$tcpu" "$la" "$lm" "$mpki" "$l2a" "$l2m"
  grep -m1 'options' "$d/run.log" 2>/dev/null | head -1
done
echo "--- 每个点的命令行 ---"
grep -h 'command line' "$S"/*/run.log 2>/dev/null | head -20
echo BATCHCPUDONE
