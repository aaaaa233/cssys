#!/bin/bash
# 拆解"小块崩塌"：到底是 MSHR 不够，还是取指缓冲被块大小限死？
cd /mnt/smartssd/wlx/cssys || exit 1
python3 framework/sweep.py --name lab2_line_mshr --bench qnn --bench-args 8 \
   --base "--cpu o3" \
   --vary cacheline=16,32,64 --vary l1d-mshrs=4,16,64 \
   --jobs 9 2>&1 | tail -14
echo LINEMSHRDONE
