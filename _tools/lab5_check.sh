#!/bin/bash
# 正确性底线：五个版本必须打印完全相同的 checksum 和直方图。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
for v in qnn qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4; do
  echo "==== $v"
  $G --outdir=out/chk_$v framework/cssys_se.py \
     --cmd bench/bin/riscv/$v --options "8" --cpu atomic 2>&1 \
     | grep -E 'qnn samples|class histogram|panic|fatal|Unknown|error'
done
