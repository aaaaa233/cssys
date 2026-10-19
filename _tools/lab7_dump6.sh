#!/bin/bash
# ★ dump5 翻出一个大问题：pe 48->64 在 batch=2 上收益**逐位为零**，
#   在 batch=4 上却值 5.1%（74256 -> 70438），而且 580.6 A 还在预算内。
#   这正是实验六 Roofline 那张图的兑现：batch 提高算术强度 -> 工作点从访存受限
#   移到算力受限 -> 这时候加算力才开始有用。
#   所以 (width, pe, batch) 这个二维面必须重扫，之前定的最优解不作数。
#
# 预算算术（FREE+CUT 底盘）： A = 250.2 + core(w) + pe
#   core: w2 188.7 / w3 203.1 / w4 220.9 / w5 242.1 / w6 266.4 / w8 323.9
#   600 A 以内的 pe 上限： w4<=128  w5<=107  w6<=83  w8<=25
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump6
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"

r () { local tag=$1 bin=$2 sd=$3 w=$4 pe=$5
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "8 $sd" --cpu o3 \
     --accel l2bus --accel-pe $pe $FREE $CUT --width $w \
     > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
S=0x01352505

echo "########## (n) (width, pe) 二维面，batch=4，全部 <=600 A ##########"
for pe in 48 64 80 96 112 128; do r N_b4_w4_$pe qnn_accel_b4 $S 4 $pe; done
for pe in 48 64 80 96 107;     do r N_b4_w5_$pe qnn_accel_b4 $S 5 $pe; done
for pe in 48 56 64 72 83;      do r N_b4_w6_$pe qnn_accel_b4 $S 6 $pe; done
python3 framework/area.py $OUT/N_b4_* --csv

echo
echo "########## (o) 同一个面，batch=2 和 batch=8 ##########"
for pe in 48 64 96 128; do r O_b2_w4_$pe qnn_accel_b2 $S 4 $pe; done
for pe in 48 64 83;     do r O_b2_w6_$pe qnn_accel_b2 $S 6 $pe; done
for pe in 48 64 96 128; do r O_b8_w4_$pe qnn_accel_b8 $S 4 $pe; done
for pe in 48 64 83;     do r O_b8_w6_$pe qnn_accel_b8 $S 6 $pe; done
python3 framework/area.py $OUT/O_b2_* $OUT/O_b8_* --csv

echo
echo "########## (p) 算力饱和点：pe 一直加上去（不管预算），看屋顶在哪 ##########"
for pe in 32 48 64 96 128 192 256; do r P_b4_$pe qnn_accel_b4 $S 6 $pe; done
python3 framework/area.py $OUT/P_b4_* --csv
echo "--- 加速器自己的统计（stall_frac 是判断卡在哪个屋顶的唯一抓手）---"
for pe in 32 48 64 96 128 192 256; do
  printf 'pe=%-4s ' $pe
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/P_b4_$pe/stats.txt | grep -E \
    'system.accel.jobCycles|system.accel.busyCycles|system.accel.stallCycles|system.accel.macsPerCycle|system.accel.bytesPerCycle' \
    | awk '{printf "%s=%s  ", $1, $2}'; echo
done

echo
echo "########## (q) checksum ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP6DONE
