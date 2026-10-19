#!/bin/bash
# 抓一个"卡住"的种子的现场：把加速器的 DPRINTF 打开，看它停在哪一步。
# 已知 0x00003333 和 0x00005555 在默认加速器配置下就会卡住。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/hangdbg
mkdir -p $OUT

for sd in 0x00003333 0x01352505; do
  echo "########## seed $sd ##########"
  timeout 60 $G --outdir=$OUT/d$sd --debug-flags=Dotp8Accel \
      $C --cmd bench/bin/riscv/qnn_accel_b2 --options "8 $sd" \
      --cpu o3 --accel l2bus --accel-pe 32 > $OUT/d$sd.log 2>&1
  echo "rc=$?  行数=$(wc -l < $OUT/d$sd.log)"
  echo "--- 前 12 行 GO/done ---"
  grep -E 'GO:|done:' $OUT/d$sd.log | head -12
  echo "--- 最后 5 行 ---"
  tail -5 $OUT/d$sd.log
  echo
done

echo "########## 卡住那次的加速器统计 ##########"
grep -E 'accel\.(jobs|macs|bytesRead|lineReads|busyCycles|stallCycles)' \
     $OUT/d0x00003333/stats.txt 2>/dev/null | head -20
echo HANGDBGDONE
