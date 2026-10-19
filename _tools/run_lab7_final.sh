#!/bin/bash
# 实验七 参考数据 C5：把"免费的刀"叠到帕累托前沿上，重新找 600 A 预算内的最优
#
# C4 发现了两把此前没试过的刀，都在核心内部：
#   BTB 4096 → 1024   周期数一个不差（76102 = 76102），面积 −30.7 A
#   LQ/SQ 32 → 16     反而快了 30 个周期，面积 −11.7 A
# 两把一起（K_allcut，还顺手把 BTB 砍到 512）：519.2 A / 76072 周期，
# **在两个轴上同时**打败了原来的候选 Z_w4pe48（566.7 A / 76102）。
#
# 于是 600 A 预算下多出来 ~80 A 的余量。问题变成：这 80 A 拿去加宽核心划算吗？
# pe48 下已知的前沿：w3 548.8/78068  w4 566.7/76102  w5 587.9/75286
#                    w6 612.1/74615  w8 669.7/74064
# 把 −47.5 A 的刀叠上去，w6 大概会落到 565 A —— 如果真是这样，
# **预算内的最优就不是 w4 而是 w6**，答案得改。必须实测。
cd /mnt/smartssd/wlx/cssys || exit 1

G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/final
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"
S0='8 0x01352505'

run () { local tag=$1; shift; local bin=$1; shift; local sd=$1; shift
  echo "--- $tag"
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
     --options "$sd" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1 || echo "   FAIL $tag"
}

# ---- 叠了刀之后的宽度前沿（pe 48）----
for w in 2 3 4 5 6 8; do
  if [ "$w" = 8 ]; then WFLAG=""; else WFLAG="--width $w"; fi
  run G_pe48_w$w qnn_accel_b2 "$S0" --accel l2bus --accel-pe 48 $FREE $CUT $WFLAG
done

# ---- 算力那一边：省下的面积拿去买 pe 划算吗 ----
run G_pe64_w4 qnn_accel_b2 "$S0" --accel l2bus --accel-pe 64 $FREE $CUT --width 4
run G_pe64_w6 qnn_accel_b2 "$S0" --accel l2bus --accel-pe 64 $FREE $CUT --width 6
run G_pe32_w6 qnn_accel_b2 "$S0" --accel l2bus --accel-pe 32 $FREE $CUT --width 6

# ---- 纯软件线也叠一遍：qnn 的分支多得多，这两把刀对它还免费吗 ----
run G_soft_cut  qnn "$S0" $FREE $CUT
run G_soft_base qnn "$S0" $FREE

echo
echo "=== 称重 ==="
python3 framework/area.py $OUT/G_* --csv
echo FINALDONE
