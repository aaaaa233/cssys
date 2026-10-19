#!/bin/bash
# 实验七 参考数据 C4b：补跑 C4 里挂掉的那一条 + 把 BTB 往更小处扫
#
# C4 里 `--bp 2bit` 写错了 —— gem5 里两位饱和计数器那个预测器叫 `local`。
# 顺手把 BTB 往下扫到 128：基线核心里 BTB 一项就占 46.1 A，
# 如果 qnn 的分支足够规整，这可能是整张表上最便宜的一刀。
cd /mnt/smartssd/wlx/cssys || exit 1

G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/check
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
A="--accel l2bus"
S0='8 0x01352505'

run () { local tag=$1; shift; local bin=$1; shift; local sd=$1; shift
  echo "--- $tag"
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
     --options "$sd" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1 || echo "   FAIL $tag"
}

# ---- 便宜的分支预测器（C4 里写错了名字的那条）----
run K_bplocal  qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --bp local
run K_bpbimode qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --bp bimode
run K_bpnone   qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --bp none

# ---- BTB 继续往小扫 ----
run K_btb256   qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --btb-entries 256
run K_btb128   qnn_accel_b2 "$S0" $A --accel-pe 48 $FREE --width 4 --btb-entries 128

# ---- 纯软件线上同样问一遍（qnn 的分支比 qnn_accel_b2 多得多）----
run K_soft_btb128 qnn "$S0" $FREE --btb-entries 128
run K_soft_bploc  qnn "$S0" $FREE --bp local

echo
echo "=== 称重 ==="
python3 framework/area.py $OUT/K_bp* $OUT/K_btb* $OUT/K_soft* --csv
echo CHECK2DONE
