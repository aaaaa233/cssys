#!/bin/bash
# 把写参考解答需要的、还没记下来的数据一次性打出来。
# 不再跑新仿真的部分直接读旧目录；X1..X4 对照实验是新的，要跑。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump
mkdir -p $OUT/logs
S="8 0x01352505"

echo "########## 1) 基线 qnn 默认 o3 —— 面积/能量分项 ##########"
[ -d out/lab7/base ] || $G --outdir=out/lab7/base $C --cmd bench/bin/riscv/qnn \
    --options "$S" --cpu o3 > $OUT/logs/base.log 2>&1
python3 framework/area.py out/lab7/base --detail

echo
echo "########## 2) 实验六定稿配置 qnn_accel pe32 —— 面积分项 ##########"
[ -d out/lab7/l6 ] || $G --outdir=out/lab7/l6 $C --cmd bench/bin/riscv/qnn_accel \
    --options "$S" --cpu o3 --accel l2bus --accel-pe 32 > $OUT/logs/l6.log 2>&1
python3 framework/area.py out/lab7/l6 --detail

echo
echo "########## 3) 参考最优 G_pe48_w6 —— 面积/能量分项 ##########"
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"
[ -d $OUT/best ] || $G --outdir=$OUT/best $C --cmd bench/bin/riscv/qnn_accel_b2 \
    --options "$S" --cpu o3 --accel l2bus --accel-pe 48 $FREE $CUT --width 6 \
    > $OUT/logs/best.log 2>&1
python3 framework/area.py $OUT/best --detail

echo
echo "########## 4) 任务3 单旋钮扫描 27 点（旧数据，直接读） ##########"
for d in out/sweeps/lab7_*/p*/; do echo "$d"; done | head -1 > /dev/null
python3 framework/area.py out/sweeps/lab7_l1i/p*/ out/sweeps/lab7_l1d/p*/ \
        out/sweeps/lab7_l2/p*/ out/sweeps/lab7_width/p*/ out/sweeps/lab7_rob/p*/ \
        out/sweeps/lab7_iq/p*/ out/sweeps/lab7_iregs/p*/ --csv 2>/dev/null \
  || echo "  (单点扫描目录名对不上，下面单独列)"
echo "--- 实际存在的 sweep 目录 ---"
ls -d out/sweeps/*/ 2>/dev/null

echo
echo "########## 5) 任务5 对照实验 X1..X4 ##########"
x () { local tag=$1; shift; local bin=$1; shift
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "$S" --cpu o3 \
     $FREE "$@" > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
x X1 qnn
x X2 qnn --width 4
x X3 qnn_accel_b2 --accel l2bus --accel-pe 32
x X4 qnn_accel_b2 --accel l2bus --accel-pe 32 --width 4
python3 framework/area.py $OUT/X1 $OUT/X2 $OUT/X3 $OUT/X4 --csv

echo
echo "########## 6) 任务2第5问：icache vs dcache 访问次数 ##########"
grep -E 'icache.overallAccesses::total|dcache.overallAccesses::total' \
     out/lab7/base/stats.txt | tail -4

echo
echo "########## 7) 免费旋钮逐个叠加（任务3第2问的标准答案） ##########"
f () { local tag=$1; shift
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/qnn --options "$S" --cpu o3 \
     "$@" > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
f S0
f S1 --l2-size 128kB
f S2 --l2-size 128kB --l1i-size 2kB
f S3 --l2-size 128kB --l1i-size 2kB --l1d-size 8kB
f S4 --l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128
f S5 --l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160
python3 framework/area.py $OUT/S0 $OUT/S1 $OUT/S2 $OUT/S3 $OUT/S4 $OUT/S5 --csv

echo
echo "########## 8) 模型系数（参考解答附录 B 要抄） ##########"
python3 framework/area.py --model
echo DUMPDONE
