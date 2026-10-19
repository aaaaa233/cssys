#!/bin/bash
# dump2 挖出三件事，都要钉死了才能写进参考解答：
#  (a) qnn_accel_b4 在 pe48/w6 上比 b2 快 0.57%，面积逐位相同 —— 它才是最优解？
#      margin 只有 0.57%，必须四个种子都验一遍（同种子内配对比较）。
#  (b) 指导书说"只调核和 Cache 最多 5 倍"—— 实测纯软件只有 1.08 倍，
#      5.4 倍是实验五那条路。要测出实验五路线在 600 A 内的真实最好成绩。
#  (c) ★ width 陷阱的机理：w4→w6 只快 0.45%，w6→w8 却快 35%。
#      猜测是"取指组被 taken 分支截断"——循环体约 8 条指令，
#      w8 一拍取完一圈，w6 要两拍(6+2)，w4 也要两拍(4+4)，所以 w6≈w4。
#      要用 fetch 的统计量证实。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump3
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"

r () { local tag=$1; shift; local bin=$1; shift; local sd=$1; shift
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "8 $sd" --cpu o3 \
     "$@" > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}

echo "########## (a) b1/b2/b4/b8 × 四个种子（pe48 w6 CUT） ##########"
for sd in 0x01352505 0x00001234 0x0000abcd 0x00003333; do
  t=${sd: -4}
  for b in "" _b2 _b4 _b8; do
    r A_${t}${b:-_b1} qnn_accel$b "$sd" --accel l2bus --accel-pe 48 $FREE $CUT --width 6
  done
done
python3 framework/area.py $OUT/A_* --csv

echo
echo "########## (b) 三条路线在 600 A 预算内各自的最好成绩 ##########"
S=0x01352505
# 路线一：完全不换二进制
r P1_a qnn        $S $FREE
r P1_b qnn        $S $FREE --btb-entries 512
r P1_c qnn        $S --l2-size 128kB --l1i-size 2kB --l1d-size 8kB
# 路线二：实验五的自定义指令
r P2_a qnn_dotp8x4c $S $FREE --dotp8-lat 3
r P2_b qnn_dotp8x4c $S $FREE --dotp8-lat 3 --btb-entries 512
r P2_c qnn_dotp8x4c $S $FREE --dotp8-lat 2 --btb-entries 512 --lq 16 --sq 16
r P2_d qnn_dotp8x4c $S $FREE --dotp8-lat 1 --btb-entries 512 --lq 16 --sq 16
# 路线三：实验六的加速器（对照）
r P3_a qnn_accel_b4 $S --accel l2bus --accel-pe 48 $FREE $CUT --width 6
python3 framework/area.py $OUT/P1_a $OUT/P1_b $OUT/P1_c $OUT/P2_a $OUT/P2_b \
                          $OUT/P2_c $OUT/P2_d $OUT/P3_a --csv

echo
echo "########## (c) width 陷阱的机理：取指统计 ##########"
for w in 2 4 6 8; do
  r C_w$w qnn $S --width $w
done
for w in 2 4 6 8; do
  f=$OUT/C_w$w/stats.txt
  echo "===== width $w ====="
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $f | grep -E \
    'system.cpu.numCycles|fetch.instsPerCycle::mean|fetch.cycles|fetch.insts |fetch.branches|fetch.predictedBranches|fetch.squashCycles|fetch.blockedCycles|fetch.miscStallCycles|fetch.tycles|decode.blockedCycles|rename.blockCycles|iew.dispatchedInsts|iew.iqFullEvents|iew.lsqFullEvents|commit.commitSquashedInsts|commit.instsPerCycle|rob.reads' \
    | head -25
done

echo
echo "########## (c2) 取指组分布（rateDist），看有没有卡在 6 ##########"
for w in 6 8; do
  echo "===== width $w  fetch.rateDist ====="
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/C_w$w/stats.txt \
    | grep -E 'fetch.rateDist::[0-9]+ ' | head -12
done

echo
echo "########## (d) checksum 自检 ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP3DONE
