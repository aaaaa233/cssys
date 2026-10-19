#!/bin/bash
# 实验六 参考数据全套采集
# 所有点都用同一个负载：8 个样本、seed 0x01352505、O3 核。
# 采完这几张表，指导书里的每一个数都有出处。
cd /mnt/smartssd/wlx/cssys || exit 1
set -x
OPT="8 0x01352505"

# --- M1 三条基线：纯软件 / 实验五自定义指令 / 实验六加速器 -------------------
# --dotp8-lat 3 是实验五的结论配置（8 路 int8 乘法 + 加法树，3 拍才诚实）。
# 不写这一句就是默认的 1 拍，等于白送一个不存在的硬件。
python3 framework/sweep.py --name lab6_m1_soft \
    --bench qnn --bench-args "$OPT" --base "--cpu o3 --dotp8-lat 3" \
    --vary bench=qnn,qnn_dotp8x4c --jobs 2

python3 framework/sweep.py --name lab6_m1_accel \
    --bench qnn_accel --bench-args "$OPT" --base "--cpu o3" \
    --vary accel=l2bus,membus --vary accel-pe=8,32 --jobs 4

# --- M3 outstanding：Little 定律 ------------------------------------------
# pe=64 让算力绝不成为瓶颈，这样测到的就是纯粹的带宽上限
python3 framework/sweep.py --name lab6_m3_outstanding \
    --bench qnn_accel --bench-args "$OPT" --base "--cpu o3 --accel-pe 64" \
    --vary accel=l2bus,membus \
    --vary accel-outstanding=1,2,4,8,16,32 --jobs 12

# --- M4 batch：把算术强度从 1 抬到 8 ---------------------------------------
python3 framework/sweep.py --name lab6_m4_batch \
    --bench qnn_accel --bench-args "$OPT" --base "--cpu o3 --accel-pe 32" \
    --vary bench=qnn_accel,qnn_accel_b2,qnn_accel_b4,qnn_accel_b8 \
    --vary accel=l2bus,membus --jobs 8

# --- M5 L2 容量：加速器取的数据到底在哪一级 --------------------------------
# 权重一共 98 KB。L2 装得下 / 装不下，加速器的带宽会换一个上限。
python3 framework/sweep.py --name lab6_m5_l2size \
    --bench qnn_accel --bench-args "$OPT" --base "--cpu o3 --accel-pe 32" \
    --vary accel=l2bus,membus \
    --vary l2-size=32kB,64kB,128kB,256kB,512kB --jobs 10

echo REFDONE
