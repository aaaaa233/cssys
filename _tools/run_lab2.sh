#!/bin/bash
# 教师侧参考数据生成：第 2 次实验的四组扫描
cd /mnt/smartssd/wlx/cssys || exit 1
sleep 45

python3 framework/sweep.py --name lab2_assoc \
  --bench qnn --bench-args 8 --base "--cpu o3" \
  --vary l1d-size=32kB,64kB,128kB --vary l1d-assoc=1,2,4,8 --jobs 12

python3 framework/sweep.py --name lab2_line \
  --bench qnn --bench-args 8 --base "--cpu o3 --l1d-size 32kB" \
  --vary cacheline=16,32,64,128,256 --jobs 5

python3 framework/sweep.py --name lab2_l2 \
  --bench qnn --bench-args 8 --base "--cpu o3 --l1d-size 32kB" \
  --vary l2-size=128kB,256kB,512kB,1MB,2MB --jobs 5

python3 framework/sweep.py --name lab2_mshr \
  --bench qnn --bench-args 8 --base "--cpu o3 --l1d-size 32kB" \
  --vary l1d-mshrs=1,2,4,8,16 --jobs 5

echo LAB2DONE
