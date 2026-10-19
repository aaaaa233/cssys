#!/bin/bash
# 验证：热循环的代码对齐是不是 4.5x 差异的原因
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
CC=riscv64-linux-gnu-gcc
F="-O2 -Wall -Ibench/include -static"
A="-falign-functions=64 -falign-loops=64 -falign-jumps=64 -falign-labels=64"

mkdir -p out/align bench/bin/align
$CC $F            -o bench/bin/align/a_roi   bench/src/qnn.c
$CC $F -DNO_M5OPS -o bench/bin/align/a_noroi bench/src/qnn.c
$CC $F $A            -o bench/bin/align/b_roi   bench/src/qnn.c
$CC $F $A -DNO_M5OPS -o bench/bin/align/b_noroi bench/src/qnn.c

for v in a_roi a_noroi b_roi b_noroi; do
  $G --outdir=out/align/$v $C --cmd bench/bin/align/$v \
     --options 8 --cpu o3 > out/align_$v.log 2>&1 &
done
wait

echo "变体            dot_i8地址   %64   最终tick"
for v in a_roi a_noroi b_roi b_noroi; do
  addr=$(riscv64-linux-gnu-nm bench/bin/align/$v | awk '$3=="dot_i8"{print $1}')
  off=$(( 0x${addr} % 64 ))
  tick=$(grep -o 'tick [0-9]*' out/align_$v.log | tail -1 | awk '{print $2}')
  printf "%-14s %s %5d %14s\n" "$v" "$addr" "$off" "$tick"
done

echo
echo "取指相关统计（无对齐 vs 有对齐）:"
for v in a_roi a_noroi b_roi b_noroi; do
  echo "-- $v"
  grep -E '^system.cpu.fetchStats0.(numCycles|numFetchedInsts|numInsts)|^system.cpu.fetch.(icacheStallCycles|cacheLines)|^system.cpu.numCycles ' \
      out/align/$v/stats.txt | head -8
done
echo DIAG3DONE
