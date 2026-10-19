#!/bin/bash
# 补跑：ROI 占比随负载规模的变化（任务 2 第 3 问的参考数据）
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
for n in 8 64; do
  $G --outdir=out/lab1/noroi_$n $C \
     --cmd bench/bin/riscv/qnn_noroi --options "$n" --cpu o3 > /dev/null 2>&1 &
  $G --outdir=out/lab1/roi_$n $C \
     --cmd bench/bin/riscv/qnn --options "$n" --cpu o3 > /dev/null 2>&1 &
done
wait
echo NOROIDONE
