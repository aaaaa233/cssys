#!/bin/bash
# 收尾取数：参考解答要用的三样东西
#  (r) 最优解 w6/pe83/b4 的面积与能量分项（--detail），这是 4c 的标准答案
#  (s) batch=2 的 Roofline 右半边（对照 dump6 的 batch=4），
#      用来把"拐点随算术强度平移"这件事**两条曲线并排**摆出来
#  (t) 最优解自己的加速器统计：证明 pe=83 已经贴着屋顶
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump7
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"
S=0x01352505
r () { local tag=$1 bin=$2 w=$3 pe=$4
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "8 $S" --cpu o3 \
     --accel l2bus --accel-pe $pe $FREE $CUT --width $w \
     > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}

echo "########## (r) 最优解 b4/w6/pe83 的分项 ##########"
r R_best qnn_accel_b4 6 83
python3 framework/area.py $OUT/R_best --detail

echo
echo "########## (s) batch=2 的 Roofline 右半边 ##########"
for pe in 24 32 40 48 64 96 128; do r S_b2_$pe qnn_accel_b2 6 $pe; done
python3 framework/area.py $OUT/S_b2_* --csv
echo "--- b2 加速器统计 ---"
for pe in 24 32 40 48 64 96 128; do
  printf 'b2 pe=%-4s ' $pe
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/S_b2_$pe/stats.txt | grep -E \
    'system.accel.jobCycles|system.accel.busyCycles|system.accel.stallCycles|system.accel.macsPerCycle|system.accel.bytesPerCycle|system.accel.macs ' \
    | awk '{printf "%s=%s  ", $1, $2}'; echo
done

echo
echo "########## (t) 最优解的加速器统计 ##########"
for d in R_best; do
  printf '%-8s ' $d
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/$d/stats.txt | grep -E \
    'system.accel.jobs |system.accel.macs |system.accel.jobCycles|system.accel.busyCycles|system.accel.stallCycles|system.accel.macsPerCycle|system.accel.bytesPerCycle|system.accel.bytesRead' \
    | awk '{printf "%s=%s  ", $1, $2}'; echo
done
echo "--- 同一底盘 pe=48 的对照（b4）---"
awk '/^-+ Begin Simulation Statistics/{n++} n==2' out/lab7/dump6/N_b4_w6_48/stats.txt | grep -E \
  'system.accel.jobs |system.accel.macs |system.accel.jobCycles|system.accel.busyCycles|system.accel.stallCycles|system.accel.macsPerCycle|system.accel.bytesPerCycle|system.accel.bytesRead' \
  | awk '{printf "%s=%s  ", $1, $2}'; echo
echo "--- CPU 侧：最优解里 CPU 和加速器各占多少 ---"
for d in $OUT/R_best out/lab7/dump6/N_b4_w6_48; do
  printf '%-32s ' $d
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $d/stats.txt | grep -E \
    'system.cpu.numCycles |system.cpu.ipc |system.cpu.commit.committedInsts ' \
    | awk '{printf "%s=%s  ", $1, $2}'; echo
done

echo
echo "########## (u) checksum ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP7DONE
