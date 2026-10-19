#!/bin/bash
# 拿 area.py 给已有的各次实验运行称重，检查模型在各种配置上都能跑、数值也讲得通。
cd /mnt/smartssd/wlx/cssys || exit 1

echo "=== A) 实验一：四种 CPU 模型 ==="
python3 framework/area.py out/sweeps/lab1_cpu_models/p00* --csv

echo
echo "=== B) 实验四：发射宽度 ==="
python3 framework/area.py out/sweeps/lab4_width/p00* --csv

echo
echo "=== C) 实验四：ROB / IQ / 物理寄存器 ==="
python3 framework/area.py out/sweeps/lab4_rob/p00* --csv 2>/dev/null | head -20

echo
echo "=== D) 实验二：L2 容量 ==="
python3 framework/area.py out/sweeps/lab2_l2/p00* --csv

echo
echo "=== E) 实验五：自定义指令的几个版本 ==="
python3 framework/area.py out/sweeps/lab5b_qnn/p000 \
                         out/sweeps/lab5b_qnn_dotp8/p000 \
                         out/sweeps/lab5b_qnn_dotp8x2/p000 \
                         out/sweeps/lab5b_qnn_dotp8x4/p000 \
                         out/sweeps/lab5b_qnn_dotp8x4c/p000 --csv

echo
echo "=== F) 实验六：加速器 pe 扫描 ==="
python3 framework/area.py out/sweeps/lab6_where_pe/p0* --csv

echo
echo "=== G) 实验六：L2 容量（带加速器）==="
python3 framework/area.py out/sweeps/lab6_m5_l2size/p0* --csv

echo WEIGHDONE
