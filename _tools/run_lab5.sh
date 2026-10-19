#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"
G=gem5/build/RISCV/gem5.opt
V="qnn qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c"

# ---- 主表：课程标准 o3 基线（和实验一~四完全同一条命令行），延迟按 3 拍算 ----
for v in $V; do
  $S --name lab5_$v --bench $v --bench-args 8 \
     --base "--cpu o3 --dotp8-lat 3" --jobs 1 > /dev/null 2>&1
done
echo "版本            指令数      周期数     IPC    l1d_mshr  取指块停顿"
for v in $V; do
  D=out/sweeps/lab5_$v/p000/stats.txt
  ST=$(awk '/Begin Simulation Statistics/{n++} n==2' $D \
       | awk '/fetchStats0.icacheStallCycles/{print $2}')
  printf "%-14s" "$v"
  $R results/lab5_$v.csv insts cycles ipc l1d_mshr_misses | tail -1 \
    | awk -v s="$ST" '{printf "%12s %11s %8s %10s %10s\n", $2, $3, $4, $5, s}'
done
echo MAINDONE
