#!/bin/bash
# 教师侧参考数据生成：第 1、2 次实验全部扫描（stats.py 更新后重跑）
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"

$S --name lab1_cpu_models --bench qnn --bench-args 8 \
   --vary cpu=atomic,timing,minor,o3 --jobs 4

$S --name lab1_fidelity --bench qnn --bench-args 8 \
   --vary cpu=timing,minor,o3 --vary l1d-size=16kB,128kB --jobs 6

$S --name lab2_l1d_size --bench qnn --bench-args 8 --base "--cpu o3" \
   --vary l1d-size=8kB,16kB,32kB,64kB,128kB,256kB --jobs 6

$S --name lab2_assoc --bench qnn --bench-args 8 --base "--cpu o3" \
   --vary l1d-size=32kB,64kB,128kB --vary l1d-assoc=1,2,4,8 --jobs 12

$S --name lab2_line --bench qnn --bench-args 8 --base "--cpu o3 --l1d-size 32kB" \
   --vary cacheline=16,32,64,128,256 --jobs 5

$S --name lab2_l2 --bench qnn --bench-args 8 --base "--cpu o3 --l1d-size 32kB" \
   --vary l2-size=128kB,256kB,512kB,1MB,2MB --jobs 5

$S --name lab2_mshr --bench qnn --bench-args 8 --base "--cpu o3 --l1d-size 32kB" \
   --vary l1d-mshrs=1,2,4,8,16 --jobs 5

echo ALLDONE
