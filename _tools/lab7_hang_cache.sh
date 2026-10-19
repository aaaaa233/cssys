#!/bin/bash
# 死锁现场：CPU 卡在 STATUS 这条 uncacheable load 上，加速器卡在等 hbat 的取数上。
# 猜测是 L1D 被那条没人回复的 uncacheable 访问占住，导致它没法回应加速器的 snoop
# —— 循环等待。用 Cache 的 debug 输出验证。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/hangdbg
mkdir -p $OUT

echo "########## 坏种子 0x3333：第二条 GO 前后的 Cache 行为 ##########"
timeout 150 $G --outdir=$OUT/c3333 \
    --debug-flags=Cache,Dotp8Accel --debug-start=389700000 \
    $C --cmd bench/bin/riscv/qnn_accel_b2 --options "8 0x00003333" \
    --cpu o3 --accel l2bus --accel-pe 32 > $OUT/c3333.log 2>&1
echo "rc=$? 行数=$(wc -l < $OUT/c3333.log)"
echo
echo "--- 最后 60 行 ---"
tail -60 $OUT/c3333.log
echo
echo "--- 出现过的 dcache 事件类型统计（尾部 20000 行）---"
tail -20000 $OUT/c3333.log | grep -o 'system\.cpu\.dcache: [A-Za-z ]*' | sort | uniq -c | sort -rn | head -20
echo CACHEDBGDONE
