#!/bin/bash
# 实验七 参考数据 C2：组合验证
#
# 单点扫描给出的"每个旋钮省多少面积、赚多少性能"是在**别的旋钮都不动**
# 的前提下测的。这个脚本把那些"看起来免费"的动作叠起来，检验它们可不可加。
#
# 两条线：
#   c* —— 纯软件 qnn，逐个叠加单点扫描里"免费或更好"的动作
#   a* —— qnn_accel + 加速器，叠加同样的动作
# 关键悬念：实验六 6c 已经证明加速器取的 820 KB 来自 L1D/L2 里的**脏行**。
#           那么"把 L1D 砍到 8kB"这个对 qnn 免费的动作，对 qnn_accel 呢？
cd /mnt/smartssd/wlx/cssys || exit 1

G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
SEED='8 0x01352505'
OUT=out/lab7/combo
mkdir -p $OUT/logs

run () {            # run <标签> <二进制> <额外参数...>
  local tag=$1; shift
  local bin=$1; shift
  echo "--- $tag"
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
     --options "$SEED" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1 \
     || echo "   FAIL $tag"
}

# ============ 纯软件线：逐步叠加"免费"动作 ============
run c0_base      qnn
run c1_l2        qnn  --l2-size 128kB
run c2_l2i       qnn  --l2-size 128kB --l1i-size 2kB
run c3_l2id      qnn  --l2-size 128kB --l1i-size 2kB --l1d-size 8kB
run c4_l2id_rob  qnn  --l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128
run c5_all       qnn  --l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160
# 对照：只叠 L1D，不动 L2（看 L1D 那 4.5% 是不是真的来自 L1D 自己）
run c6_d_only    qnn  --l1d-size 8kB

# ============ 加速器线：同样的动作，换个程序 ============
run a0_base      qnn_accel --accel l2bus --accel-pe 32
run a1_l2        qnn_accel --accel l2bus --accel-pe 32 --l2-size 128kB
run a2_l2i       qnn_accel --accel l2bus --accel-pe 32 --l2-size 128kB --l1i-size 2kB
run a3_l2id      qnn_accel --accel l2bus --accel-pe 32 --l2-size 128kB --l1i-size 2kB --l1d-size 8kB
run a4_l2id_rob  qnn_accel --accel l2bus --accel-pe 32 --l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128
run a5_all       qnn_accel --accel l2bus --accel-pe 32 --l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160
# 对照：加速器系统里只砍 L1D
run a6_d_only    qnn_accel --accel l2bus --accel-pe 32 --l1d-size 8kB
# 对照：把核也做窄（T_CPU 占了 60%，窄核会不会更划算？）
run a7_w4        qnn_accel --accel l2bus --accel-pe 32 --l2-size 128kB --l1i-size 2kB --width 4

echo
echo "=== 称重 ==="
python3 framework/area.py $OUT/c*/ $OUT/a*/ --csv
echo COMBODONE
