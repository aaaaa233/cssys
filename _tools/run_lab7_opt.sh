#!/bin/bash
# 实验七 参考数据 C3：找真正的最优解
#
# C2 已经证明：把五个"免费"动作叠起来，面积 836.0 → 589.7 A，还更快。
# 现在在这个新底盘上找最优。三条线索：
#   B —— batch 是纯软件变体（换个二进制），面积开销为 0。实验六 M4 说 b2 最快。
#   W —— 有了加速器，CPU 只剩 8.5 万条指令。8 发射的核还有必要吗？
#   P —— 加速器算力 pe 在新底盘上的最优点还是 32 吗？
# 另外把实验五那条路（自定义指令）也放进同一张表，让三条技术路线可比。
cd /mnt/smartssd/wlx/cssys || exit 1

G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
SEED='8 0x01352505'
OUT=out/lab7/opt
mkdir -p $OUT/logs

# 五个"免费"动作，C2 验证过可以叠加
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"

run () { local tag=$1; shift; local bin=$1; shift
  echo "--- $tag"
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
     --options "$SEED" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1 || echo "   FAIL $tag"
}

A="--accel l2bus --accel-pe 32"

# ---- B 线：batch（换二进制，0 面积）----
run B1_b1  qnn_accel    $A $FREE
run B2_b2  qnn_accel_b2 $A $FREE
run B4_b4  qnn_accel_b4 $A $FREE
run B8_b8  qnn_accel_b8 $A $FREE

# ---- W 线：有了加速器，核还要多宽？（用 B 线的赢家 b2）----
run W2_w2  qnn_accel_b2 $A $FREE --width 2
run W4_w4  qnn_accel_b2 $A $FREE --width 4
run W6_w6  qnn_accel_b2 $A $FREE --width 6
# 对照：没有加速器时把核做窄，代价是多少
run W4_soft qnn         $FREE --width 4

# ---- P 线：新底盘上的算力最优点 ----
run P16 qnn_accel_b2 --accel l2bus --accel-pe 16 $FREE
run P48 qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE
run P64 qnn_accel_b2 --accel l2bus --accel-pe 64 $FREE
# 挂载点：新底盘（L2 只有 128kB）上还是 l2bus 赢吗？
run M_mem qnn_accel_b2 --accel membus --accel-pe 32 $FREE

# ---- D 线：实验五那条路，放进同一张表 ----
run D_lat1 qnn_dotp8x4c $FREE
run D_lat3 qnn_dotp8x4c $FREE --dotp8-lat 3
run D_soft qnn          $FREE

# ---- 候选终局：把 W 线赢家和 B 线赢家合起来再微调 ----
run Z_w4pe48 qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE --width 4
run Z_w4d16  qnn_accel_b2 $A $FREE --width 4 --l1d-size 16kB
run Z_w4l2   qnn_accel_b2 $A --l2-size 256kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160 --width 4

echo
echo "=== 称重 ==="
python3 framework/area.py $OUT/B* $OUT/W* $OUT/P* $OUT/M* $OUT/D* $OUT/Z* --csv
echo OPTDONE
