#!/bin/bash
# 隔离实验：0 个样本，ROI 为空，剩下的几乎全是启动+收尾
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
for b in qnn qnn_noroi; do
  for n in 0 8; do
    $G --outdir=out/diag/${b}_$n $C --cmd bench/bin/riscv/$b \
       --options "$n" --cpu o3 > out/diag_${b}_$n.log 2>&1 &
  done
done
wait
for b in qnn qnn_noroi; do
  for n in 0 8; do
    echo -n "$b n=$n  finaltick="
    grep -o 'tick [0-9]*' out/diag_${b}_$n.log | tail -1
  done
done
echo DIAGDONE
