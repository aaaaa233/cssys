#!/bin/bash
# 实验七 参考数据 C4：收尾检查
#  1) 还有没有更便宜的旋钮没试（BTB / LQ / SQ / 分支预测器）
#  2) 细化帕累托前沿（width 3/5、pe 40）
#  3) ★ 换种子重跑前四名——学生用的是自己的学号种子，
#     如果排名会随种子变，这道题就不能出。**这一条是本次实验能否成立的前提。**
cd /mnt/smartssd/wlx/cssys || exit 1

G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/check
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
A="--accel l2bus"

run () { local tag=$1; shift; local bin=$1; shift; local sd=$1; shift
  echo "--- $tag"
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
     --options "$sd" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1 || echo "   FAIL $tag"
}

S0='8 0x01352505'

# ---- 1) 还没试过的便宜旋钮，都加在 Z_w4pe48 上 ----
run K_btb512  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --btb-entries 512
run K_btb1024 qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --btb-entries 1024
run K_bp2bit  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --bp 2bit
run K_lqsq16  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --lq 16 --sq 16
run K_iq32    qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --iq 32
# 把上面划算的全叠上（先都叠，看结果再决定）
run K_allcut  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 \
                                    --btb-entries 512 --lq 16 --sq 16

# ---- 2) 帕累托前沿细化 ----
run F_w3pe48  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 3
run F_w5pe48  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 5
run F_w4pe40  qnn_accel_b2 "$S0" $A --accel-pe 40 $FREE --width 4
run F_w6pe48  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 6

# ---- 3) ★ 换种子验证排名稳不稳 ----
for sd in 0x00001234 0x0000abcd; do
  t=${sd: -4}
  run S_${t}_base  qnn          "8 $sd"
  run S_${t}_w4p48 qnn_accel_b2 "8 $sd" $A --accel-pe 48 $FREE --width 4
  run S_${t}_w6    qnn_accel_b2 "8 $sd" $A --accel-pe 32 $FREE --width 6
  run S_${t}_w2    qnn_accel_b2 "8 $sd" $A --accel-pe 32 $FREE --width 2
  run S_${t}_w8    qnn_accel_b2 "8 $sd" $A --accel-pe 32 $FREE
done

echo
echo "=== 称重 ==="
python3 framework/area.py $OUT/K_* $OUT/F_* $OUT/S_* --csv
echo CHECKDONE
