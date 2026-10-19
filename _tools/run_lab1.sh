#!/bin/bash
# 教师侧参考数据生成：第 1 次实验的 ROI 对比与工作负载规模扫描
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py

for n in 2 4 8 16 32 64; do
  $G --outdir=out/lab1/scale_$n $C \
     --cmd bench/bin/riscv/qnn --options "$n" --cpu o3 > out/lab1_scale_$n.log 2>&1 &
done
$G --outdir=out/lab1/noroi $C \
   --cmd bench/bin/riscv/qnn_noroi --options 8 --cpu o3 > out/lab1_noroi.log 2>&1 &
$G --outdir=out/lab1/roi $C \
   --cmd bench/bin/riscv/qnn --options 8 --cpu o3 > out/lab1_roi.log 2>&1 &
wait
echo SCALEDONE
