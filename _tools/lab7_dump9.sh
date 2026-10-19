#!/bin/bash
# 任务 1 的关键一击：实验六 Q6 里几乎所有人都写"把 pe 从 32 加到 64"。
# dump8 已经暗示这一笔钱是零收益（b1 在 pe=48/83/128 上周期数逐位相同），
# 但那是在实验七的 FREE 底盘上测的。这里在**实验六原样的底盘**（默认 Cache）
# 上重测一遍，好在参考解答里把这句话说死。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump9
mkdir -p $OUT/logs
S=0x01352505
r () { local tag=$1 pe=$2
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/qnn_accel --options "8 $S" --cpu o3 \
     --accel l2bus --accel-pe $pe > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
echo "########## (x) 实验六原底盘（默认 Cache/核）× pe ##########"
for pe in 8 16 24 32 48 64 128; do r L6_pe$pe $pe; done
python3 framework/area.py $OUT/L6_* --csv
echo "--- 加速器统计：屋顶在哪 ---"
printf '%-6s %10s %10s %10s %12s %12s %10s\n' pe cycles jobCycles 非加速器 macsPerCyc bytesPerCyc stall
for pe in 8 16 24 32 48 64 128; do
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/L6_pe$pe/stats.txt > /tmp/t.$$
  cyc=$(awk '/^system.cpu.numCycles /{print $2}' /tmp/t.$$)
  jc=$(awk  '/^system.accel.jobCycles/{print $2}' /tmp/t.$$)
  mpc=$(awk '/^system.accel.macsPerCycle/{print $2}' /tmp/t.$$)
  bpc=$(awk '/^system.accel.bytesPerCycle/{print $2}' /tmp/t.$$)
  st=$(awk  '/^system.accel.stallCycles/{print $2}' /tmp/t.$$)
  printf '%-6s %10s %10s %10s %12s %12s %10s\n' "$pe" "$cyc" "$jc" "$((cyc-jc))" "$mpc" "$bpc" "$st"
done
rm -f /tmp/t.$$
echo
echo "########## (y) checksum ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP9DONE
