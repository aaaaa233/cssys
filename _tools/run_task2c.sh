#!/bin/bash
# 完全照抄指导书任务 2(c) 的步骤，产出教师参考解答要用的那张表
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
B="qnn qnn_noroi qnn_noalign qnn_noalign_noroi"

for b in $B; do
  $G --outdir=out/t2c/$b $C --cmd bench/bin/riscv/$b --options 8 --cpu o3 \
     > out/t2c_$b.log 2>&1 &
done
wait

echo "二进制                  dot_i8地址  mod64   全程序指令    全程序周期   段数"
for b in $B; do
  a=$(riscv64-linux-gnu-nm bench/bin/riscv/$b | awk '$3=="dot_i8"{print $1}')
  f=out/t2c/$b/stats.txt
  ni=$(grep -c 'Begin Simulation Statistics' "$f")
  ins=$(grep -E '^simInsts ' "$f" | awk '{s+=$2} END{print s}')
  cyc=$(grep -E '^system.cpu.numCycles ' "$f" | awk '{s+=$2} END{print s}')
  printf "%-22s %-10s %5d %13s %13s %5s\n" "$b" "$a" $((0x$a % 64)) "$ins" "$cyc" "$ni"
done

echo
echo "各段周期数明细:"
for b in $B; do
  echo -n "$b: "
  grep -E '^system.cpu.numCycles ' out/t2c/$b/stats.txt | awk '{printf "%s ", $2} END{print ""}'
done
echo T2CDONE
