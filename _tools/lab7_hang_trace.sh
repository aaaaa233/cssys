#!/bin/bash
# 加速器第一条命令做完了(tick 387890000)，第二条 GO 再也没来。
# 所以卡的是 CPU 侧。把那之后的指令流打出来看它在干什么。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/hangdbg
mkdir -p $OUT

echo "########## 坏种子 0x3333：done 之后的指令流 ##########"
timeout 120 $G --outdir=$OUT/tr3333 --debug-flags=Exec --debug-start=387800000 \
    $C --cmd bench/bin/riscv/qnn_accel_b2 --options "8 0x00003333" \
    --cpu o3 --accel l2bus --accel-pe 32 > $OUT/tr3333.log 2>&1
echo "行数=$(wc -l < $OUT/tr3333.log)"
echo "--- 头 25 条 ---"
grep ': *system.cpu' $OUT/tr3333.log | head -25
echo "--- 尾 25 条 ---"
grep ': *system.cpu' $OUT/tr3333.log | tail -25
echo
echo "--- 尾部出现的不同 PC 有几个（看是不是死循环）---"
grep ': *system.cpu' $OUT/tr3333.log | tail -3000 \
  | sed -e 's/.*system.cpu *//' -e 's/ *:.*//' | sort | uniq -c | sort -rn | head -15
echo HANGTRACEDONE
