#!/bin/bash
# 实验六 探索性扫描 1：挂载点 x 算力
# 目的：找到"挂哪儿"这个决定开始产生可测差异的 pe 值
cd /mnt/smartssd/wlx/cssys || exit 1
python3 framework/sweep.py --name lab6_where_pe \
    --bench qnn_accel --bench-args "8 0x01352505" \
    --base "--cpu o3" \
    --vary accel=l2bus,membus \
    --vary accel-pe=8,16,32,64 \
    --jobs 8 --timeout 3600
echo SWEEP1DONE
